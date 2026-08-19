"""Locust 引擎（可选）：动态生成 locustfile 并以 headless 模式驱动。

设计取舍（方案 §2）：不把 Locust Web UI 嵌 iframe（无法与 TestHub 的项目隔离
与权限体系打通），而是复用其运行时作为「中大并发」场景的备选引擎。
Locust 非必装依赖，未安装时 /engines/status/ 会如实上报，前端置灰不可选。
"""
import csv
import importlib.metadata
import importlib.util
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import time

from .base import BaseEngine, EngineError
from .workspace import make_run_dir

LOCUSTFILE_TEMPLATE = '''"""由 TestHub 性能测试模块自动生成，请勿手工修改。"""
import json
import random

from locust import HttpUser, TaskSet, between, constant, task

SCENARIO = json.loads(r\'\'\'{scenario_json}\'\'\')
STEPS = [s for s in SCENARIO["steps"] if s.get("enabled", True)]
SETUP_STEPS = [s for s in STEPS if s.get("is_setup")]
MAIN_STEPS = [s for s in STEPS if not s.get("is_setup")]
VARIABLES = SCENARIO.get("variables") or []


def _render(text, ctx):
    if not isinstance(text, str):
        return text
    for key, value in ctx.items():
        text = text.replace("{{{{" + key + "}}}}", str(value))
    # 兼容从接口测试导入时出现的 /{{baseUrl}}/login → /http://host/login 数据错误
    stripped = text.lstrip('/')
    if stripped.startswith(('http://', 'https://')):
        return stripped
    return text


FILE_CACHE = {{}}


def _read_file_cached(path):
    """上传文件字节缓存：压测下避免每次迭代重读磁盘。"""
    data = FILE_CACHE.get(path)
    if data is None:
        with open(path, 'rb') as fh:
            data = fh.read()
        FILE_CACHE[path] = data
    return data


def _parse_form_body(body):
    """FORM body 文本 → dict（兼容 JSON 对象与 k=v&k=v 两种历史格式）。"""
    if not body.strip():
        return {{}}
    try:
        parsed = json.loads(body)
        if isinstance(parsed, dict):
            return parsed
    except ValueError:
        pass
    return dict(p.split('=', 1) for p in body.split('&') if '=' in p)


class ScenarioTasks(TaskSet):
    def on_start(self):
        self.ctx = {{}}
        for v in VARIABLES:
            self.ctx[(v or {{}}).get('name', '')] = (v or {{}}).get('value', '')
        for step in SETUP_STEPS:
            self._call(step, catch=True)

    @task
    def run_scenario(self):
        for step in MAIN_STEPS:
            self._call(step)

    def _call(self, step, catch=False):
        method = (step.get("method") or "GET").upper()
        url = _render(step.get("url") or "", self.ctx)
        headers = {{k: _render(v, self.ctx) for k, v in (step.get("headers") or {{}}).items()}}
        kwargs = {{"headers": headers, "name": step.get("name") or url, "catch_response": True}}
        body = _render(step.get("body") or "", self.ctx)
        body_type = (step.get("body_type") or "NONE").upper()
        step_files = step.get("files") or []
        if body_type == "FORM" and step_files:
            # multipart/form-data：文本字段 + 文件字段（requests 在 data+files
            # 同时存在时自动 multipart 编码），文件字节带缓存复用
            kwargs["data"] = {{k: _render(str(v), self.ctx)
                               for k, v in _parse_form_body(body).items()}}
            files = []
            for f in step_files:
                try:
                    files.append((f.get("field") or "file",
                                  (f.get("filename") or "file",
                                   _read_file_cached(f.get("path")),
                                   f.get("content_type") or "application/octet-stream")))
                except (OSError, TypeError):
                    continue
            kwargs["files"] = files
        elif body_type == "JSON" and body.strip():
            try:
                kwargs["json"] = json.loads(body)
            except ValueError:
                kwargs["data"] = body
        elif body_type in ("FORM", "RAW", "XML") and body.strip():
            kwargs["data"] = body
        with self.client.request(method, url, **kwargs) as response:
            if response.status_code and 200 <= response.status_code < 400:
                response.success()
            else:
                response.failure(f"HTTP {{response.status_code}}")


class ScenarioUser(HttpUser):
    tasks = [ScenarioTasks]
    host = SCENARIO.get("env_config", {{}}).get("base_url") or "http://localhost"
    wait_time = constant(0)
'''


def is_available():
    """检测 locust 是否已安装。

    注意：绝不能在这里 `import locust` —— locust 在包导入时就会执行 gevent 的
    monkey.patch_all()，若在 Django/Web 进程（任意工作线程）里被触发，会破坏
    Django 的线程级数据库连接模型，导致后续所有请求 500
    （DatabaseWrapper objects created in a thread can only be used in that same thread）。
    改用 importlib.util.find_spec 做“是否可导入”探测，它不会执行 locust 的 __init__，
    因此不会触发 monkey-patch。
    """
    try:
        return importlib.util.find_spec('locust') is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def get_version():
    """读取 locust 已安装版本；同样不 import locust 本体，避免 monkey-patch。"""
    try:
        return importlib.metadata.version('locust')
    except Exception:  # noqa: BLE001
        return ''


def _open_csv_text(path):
    """以兼容编码打开 Locust 产出的 CSV 文件，返回可读取的文本对象。

    Locust 在中文 Windows 默认以系统 ANSI 编码（CP936/GBK）写出 CSV，
    直接按 UTF-8 读取会触发 UnicodeDecodeError。此处先尝试 UTF-8（含 BOM），
    再回退中文常见编码，最后以 latin1+replace 兜底，确保 collect 阶段不因
    编码问题崩溃。
    """
    with open(path, 'rb') as fh:
        raw = fh.read()
    for enc in ('utf-8-sig', 'utf-8', 'gb18030', 'gbk', 'cp936'):
        try:
            return io.StringIO(raw.decode(enc))
        except UnicodeDecodeError:
            continue
    return io.StringIO(raw.decode('latin1', errors='replace'))


class LocustEngine(BaseEngine):
    """通过 subprocess 调用 locust --headless 的引擎。"""

    name = 'LOCUST'

    def __init__(self, snapshot, on_sample=None, on_log=None, raw_csv_path=None,
                 work_dir=None):
        """raw_csv_path 是平台驱动层统一传入的（内置引擎写原始明细 CSV 用），
        Locust 不消费它，但必须接受以兼容 run_execution 的统一实例化签名，
        否则执行 Locust 时会 TypeError 崩溃。

        work_dir 默认落到项目内的 perf_workspace（F 盘），避免多并发执行写入同名
        locust_stats.csv 互相覆盖，也严禁落到系统 TMP（C 盘）。
        """
        super().__init__(snapshot, on_sample, on_log)
        self.raw_csv_path = raw_csv_path
        self.work_dir = work_dir or make_run_dir('locust')
        self.load_config = snapshot.get('load_config') or {}
        self.base_url = (snapshot.get('env_config') or {}).get('base_url') or ''
        self.locustfile = os.path.join(self.work_dir, 'locustfile.py')
        self.csv_prefix = os.path.join(self.work_dir, 'locust')
        self.process = None
        self._start_ts = None
        self._stop_reason = ''
        # 采样状态（与 JMeterEngine 对齐，在 __init__ 初始化确保 _try_emit_sample 可独立调用）
        self._sample_interval = 3.0
        self._last_emit_ts = 0.0
        self._global_total = 0
        self._history_seen = 0

    def prepare(self):
        if not is_available():
            raise EngineError('未安装 locust，无法使用该引擎。请执行 pip install locust 或改用内置引擎')
        steps = [s for s in (self.snapshot.get('steps') or [])
                 if s.get('enabled', True) and not s.get('is_setup')]
        if not steps:
            raise EngineError('场景没有可执行的业务步骤')
        base_url = (self.snapshot.get('env_config') or {}).get('base_url')
        self.base_url = base_url
        # 仅当存在相对路径步骤时才要求 base_url；步骤均为绝对 http(s):// URL 时无需配置
        # （与 preflight / 内置引擎保持一致，Locust 对绝对 URL 会直连而忽略 host）
        if not base_url:
            for step in steps:
                url = (step.get('url') or '').strip()
                if url and not url.startswith(('http://', 'https://')):
                    raise EngineError(
                        f'步骤「{step.get("name")}」使用相对路径，但未配置环境基址 base_url')

        os.makedirs(self.work_dir, exist_ok=True)
        variables = list(self.snapshot.get('variables') or [])
        # 兼容从接口测试导入的 {{baseUrl}}：若用户未显式定义 baseUrl 变量，自动注入
        if base_url and not any((v or {}).get('name') == 'baseUrl' for v in variables):
            variables.append({'name': 'baseUrl', 'type': 'CONSTANT', 'value': base_url})
        payload = json.dumps({
            'steps': self.snapshot.get('steps') or [],
            'env_config': self.snapshot.get('env_config') or {},
            'variables': variables,
        }, ensure_ascii=False)
        with open(self.locustfile, 'w', encoding='utf-8') as fh:
            fh.write(LOCUSTFILE_TEMPLATE.format(scenario_json=payload))
        self.log(f'已生成 locustfile：{self.locustfile}')

    def run(self):
        load = self.load_config
        users = max(int(load.get('concurrency') or 10), 1)
        spawn_rate = users / max(float(load.get('ramp_up') or 1), 1)
        duration = int(load.get('duration') or 60)

        cmd = [
            sys.executable, '-m', 'locust',
            '-f', self.locustfile,
            '--headless',
            '-u', str(users),
            '-r', str(max(round(spawn_rate, 2), 0.1)),
            '-t', f'{duration}s',
            '--csv', self.csv_prefix,
        ]
        # host 仅在配置了环境基址时传入；步骤全部为绝对 URL 时 Locust 会直连目标，无需 host
        if self.base_url:
            cmd.extend(['--host', self.base_url])
        self.log(f'启动 Locust：{" ".join(cmd)}')
        self._start_ts = time.time()
        self._last_emit_ts = 0.0  # 重置节流计时器
        self._history_seen = 0     # 重置增量读取游标

        # 强制 UTF-8 模式，避免中文 Windows 上 Locust 以 CP936 写出 CSV，
        # 导致后续 collect 读取时解码失败。
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'

        self.process = subprocess.Popen(
            cmd, cwd=self.work_dir,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace',
            env=env,
        )
        try:
            while not self._stopping:
                line = self.process.stdout.readline()
                if not line:  # EOF / 进程退出
                    break
                line = line.rstrip()
                if line:
                    self.log(line[:500])
                # 尝试从 stats_history.csv 读取并发射采样点
                self._try_emit_sample()
                if self.process.poll() is not None:
                    break
        finally:
            # 收尾：确保最后一批数据被采集
            self._try_emit_sample()
            if self.process.poll() is None:
                try:
                    self.process.send_signal(signal.SIGTERM)
                    self.process.wait(timeout=10)
                except (subprocess.TimeoutExpired, OSError):
                    try:
                        self.process.kill()
                        self.process.wait(timeout=5)
                    except (subprocess.TimeoutExpired, OSError):
                        pass
            else:
                self.process.wait()
            self._duration = time.time() - self._start_ts if self._start_ts else 0.0

    def _try_emit_sample(self):
        """尝试从 Locust 的 stats_history.csv 读取增量聚合行并回调 on_sample。

        Locust 在 --csv 模式下会周期性写入 {prefix}_stats_history.csv，
        其中包含各请求类型的时序统计 + 一行「Aggregated」汇总。
        本方法增量读取该文件，取 Aggregated 行构造 sample 回调。
        """
        now = time.time()
        if now - self._last_emit_ts < self._sample_interval:
            return

        history_file = f'{self.csv_prefix}_stats_history.csv'
        if not os.path.exists(history_file):
            return

        try:
            fh = _open_csv_text(history_file)
            reader = csv.DictReader(fh)
            rows = list(reader)
        except (OSError, csv.Error):
            return

        new_rows = rows[self._history_seen:]
        if not new_rows:
            return

        self._history_seen = len(rows)

        # 在新增行中找 Aggregated 汇总行（最新的那一行）
        agg = None
        for r in new_rows:
            if (r.get('Name') or '').strip() == 'Aggregated':
                agg = r

        if not agg:
            return

        total = int(_f(agg, 'Request Count', default=0))
        failed = int(_f(agg, 'Failure Count', default=0))
        self._global_total = total

        sample = {
            'ts_offset': int(now - self._start_ts) if self._start_ts else 0,
            'active_users': int(self.load_config.get('concurrency') or 0),
            'tps': round(_f(agg, 'Requests/s'), 2),
            'avg_rt': round(_f(agg, 'Average Response Time'), 2),
            'p90_rt': round(_f(agg, '90%'), 2),
            'p95_rt': round(_f(agg, '95%'), 2),
            'p99_rt': round(_f(agg, '99%'), 2),
            'error_rate': round(failed / total * 100, 2) if total else 0.0,
            'total_requests': total,
            'cpu_percent': 0.0,
            'memory_mb': 0.0,
        }
        self.on_sample(sample)
        self._last_emit_ts = now

    def stop(self, graceful=True):
        self._stopping = True
        self._stop_reason = '收到停止指令'
        if self.process and self.process.poll() is None:
            try:
                self.process.send_signal(signal.SIGTERM if graceful else signal.SIGKILL)
            except Exception:  # noqa: BLE001
                pass

    def collect(self):
        duration = getattr(self, '_duration', None) or (time.time() - self._start_ts if self._start_ts else 0)
        stats_file = f'{self.csv_prefix}_stats.csv'
        history_file = f'{self.csv_prefix}_stats_history.csv'
        summary = {}
        request_stats = []
        samples = []

        if os.path.exists(stats_file):
            fh = _open_csv_text(stats_file)
            for row in csv.DictReader(fh):
                entry = _parse_locust_row(row, duration)
                if (row.get('Name') or '').strip() == 'Aggregated':
                    summary = _row_to_summary(entry, duration)
                else:
                    request_stats.append(entry)

        # 从 stats_history.csv 回填时序采样点（用于报告曲线）
        if os.path.exists(history_file):
            try:
                fh = _open_csv_text(history_file)
                for row in csv.DictReader(fh):
                    if (row.get('Name') or '').strip() == 'Aggregated':
                        total = int(_f(row, 'Request Count', default=0))
                        failed = int(_f(row, 'Failure Count', default=0))
                        samples.append({
                                'ts_offset': int(_f(row, 'Timestamp', default=0)),
                                'active_users': int(_f(row, 'User Count', default=self.load_config.get('concurrency') or 0)),
                                'tps': round(_f(row, 'Requests/s'), 2),
                                'avg_rt': round(_f(row, 'Average Response Time'), 2),
                                'p90_rt': round(_f(row, '90%'), 2),
                                'p95_rt': round(_f(row, '95%'), 2),
                                'p99_rt': round(_f(row, '99%'), 2),
                                'error_rate': round(failed / total * 100, 2) if total else 0.0,
                                'total_requests': total,
                                'cpu_percent': 0.0,
                                'memory_mb': 0.0,
                            })
            except (OSError, csv.Error):
                pass

        if not summary:
            summary = {
                'total_requests': 0, 'success_requests': 0, 'failed_requests': 0,
                'error_rate': 0, 'tps': 0, 'peak_tps': 0, 'avg_rt': 0,
                'min_rt': 0, 'max_rt': 0, 'p50_rt': 0, 'p90_rt': 0,
                'p95_rt': 0, 'p99_rt': 0, 'sent_bytes': 0, 'recv_bytes': 0,
                'max_concurrency': int(self.load_config.get('concurrency') or 0),
                'error_top': [],
            }

        # 错误分析：Locust --csv 模式会产出 {prefix}_exceptions.csv
        # （列：Count,Message,Traceback,Nodes），此前未采集导致报告
        # 「错误分析/错误 TOP」永远为空。取首行非空信息作为错误类型。
        exceptions_file = f'{self.csv_prefix}_exceptions.csv'
        if os.path.exists(exceptions_file):
            try:
                error_top = []
                fh = _open_csv_text(exceptions_file)
                for row in csv.DictReader(fh):
                    message = (row.get('Message') or '').strip()
                    if not message:
                        continue
                    count = int(_f(row, 'Count', default=0))
                    first_line = message.splitlines()[0][:120]
                    # 取异常类名（如 "ConnectionError(..." -> ConnectionError）
                    etype = first_line.split('(')[0].split(':')[0].strip()
                    error_top.append({
                        'type': (etype or 'Exception')[:60],
                        'count': count,
                        'sample_step': (row.get('Nodes') or '').strip()[:100],
                        'message': message[:300],
                    })
                error_top.sort(key=lambda x: -x['count'])
                summary['error_top'] = error_top[:10]
            except (OSError, csv.Error, ValueError):
                pass

        return {
            'summary': summary,
            'request_stats': request_stats,
            'samples': samples,
            'duration': round(duration, 2),
            'stop_reason': self._stop_reason,
            'raw_rows': 0,
        }


def _f(row, *keys, default=0.0):
    for key in keys:
        if key in row and row[key] not in (None, ''):
            try:
                return float(row[key])
            except (TypeError, ValueError):
                continue
    return default


def _parse_locust_row(row, duration):
    total = int(_f(row, 'Request Count', default=0))
    failed = int(_f(row, 'Failure Count', default=0))
    return {
        'step_name': (row.get('Name') or '').strip()[:200],
        'method': (row.get('Type') or row.get('Method') or '').strip()[:10],
        'url': (row.get('Name') or '').strip()[:1000],
        'total': total,
        'success': max(total - failed, 0),
        'failed': failed,
        'error_rate': round(failed / total * 100, 2) if total else 0.0,
        'tps': round(_f(row, 'Requests/s'), 2) or (round(total / duration, 2) if duration else 0.0),
        'avg_rt': round(_f(row, 'Average Response Time'), 2),
        'min_rt': round(_f(row, 'Min Response Time'), 2),
        'max_rt': round(_f(row, 'Max Response Time'), 2),
        'p50_rt': round(_f(row, '50%'), 2),
        'p90_rt': round(_f(row, '90%'), 2),
        'p95_rt': round(_f(row, '95%'), 2),
        'p99_rt': round(_f(row, '99%'), 2),
        'sent_bytes': 0,
        'recv_bytes': int(_f(row, 'Total Content Size', default=0)),
        'error_detail': [],
    }


def _row_to_summary(entry, duration):
    return {
        'total_requests': entry['total'],
        'success_requests': entry['success'],
        'failed_requests': entry['failed'],
        'error_rate': entry['error_rate'],
        'tps': entry['tps'],
        'peak_tps': entry['tps'],
        'avg_rt': entry['avg_rt'],
        'min_rt': entry['min_rt'],
        'max_rt': entry['max_rt'],
        'p50_rt': entry['p50_rt'],
        'p90_rt': entry['p90_rt'],
        'p95_rt': entry['p95_rt'],
        'p99_rt': entry['p99_rt'],
        'sent_bytes': entry['sent_bytes'],
        'recv_bytes': entry['recv_bytes'],
        'max_concurrency': 0,
        'error_top': [],
    }

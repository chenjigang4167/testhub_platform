# -*- coding: utf-8 -*-
"""
压测验收目标评估（perf_targets evaluation）。

与 SLA 评估的区别：
- SLA 评估（sla.py）：基于 sla_config 阈值，判定执行过程中是否"违规"（实时熔断）
- 验收目标评估（本模块）：基于 perf_targets，判定执行结果是否"通过"（事后判定）

评估维度：
- max_p95_rt：P95 响应时间上限（ms），任一步骤 P95 超过即 FAILED
- max_avg_rt：平均响应时间上限（ms），任一步骤 avg 超过即 FAILED
- min_tps：整体 TPS 下限，低于即 FAILED
- max_error_rate：错误率上限（%），任一步骤错误率超过即 FAILED
"""

from typing import Dict, List, Tuple

NOT_EVALUATED = 'NOT_EVALUATED'
PASSED = 'PASSED'
FAILED = 'FAILED'


def _pick(container: Dict, *names, default=0):
    """按候选键名依次取值，取第一个非 None 的。

    存在原因：request_stats 由 metrics.to_stat() 产出，键名是 avg_rt / p95_rt；
    而旧版与单测用的是 avg_response_time / p95。只认一套会让取值为空，
    再被 ``or 0`` 兜底成 0，导致「实际值恒小于阈值 → 恒 PASS」的假达标。
    """
    for name in names:
        value = container.get(name)
        if value is not None:
            return value
    return default


def evaluate_targets(perf_targets: Dict, stats: List[Dict], summary: Dict) -> Tuple[str, List[Dict]]:
    """
    评估验收目标。

    :param perf_targets: 场景的 perf_targets 字段，如
        {"max_p95_rt": 2000, "max_avg_rt": 1000, "min_tps": 100, "max_error_rate": 1.0}
    :param stats: request_stats 列表（由 metrics.to_stat 产出），每个元素含
        step_name, avg_rt, p95_rt, error_rate 等；旧键名 avg_response_time / p95 亦兼容
    :param summary: 执行汇总，含 tps, error_rate 等
    :return: (verdict, details)
        verdict: 'PASSED' | 'FAILED' | 'NOT_EVALUATED'
        details: [{"step": str, "metric": str, "target": num, "actual": num, "result": "PASS/FAIL"}]
    """
    if not perf_targets:
        return NOT_EVALUATED, []

    details = []
    has_fail = False

    # --- 逐步骤检查 ---
    max_p95 = perf_targets.get('max_p95_rt')
    max_avg = perf_targets.get('max_avg_rt')
    max_err = perf_targets.get('max_error_rate')

    for s in stats:
        step_name = s.get('step_name', s.get('name', '未知'))

        if max_p95 is not None:
            actual = _pick(s, 'p95_rt', 'p95')
            ok = actual <= max_p95
            if not ok:
                has_fail = True
            details.append({
                'step': step_name, 'metric': 'P95响应时间',
                'target': max_p95, 'actual': actual, 'unit': 'ms',
                'result': 'FAIL' if not ok else 'PASS'
            })

        if max_avg is not None:
            actual = _pick(s, 'avg_rt', 'avg_response_time')
            ok = actual <= max_avg
            if not ok:
                has_fail = True
            details.append({
                'step': step_name, 'metric': '平均响应时间',
                'target': max_avg, 'actual': actual, 'unit': 'ms',
                'result': 'FAIL' if not ok else 'PASS'
            })

        if max_err is not None:
            actual = _pick(s, 'error_rate')
            ok = actual <= max_err
            if not ok:
                has_fail = True
            details.append({
                'step': step_name, 'metric': '错误率',
                'target': max_err, 'actual': actual, 'unit': '%',
                'result': 'FAIL' if not ok else 'PASS'
            })

    # --- 整体 TPS 检查 ---
    min_tps = perf_targets.get('min_tps')
    if min_tps is not None:
        actual = _pick(summary, 'tps')
        ok = actual >= min_tps
        if not ok:
            has_fail = True
        details.append({
            'step': '(整体)', 'metric': 'TPS',
            'target': min_tps, 'actual': actual, 'unit': 'req/s',
            'result': 'FAIL' if not ok else 'PASS'
        })

    verdict = FAILED if has_fail else PASSED
    return verdict, details

import json
import time
from django.utils import timezone
from .models import RequestHistory
from .variable_resolver import VariableResolver


def _iter_sse_events(text):
    """按 SSE 协议切分报文，产出 (事件名, data 内容)"""
    event_name = None
    buf = []
    for line in (text or "").splitlines():
        if not line.strip():
            if event_name or buf:
                yield event_name, "\n".join(buf)
            event_name, buf = None, []
            continue
        if line.startswith("event:"):
            event_name = line[6:].strip()
        elif line.startswith("data:"):
            buf.append(line[5:].strip())
    if event_name or buf:
        yield event_name, "\n".join(buf)


def _parse_sse_body(text):
    """解析 SSE 报文，返回第一个带 error 字段的业务对象；没有则退回首个可解析对象"""
    fallback = None
    for _name, payload in _iter_sse_events(text):
        try:
            obj = json.loads(payload)
        except Exception:
            continue
        if isinstance(obj, dict) and "error" in obj:
            return obj
        if fallback is None:
            obj_any = obj
            fallback = obj_any
    return fallback


def parse_response_body(response):
    """统一解析响应体：SSE 走事件解析，其余优先 JSON，都失败返回文本"""
    content_type = (response.headers.get("content-type") or "").lower()
    if "text/event-stream" in content_type:
        parsed = _parse_sse_body(response.text or "")
        return parsed if parsed is not None else (response.text or "")
    try:
        return json.loads(response.text)
    except Exception:
        return response.text


def _json_query(data, path):
    """按 JSONPath 取值：单命中返回值，多命中返回列表，无命中返回 None"""
    from jsonpath_ng import parse as jsonpath_parse

    matches = jsonpath_parse(path).find(data)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].value
    return [m.value for m in matches]


def apply_extract_rules(api_request, response, runtime_vars):
    """按请求上配置的 extract_rules 从响应中提取变量，写入套件级 runtime_vars

    规则结构（列表）：
        {"name": "变量名", "source": "body|cookies|headers|status_code",
         "path": "data.article.logId", "default": "兜底值", "join": ","}

    - 路径解析出多个值时，配置了 join 就拼接成字符串，否则取第一个
    - 取不到值且配置了 default 时使用 default，否则记为失败但不抛异常
    """
    rules = getattr(api_request, "extract_rules", None) or []
    if not rules:
        return []

    body_cache = {}
    results = []
    for rule in rules:
        name = str(rule.get("name") or "").strip()
        if not name:
            continue
        source = str(rule.get("source") or "body").strip().lower()
        path = str(rule.get("path") or "").strip()
        value = None
        error = ""
        try:
            if source == "body":
                if "v" not in body_cache:
                    body_cache["v"] = parse_response_body(response)
                parsed = body_cache["v"]
                if isinstance(parsed, str):
                    raise ValueError("响应不是 JSON/SSE，无法按 body 提取")
                value = _json_query(parsed, path) if path else parsed
            elif source == "cookies":
                value = response.cookies.get(path) if path else dict(response.cookies)
            elif source == "headers":
                value = response.headers.get(path)
            elif source == "status_code":
                value = response.status_code
            else:
                error = "不支持的 source: %s" % source
        except Exception as exc:
            error = "%s: %s" % (type(exc).__name__, exc)

        # 空字符串等价于「没配」：前端保存时已剔除，但 Admin / 老数据可能带空串，
        # 若当成有效配置会出现「提取失败却显示成功（值为空串）」「多值被空串拼接」的误判
        join_with = rule.get("join")
        if join_with is not None and str(join_with) == "":
            join_with = None
        default_value = rule.get("default")
        if default_value is not None and str(default_value) == "":
            default_value = None

        # 多值结果处理：配置了 join 就统一拼成字符串（单命中也要拼），否则取第一个
        if join_with is not None:
            if isinstance(value, list):
                value = str(join_with).join(str(v) for v in value)
            elif value is not None:
                value = str(value)
        elif isinstance(value, list):
            value = value[0] if value else None

        if value is None or value == "":
            if default_value is not None:
                value = default_value
                error = ""
            else:
                results.append({"name": name, "success": False, "value": None,
                                "error": error or "未取到值"})
                continue

        runtime_vars[name] = value
        results.append({"name": name, "success": True, "value": value, "error": error})
    return results


def execute_assertions(response, assertions):
    """执行断言验证"""
    results = []
    
    for assertion in assertions:
        result = {
            'name': assertion.get('name', '未命名断言'),
            'type': assertion.get('type'),
            'passed': False,
            'expected': assertion.get('expected'),
            'actual': None,
            'error': None
        }
        
        try:
            assertion_type = assertion.get('type')
            expected = assertion.get('expected')
            actual = None
            passed = False
            
            if assertion_type == 'status_code':
                actual = response.status_code
                passed = actual == expected
                
            elif assertion_type == 'response_time':
                # 响应时间断言在调用方处理
                actual = assertion.get('actual_time')
                passed = actual <= expected if actual else False
                
            elif assertion_type == 'contains':
                text = response.text or ''
                pattern = str(expected)
                actual = text[:200] + '...' if len(text) > 200 else text
                passed = pattern in str(text)
                
            elif assertion_type == 'json_path':
                json_path = assertion.get('json_path', '')
                expected_value = assertion.get('expected')
                actual = None
                passed = False
                
                try:
                    # 统一解析响应体：JSON / SSE / 文本 都能拿到业务对象
                    response_json = parse_response_body(response)
                    if isinstance(response_json, str):
                        content_type = response.headers.get('content-type', '')
                        raise ValueError(f"响应既不是 JSON 也不是可解析的 SSE 报文，Content-Type: {content_type}")
                    
                    # 检查JSONPath表达式是否为空
                    if not json_path:
                        raise ValueError("JSON路径表达式不能为空")
                    
                    from jsonpath_ng import parse
                    matches = parse(json_path).find(response_json)
                    actual = matches[0].value if matches else None
                    passed = str(actual) == str(expected_value)
                    
                    # 确保actual值被正确设置到result中
                    result['actual'] = actual
                except json.JSONDecodeError as e:
                    actual = None
                    passed = False
                    result['error'] = f"JSON解析失败: {str(e)}"
                    result['actual'] = actual
                except ImportError as e:
                    actual = None
                    passed = False
                    result['error'] = f"缺少依赖库: {str(e)}，请安装jsonpath-ng"
                    result['actual'] = actual
                except Exception as e:
                    actual = None
                    passed = False
                    result['error'] = f"执行错误: {str(e)}"
                    result['actual'] = actual
                    
            elif assertion_type == 'sse_event':
                # SSE 事件断言：指定事件（留空=任意带 data 的事件）至少出现 min_count 次
                event_name = str(assertion.get('event') or '').strip()
                try:
                    min_count = int(assertion.get('min_count') or 1)
                    if min_count < 1:
                        min_count = 1
                except (TypeError, ValueError):
                    min_count = 1
                events = list(_iter_sse_events(response.text or ''))
                if event_name:
                    actual = sum(1 for _n, _p in events if (_n or '').strip() == event_name)
                else:
                    actual = sum(1 for _n, _p in events if _p)
                passed = actual >= min_count
                result['expected'] = min_count
                result['actual'] = actual
                if not events and 'text/event-stream' not in (
                    response.headers.get('content-type') or ''
                ).lower():
                    result['error'] = '响应不是 SSE 报文，Content-Type: %s' % (
                        response.headers.get('content-type'))
                elif not events:
                    result['error'] = 'SSE 流中未解析到任何事件（响应体为空或格式异常）'

            elif assertion_type == 'sse_path':
                # SSE 路径断言：在事件 data 上执行 JSONPath，任一命中值等于期望即通过；
                # 期望留空时只校验「能取到值」，用于断言字段存在
                event_name = str(assertion.get('event') or '').strip()
                json_path = str(assertion.get('json_path') or '').strip()
                if not json_path:
                    raise ValueError("JSON路径表达式不能为空")

                from jsonpath_ng import parse as _jp_parse
                values = []
                event_total = 0
                for _n, _p in _iter_sse_events(response.text or ''):
                    if not _p:
                        continue
                    event_total += 1
                    if event_name and (_n or '').strip() != event_name:
                        continue
                    try:
                        _obj = json.loads(_p)
                    except Exception:
                        continue
                    for _m in _jp_parse(json_path).find(_obj):
                        values.append(_m.value)

                actual = values[0] if len(values) == 1 else (values or None)
                if expected is None or str(expected) == '':
                    passed = bool(values)
                else:
                    passed = any(str(_v) == str(expected) for _v in values)
                result['actual'] = actual
                if not event_total and 'text/event-stream' not in (
                    response.headers.get('content-type') or ''
                ).lower():
                    result['error'] = '响应不是 SSE 报文，Content-Type: %s' % (
                        response.headers.get('content-type'))
                elif not values:
                    result['error'] = 'SSE 流中未匹配到该 JSONPath 的值'

            elif assertion_type == 'header':
                header_name = assertion.get('header_name', '')
                expected_value = assertion.get('expected_value')
                actual = response.headers.get(header_name)
                passed = actual == expected_value
                
            elif assertion_type == 'equals':
                actual = response.text.strip()
                passed = actual == str(expected).strip()
            
            # 确保在所有情况下都设置actual值
            if 'actual' not in result or result['actual'] is None:
                result['actual'] = actual
            result['passed'] = passed
            
        except Exception as e:
            result['error'] = str(e)
            result['passed'] = False
        
        results.append(result)
    
    return results


def describe_assertion_failure(assertion_result):
    """断言未通过时给出可读原因

    执行器主路径（断言条件不成立）不会写 error 字段，只有 JSON 解析异常等分支才赋值，
    所以上层直接取 error 会拿到 None，最终显示成「未命名断言 - None」。这里统一兜底。
    """
    if not isinstance(assertion_result, dict):
        return '断言不通过'

    error = assertion_result.get('error')
    if error:
        return str(error)[:120]

    expected = assertion_result.get('expected')
    actual = assertion_result.get('actual')
    if expected is not None or actual is not None:
        return ('期望 %s，实际 %s' % (expected, actual))[:120]

    return '断言不通过'


def execute_test_suite(test_suite, environment, executed_by):
    """执行测试套件并返回结果"""
    from .models import TestExecution, RequestHistory
    import requests
    import time
    
    try:
        # 创建变量解析器
        resolver = VariableResolver()
        
        # 创建执行记录
        execution = TestExecution.objects.create(
            test_suite=test_suite,
            status='RUNNING',
            start_time=timezone.now(),
            executed_by=executed_by
        )
        
        # 获取套件中的请求
        suite_requests = test_suite.testsuiterequest_set.filter(enabled=True).order_by('order')
        
        execution.total_requests = suite_requests.count()
        execution.save()
        
        results = []
        passed_count = 0
        failed_count = 0
        
        # 套件级运行时变量：由上游请求的 extract_rules 写入，供下游请求使用
        runtime_vars = {}
        
        # 执行每个请求
        for suite_request in suite_requests:
            api_request = suite_request.request
            
            try:
                # 解析环境变量；运行时变量优先级更高，可覆盖同名环境变量
                variables = {}
                if environment:
                    variables.update(environment.variables)
                variables.update(runtime_vars)
                
                # 替换URL中的变量（先解析动态函数，再替换环境变量）
                url = _replace_variables(api_request.url, variables)
                url = resolver.resolve(url)
                
                # 准备请求头
                headers = {}
                if isinstance(api_request.headers, list):
                    for header_item in api_request.headers:
                        if header_item.get('enabled', True) and header_item.get('key'):
                            key = header_item['key']
                            value = _replace_variables(str(header_item.get('value', '')), variables)
                            value = resolver.resolve(value)
                            headers[key] = value
                else:
                    headers = api_request.headers.copy()
                    for key, value in headers.items():
                        headers[key] = _replace_variables(str(value), variables)
                        headers[key] = resolver.resolve(headers[key])
                
                # 准备请求参数
                params = api_request.params.copy() if api_request.params else {}
                for key, value in params.items():
                    params[key] = _replace_variables(str(value), variables)
                    params[key] = resolver.resolve(params[key])
                
                # 准备请求体
                json_data = None
                form_data = None
                if api_request.body and api_request.method in ['POST', 'PUT', 'PATCH']:
                    body_type = api_request.body.get('type')
                    if body_type == 'json':
                        json_data = api_request.body.get('data', {})
                        json_data = _replace_variables_in_dict(json_data, variables)
                        json_data = _resolve_variables_in_dict(json_data, resolver)
                    elif body_type in ('form', 'form-data', 'x-www-form-urlencoded', 'data'):
                        form_data = api_request.body.get('data', {})
                        form_data = _replace_variables_in_dict(form_data, variables)
                        form_data = _resolve_variables_in_dict(form_data, resolver)
                body_data = json_data if json_data is not None else form_data
                
                # 执行请求
                start_time = time.time()
                response = requests.request(
                    method=api_request.method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    data=form_data,
                    timeout=30
                )
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # 执行断言验证
                assertions = api_request.assertions or []
                for assertion in assertions:
                    if assertion.get('type') == 'response_time':
                        assertion['actual_time'] = response_time
                
                assertions_results = execute_assertions(response, assertions)
                
                # 响应提取：把变量写入套件级 runtime_vars，供后续请求使用
                extract_results = apply_extract_rules(api_request, response, runtime_vars)
                
                # 检查所有断言是否通过
                passed = True
                error_message = ''
                
                # 检查套件请求的断言
                for assertion in suite_request.assertions:
                    if assertion.get('type') == 'status_code':
                        expected = assertion.get('value')
                        if response.status_code != expected:
                            passed = False
                            error_message = f'状态码断言失败: 期望 {expected}, 实际 {response.status_code}'
                            break
                
                # 检查接口自身的断言
                if passed and assertions_results:
                    for assertion_result in assertions_results:
                        if not assertion_result.get('passed', True):
                            passed = False
                            error_message = f"断言失败: {assertion_result.get('name') or '未命名断言'} - {describe_assertion_failure(assertion_result)}"
                            break
                
                if passed:
                    passed_count += 1
                else:
                    failed_count += 1
                
                results.append({
                    'name': api_request.name,
                    'method': api_request.method,
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'passed': passed,
                    'error': error_message,
                    'assertions_results': assertions_results,
                    'extract_results': extract_results
                })
                
                # 保存请求历史
                RequestHistory.objects.create(
                    request=api_request,
                    environment=environment,
                    request_data={
                        'url': url,
                        'method': api_request.method,
                        'headers': headers,
                        '极速版params': params,
                        'body': body_data
                    },
                    response_data={
                        'headers': dict(response.headers),
                        'body': response.text,
                        'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                    },
                    status_code=response.status_code,
                    response_time=response_time,
                    assertions_results=assertions_results,
                    extract_results=extract_results,
                    executed_by=executed_by
                )
                
            except Exception as e:
                failed_count += 1
                results.append({
                    'name': api_request.name,
                    'method': api_request.method,
                    'url': api_request.url,
                    'passed': False,
                    'error': str(e)
                })
        
        # 更新执行结果
        execution.end_time = timezone.now()
        execution.passed_requests = passed_count
        execution.failed_requests = failed_count
        execution.status = 'COMPLETED' if failed_count == 0 else 'FAILED'
        execution.results = results
        execution.save()
        
        return {
            'success': True,
            'execution_id': execution.id,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'total_count': execution.total_requests,
            'results': results
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def execute_api_request(api_request, environment, executed_by):
    """执行单个API请求并返回结果"""
    import requests
    import time
    
    try:
        # 创建变量解析器
        resolver = VariableResolver()
        
        # 解析环境变量
        variables = {}
        if environment:
            variables.update(environment.variables)
        
        # 替换URL中的变量（先解析动态函数，再替换环境变量）
        url = _replace_variables(api_request.url, variables)
        url = resolver.resolve(url)
        
        # 准备请求头
        headers = {}
        if isinstance(api_request.headers, list):
            for header_item in api_request.headers:
                if header_item.get('enabled', True) and header_item.get('key'):
                    key = header_item['key']
                    value = _replace_variables(str(header_item.get('value', '')), variables)
                    value = resolver.resolve(value)
                    headers[key] = value
        else:
            headers = api_request.headers.copy()
            for key, value in headers.items():
                headers[key] = _replace_variables(str(value), variables)
                headers[key] = resolver.resolve(headers[key])
        
        # 准备请求参数
        params = api_request.params.copy() if api_request.params else {}
        for key, value in params.items():
            params[key] = _replace_variables(str(value), variables)
            params[key] = resolver.resolve(params[key])
        
        # 准备请求体
        json_data = None
        form_data = None
        if api_request.body and api_request.method in ['POST', 'PUT', 'PATCH']:
            body_type = api_request.body.get('type')
            if body_type == 'json':
                json_data = api_request.body.get('data', {})
                json_data = _replace_variables_in_dict(json_data, variables)
                json_data = _resolve_variables_in_dict(json_data, resolver)
            elif body_type in ('form', 'form-data', 'x-www-form-urlencoded', 'data'):
                form_data = api_request.body.get('data', {})
                form_data = _replace_variables_in_dict(form_data, variables)
                form_data = _resolve_variables_in_dict(form_data, resolver)
        body_data = json_data if json_data is not None else form_data
        
        # 执行请求
        start_time = time.time()
        response = requests.request(
            method=api_request.method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=form_data,
            timeout=30
        )
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        # 执行断言验证
        assertions = api_request.assertions or []
        for assertion in assertions:
            if assertion.get('type') == 'response_time':
                assertion['actual_time'] = response_time
        
        assertions_results = execute_assertions(response, assertions)
        
        # 保存请求历史
        history = RequestHistory.objects.create(
            request=api_request,
            environment=environment,
            request_data={
                'url': url,
                'method': api_request.method,
                'headers': headers,
                'params': params,
                'body': body_data
            },
            response_data={
                'headers': dict(response.headers),
                'body': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            },
            status_code=response.status_code,
            response_time=response_time,
            assertions_results=assertions_results,
            executed_by=executed_by
        )
        
        return {
            'success': True,
            'history_id': history.id,
            'status_code': response.status_code,
            'response_time': response_time,
            'assertions_results': assertions_results,
            'response_data': {
                'headers': dict(response.headers),
                'body': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def _replace_variables(text, variables):
    """替换文本中的变量"""
    if not isinstance(text, str):
        return text
    
    result = text
    for key, value in (variables or {}).items():
        if isinstance(value, dict):
            replacement = str(value.get('currentValue', '') or value.get('initialValue', ''))
        else:
            replacement = str(value) if value is not None else ''
        result = result.replace(f'{{{{{key}}}}}', replacement)
    return result

def _replace_variables_in_dict(data, variables):
    """递归替换字典中的变量"""
    if isinstance(data, dict):
        return {k: _replace_variables_in_dict(v, variables) for k, v in data.items()}
    elif isinstance(data, list):
        return [_replace_variables_in_dict(item, variables) for item in data]
    elif isinstance(data, str):
        return _replace_variables(data, variables)
    else:
        return data

def _resolve_variables_in_dict(data, resolver):
    """递归解析字典中的动态函数占位符"""
    if isinstance(data, dict):
        return {k: _resolve_variables_in_dict(v, resolver) for k, v in data.items()}
    elif isinstance(data, list):
        return [_resolve_variables_in_dict(item, resolver) for item in data]
    elif isinstance(data, str):
        return resolver.resolve(data)
    else:
        return data

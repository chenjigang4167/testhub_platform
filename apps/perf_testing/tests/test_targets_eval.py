# -*- coding: utf-8 -*-
"""
验收目标评估纯函数单测（DB-free，绝对导入）。
运行: python manage.py test apps.perf_testing.tests.test_targets_eval
"""
import os
import sys
import unittest

# PROJECT_ROOT 入 sys.path（DB-free 单测规范）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from apps.perf_testing.services.targets_eval import evaluate_targets, PASSED, FAILED, NOT_EVALUATED


class TestEvaluateTargets(unittest.TestCase):

    def test_no_targets_returns_not_evaluated(self):
        """未设验收目标 → NOT_EVALUATED"""
        verdict, details = evaluate_targets({}, [{'step_name': 'A', 'p95': 999}], {'tps': 10})
        self.assertEqual(verdict, NOT_EVALUATED)
        self.assertEqual(details, [])

    def test_all_pass(self):
        """全部达标 → PASSED"""
        targets = {'max_p95_rt': 2000, 'min_tps': 100, 'max_error_rate': 1.0}
        stats = [{'step_name': '登录', 'p95': 500, 'error_rate': 0.1}]
        summary = {'tps': 150}
        verdict, details = evaluate_targets(targets, stats, summary)
        self.assertEqual(verdict, PASSED)
        self.assertEqual(len(details), 3)  # p95 + error_rate + tps
        for d in details:
            self.assertEqual(d['result'], 'PASS')

    def test_p95_fail(self):
        """P95 超标 → FAILED"""
        targets = {'max_p95_rt': 1000}
        stats = [{'step_name': '查询', 'p95': 1500, 'error_rate': 0}]
        verdict, details = evaluate_targets(targets, stats, {'tps': 100})
        self.assertEqual(verdict, FAILED)
        self.assertEqual(details[0]['result'], 'FAIL')
        self.assertEqual(details[0]['actual'], 1500)

    def test_tps_fail(self):
        """TPS 不达标 → FAILED"""
        targets = {'min_tps': 200}
        stats = [{'step_name': 'A', 'p95': 100}]
        verdict, details = evaluate_targets(targets, stats, {'tps': 50})
        self.assertEqual(verdict, FAILED)
        # 最后一条是 TPS 检查
        self.assertEqual(details[-1]['metric'], 'TPS')
        self.assertEqual(details[-1]['result'], 'FAIL')

    def test_multiple_steps_mixed(self):
        """多步骤部分达标部分不达标 → FAILED"""
        targets = {'max_p95_rt': 1000, 'max_error_rate': 0.5}
        stats = [
            {'step_name': 'A', 'p95': 800, 'error_rate': 0.1},
            {'step_name': 'B', 'p95': 1200, 'error_rate': 0.3},  # P95 超标
        ]
        verdict, details = evaluate_targets(targets, stats, {'tps': 100})
        self.assertEqual(verdict, FAILED)
        # B 的 P95 应该 FAIL
        b_p95 = [d for d in details if d['step'] == 'B' and d['metric'] == 'P95响应时间'][0]
        self.assertEqual(b_p95['result'], 'FAIL')

    def test_empty_stats_with_targets(self):
        """有目标但无步骤数据 → PASSED（无步骤可判失败）"""
        targets = {'max_p95_rt': 1000}
        verdict, details = evaluate_targets(targets, [], {'tps': 100})
        self.assertEqual(verdict, PASSED)
        self.assertEqual(len(details), 0)  # 无步骤检查 + 无 TPS 目标

    def test_real_request_stats_keys(self):
        """回归：metrics.to_stat() 产出的键名（p95_rt / avg_rt）必须能被判定。

        历史缺陷：评估器只认旧键 p95 / avg_response_time，取不到就 or 0，
        导致实际值恒为 0、恒小于阈值 → 验收恒 PASS。
        """
        targets = {'max_p95_rt': 2000, 'max_avg_rt': 1000}

        ok_stats = [{'step_name': '登录', 'avg_rt': 850, 'p95_rt': 1800, 'error_rate': 0.2}]
        self.assertEqual(evaluate_targets(targets, ok_stats, {'tps': 120})[0], PASSED)

        slow_p95 = [{'step_name': '登录', 'avg_rt': 850, 'p95_rt': 2600, 'error_rate': 0.2}]
        verdict, details = evaluate_targets(targets, slow_p95, {'tps': 120})
        self.assertEqual(verdict, FAILED)
        p95_row = [d for d in details if d['metric'] == 'P95响应时间'][0]
        self.assertEqual(p95_row['actual'], 2600)
        self.assertEqual(p95_row['result'], 'FAIL')

        slow_avg = [{'step_name': '登录', 'avg_rt': 1500, 'p95_rt': 1800, 'error_rate': 0.2}]
        self.assertEqual(evaluate_targets(targets, slow_avg, {'tps': 120})[0], FAILED)


if __name__ == '__main__':
    unittest.main()

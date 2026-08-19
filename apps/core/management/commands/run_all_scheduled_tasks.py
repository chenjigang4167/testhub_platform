from django.core.management.base import BaseCommand
from django.utils import timezone
import time
import logging
import sys

# 避免长循环中的数据库连接超时
from django.db import close_old_connections

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '运行所有模块的定时任务调度器（API测试 + UI自动化 + APP自动化 + 性能测试）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='检查间隔（秒），默认60秒'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='只执行一次检查，不循环'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']

        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(self.style.SUCCESS("启动统一定时任务调度器"))
        self.stdout.write(self.style.SUCCESS(f"检查间隔: {interval}秒"))
        self.stdout.write(self.style.SUCCESS(f"调度模块: API测试 + UI自动化 + APP自动化 + 性能测试"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))

        while True:
            # 每次循环前关闭旧连接，防止 MySQL 超时断开
            close_old_connections()
            try:
                # 统一使用本地时区，避免UTC导致调度延后8小时问题
                now = timezone.localtime(timezone.now())
                self.stdout.write(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] 开始检查任务...")

                # 调度 API 测试模块的定时任务
                api_count = self.schedule_api_tasks()

                # 调度 UI 自动化模块的定时任务
                ui_count = self.schedule_ui_tasks()

                # 调度 APP 自动化模块的定时任务
                app_count = self.schedule_app_tasks()

                # 调度性能测试模块的定时任务
                perf_count = self.schedule_perf_tasks()

                total_count = api_count + ui_count + app_count + perf_count
                if total_count > 0:
                    self.stdout.write(self.style.SUCCESS(f"✓ 本次调度执行了 {total_count} 个任务 (API: {api_count}, UI: {ui_count}, APP: {app_count}, 性能: {perf_count})"))
                else:
                    self.stdout.write("  没有需要执行的任务")

                if run_once:
                    self.stdout.write(self.style.WARNING("单次执行模式，调度器退出"))
                    break

                self.stdout.write(f"等待 {interval} 秒后进行下一次检查...")
                time.sleep(interval)

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\n\n调度器已停止"))
                break
            except Exception as e:
                logger.error(f"调度器运行出错: {e}", exc_info=True)
                self.stdout.write(self.style.ERROR(f"调度器运行出错: {e}"))
                if run_once:
                    break
                self.stdout.write(f"等待 {interval} 秒后重试...")
                time.sleep(interval)

    def schedule_api_tasks(self):
        """调度 API 测试模块的定时任务"""
        try:
            # 确保连接有效，简单地关闭旧连接让 Django 重连
            close_old_connections()
            from apps.api_testing.models import ScheduledTask
            from apps.api_testing.views import ScheduledTaskViewSet

            # 获取所有活跃的定时任务
            active_tasks = ScheduledTask.objects.filter(status='ACTIVE')
            executed_count = 0

            # 显示所有活跃任务的调试信息
            if active_tasks.exists():
                now = timezone.now()
                self.stdout.write(f"  [API] 活跃任务数: {active_tasks.count()}")
                for task in active_tasks:
                    if task.next_run_time:
                        time_diff = (task.next_run_time - now).total_seconds()
                        if time_diff > 0:
                            self.stdout.write(f"        - {task.name}: 距下次执行还有 {int(time_diff)} 秒")
                        else:
                            self.stdout.write(f"        - {task.name}: 应该立即执行！")
                    else:
                        self.stdout.write(f"        - {task.name}: 未设置下次执行时间")

            for task in active_tasks:
                if task.should_run_now():
                    self.stdout.write(f"  [API] 执行任务: {task.name}")
                    self.stdout.write(f"       类型: {task.get_task_type_display() if hasattr(task, 'get_task_type_display') else task.task_type}, 触发方式: {task.get_trigger_type_display() if hasattr(task, 'get_trigger_type_display') else task.trigger_type}")
                    try:
                        # 创建执行日志
                        from apps.api_testing.models import TaskExecutionLog
                        execution_log = TaskExecutionLog.objects.create(
                            task=task,
                            status='PENDING'
                        )

                        # 调用任务执行方法
                        view = ScheduledTaskViewSet()
                        view._execute_task_async(task, execution_log)

                        executed_count += 1
                        self.stdout.write(self.style.SUCCESS(f"    ✓ 任务 {task.name} 已启动"))

                    except Exception as e:
                        logger.error(f"执行API任务 {task.name} 时出错: {e}", exc_info=True)
                        self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 执行失败: {e}"))

            return executed_count

        except Exception as e:
            logger.error(f"调度API任务时出错: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"[API] 调度失败: {e}"))
            return 0

    def schedule_ui_tasks(self):
        """调度 UI 自动化模块的定时任务"""
        try:
            from apps.ui_automation.models import UiScheduledTask

            # 获取所有活跃的定时任务
            active_tasks = UiScheduledTask.objects.filter(status='ACTIVE')
            executed_count = 0

            # 显示所有活跃任务的调试信息
            if active_tasks.exists():
                now = timezone.now()
                self.stdout.write(f"  [UI]  活跃任务数: {active_tasks.count()}")
                for task in active_tasks:
                    if task.next_run_time:
                        time_diff = (task.next_run_time - now).total_seconds()
                        if time_diff > 0:
                            self.stdout.write(f"        - {task.name}: 距下次执行还有 {int(time_diff)} 秒")
                        else:
                            self.stdout.write(f"        - {task.name}: 应该立即执行！")
                    else:
                        self.stdout.write(f"        - {task.name}: 未设置下次执行时间")

            for task in active_tasks:
                if task.should_run_now():
                    self.stdout.write(f"  [UI]  执行任务: {task.name}")
                    self.stdout.write(f"       类型: {task.get_task_type_display()}, 触发方式: {task.get_trigger_type_display()}")
                    try:
                        # 更新任务执行时间和次数
                        task.last_run_time = timezone.now()
                        task.total_runs += 1
                        # 先保存，确保last_run_time被更新
                        task.save()

                        # 根据任务类型执行不同的逻辑
                        if task.task_type == 'TEST_SUITE':
                            # 执行测试套件
                            if not task.test_suite:
                                self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 未配置测试套件"))
                                # 即使失败也要重新计算下次运行时间
                                task.refresh_from_db()
                                task.next_run_time = task.calculate_next_run()
                                task.save()
                                continue

                            test_suite = task.test_suite
                            test_case_count = test_suite.suite_test_cases.count()

                            if test_case_count == 0:
                                self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 的测试套件没有用例"))
                                # 即使失败也要重新计算下次运行时间
                                task.refresh_from_db()
                                task.next_run_time = task.calculate_next_run()
                                task.save()
                                continue

                            # 更新套件执行状态
                            test_suite.execution_status = 'running'
                            test_suite.save()

                            # 在后台线程中执行测试
                            import threading
                            from apps.ui_automation.test_executor import TestExecutor

                            def run_test():
                                try:
                                    executor = TestExecutor(
                                        test_suite=test_suite,
                                        engine=task.engine,
                                        browser=task.browser,
                                        headless=task.headless,
                                        executed_by=task.created_by
                                    )
                                    executor.run()

                                    # 测试完成后，重新加载任务并更新结果和下次运行时间
                                    task.refresh_from_db()
                                    task.successful_runs += 1
                                    task.last_result = {
                                        'status': 'success',
                                        'test_case_count': test_case_count
                                    }
                                    # 重新计算下次运行时间
                                    task.next_run_time = task.calculate_next_run()
                                    task.save()

                                    logger.info(f"UI定时任务 {task.name} 执行成功")

                                    # 发送成功通知
                                    print("       === 开始检查发送成功通知 ===")
                                    notification_setting = None
                                    if hasattr(task, 'notification_settings'):
                                        try:
                                            notification_setting = task.notification_settings.first()
                                            print(f"       获取到通知设置: {notification_setting}")
                                            if notification_setting:
                                                print(f"       通知设置详情 - ID: {notification_setting.id}, 是否启用: {notification_setting.is_enabled}, 成功通知: {notification_setting.notify_on_success}")
                                            else:
                                                print("       没有找到通知设置")
                                        except Exception as e:
                                            print(f"       获取任务通知设置时出错: {e}", file=sys.stderr)
                                            import traceback
                                            traceback.print_exc()
                                    else:
                                        print("       任务没有notification_settings属性")

                                    if notification_setting and notification_setting.is_enabled:
                                        print("       通知设置已启用，准备发送成功通知")
                                        if notification_setting.notify_on_success:
                                            print("       调用 _send_task_notification 方法发送成功通知")
                                            try:
                                                from apps.ui_automation.views import UiScheduledTaskViewSet
                                                viewset = UiScheduledTaskViewSet()
                                                viewset._send_task_notification(task, success=True)
                                                print("       ✓ 成功通知已发送")
                                            except Exception as e:
                                                print(f"       ✗ 发送UI定时任务 {task.name} 成功通知失败: {e}", file=sys.stderr)
                                        else:
                                            print("       通知设置中未启用成功通知")
                                    else:
                                        print("       通知设置未启用或不存在，跳过成功通知")
                                    print("       === 结束检查发送成功通知 ===")

                                except Exception as e:
                                    logger.error(f"UI定时任务 {task.name} 执行失败: {e}", exc_info=True)
                                    task.refresh_from_db()
                                    task.failed_runs += 1
                                    task.error_message = str(e)
                                    task.last_result = {
                                        'status': 'failed',
                                        'error': str(e)
                                    }
                                    # 即使失败也要重新计算下次运行时间
                                    task.next_run_time = task.calculate_next_run()
                                    task.save()

                                    # 发送失败通知
                                    print("       === 开始检查发送失败通知 ===")
                                    notification_setting = None
                                    if hasattr(task, 'notification_settings'):
                                        try:
                                            notification_setting = task.notification_settings.first()
                                            print(f"       获取到通知设置（失败情况）: {notification_setting}")
                                            if notification_setting:
                                                print(f"       通知设置详情（失败情况） - ID: {notification_setting.id}, 是否启用: {notification_setting.is_enabled}, 失败通知: {notification_setting.notify_on_failure}")
                                            else:
                                                print("       没有找到通知设置（失败情况）")
                                        except Exception as notify_error:
                                            print(f"       获取任务通知设置时出错（失败情况）: {notify_error}", file=sys.stderr)
                                            import traceback
                                            traceback.print_exc()
                                    else:
                                        print("       任务没有notification_settings属性（失败情况）")

                                    if notification_setting and notification_setting.is_enabled:
                                        print("       通知设置已启用，准备发送失败通知")
                                        if notification_setting.notify_on_failure:
                                            print("       调用 _send_task_notification 方法发送失败通知")
                                            try:
                                                from apps.ui_automation.views import UiScheduledTaskViewSet
                                                viewset = UiScheduledTaskViewSet()
                                                viewset._send_task_notification(task, success=False)
                                                print("       ✓ 失败通知已发送")
                                            except Exception as notify_error:
                                                print(f"       ✗ 发送UI定时任务 {task.name} 失败通知失败: {notify_error}", file=sys.stderr)
                                        else:
                                            print("       通知设置中未启用失败通知")
                                    else:
                                        print("       通知设置未启用或不存在，跳过失败通知")
                                    print("       === 结束检查发送失败通知 ===")

                            thread = threading.Thread(target=run_test, daemon=True)
                            thread.start()

                        elif task.task_type == 'TEST_CASE':
                            # 执行单个或多个测试用例
                            if not task.test_cases:
                                self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 未配置测试用例"))
                                # 即使失败也要重新计算下次运行时间
                                task.refresh_from_db()
                                task.next_run_time = task.calculate_next_run()
                                task.save()
                                continue

                            # 获取测试用例
                            from apps.ui_automation.models import TestCase as UiTestCase
                            test_cases_list = UiTestCase.objects.filter(id__in=task.test_cases)

                            if not test_cases_list.exists():
                                self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 的测试用例不存在"))
                                # 即使失败也要重新计算下次运行时间
                                task.refresh_from_db()
                                task.next_run_time = task.calculate_next_run()
                                task.save()
                                continue

                            test_case_count = test_cases_list.count()
                            self.stdout.write(f"    准备执行 {test_case_count} 个测试用例")

                            # 为每个测试用例创建一个临时的测试套件来执行
                            import threading
                            from apps.ui_automation.models import TestSuite
                            from apps.ui_automation.test_executor import TestExecutor

                            def run_test_cases():
                                success_count = 0
                                failed_count = 0
                                results = []

                                for test_case in test_cases_list:
                                    temp_suite = None
                                    try:
                                        # 创建临时测试套件
                                        temp_suite = TestSuite.objects.create(
                                            project=task.project,
                                            name=f"[临时] {test_case.name}"
                                        )

                                        # 添加测试用例到临时套件
                                        temp_suite.test_cases.add(test_case)

                                        # 更新套件执行状态
                                        temp_suite.execution_status = 'running'
                                        temp_suite.save()

                                        # 使用 TestExecutor 执行
                                        executor = TestExecutor(
                                            test_suite=temp_suite,
                                            engine=task.engine,
                                            browser=task.browser,
                                            headless=task.headless,
                                            executed_by=task.created_by
                                        )
                                        executor.run()

                                        # 检查执行结果
                                        temp_suite.refresh_from_db()
                                        suite_executions = temp_suite.executions.all()

                                        if suite_executions.exists():
                                            last_execution = suite_executions.first()

                                            if last_execution.status == 'SUCCESS':
                                                success_count += 1
                                                results.append({
                                                    'case_id': test_case.id,
                                                    'case_name': test_case.name,
                                                    'status': 'success'
                                                })
                                            else:
                                                failed_count += 1
                                                results.append({
                                                    'case_id': test_case.id,
                                                    'case_name': test_case.name,
                                                    'status': 'failed',
                                                    'error': last_execution.error_message
                                                })

                                    except Exception as e:
                                        logger.error(f"执行测试用例 {test_case.name} 失败: {e}")
                                        failed_count += 1
                                        results.append({
                                            'case_id': test_case.id,
                                            'case_name': test_case.name,
                                            'status': 'failed',
                                            'error': str(e)
                                        })
                                    finally:
                                        # 删除临时测试套件
                                        if temp_suite:
                                            temp_suite.delete()

                                # 更新任务执行结果
                                task.refresh_from_db()
                                task.successful_runs += 1
                                task.last_result = {
                                    'status': 'success' if failed_count == 0 else 'partial_success',
                                    'test_case_count': test_case_count,
                                    'success_count': success_count,
                                    'failed_count': failed_count,
                                    'results': results
                                }
                                # 重新计算下次运行时间
                                task.next_run_time = task.calculate_next_run()
                                task.save()

                                logger.info(f"UI定时任务 {task.name} 执行完成: 成功{success_count}, 失败{failed_count}")

                                # 发送通知
                                success = (failed_count == 0)
                                if success:
                                    print("       === 开始检查发送成功通知 ===")
                                else:
                                    print("       === 开始检查发送失败通知 ===")

                                notification_setting = None
                                if hasattr(task, 'notification_settings'):
                                    try:
                                        notification_setting = task.notification_settings.first()
                                        print(f"       获取到通知设置: {notification_setting}")
                                        if notification_setting:
                                            if success:
                                                print(f"       通知设置详情 - ID: {notification_setting.id}, 是否启用: {notification_setting.is_enabled}, 成功通知: {notification_setting.notify_on_success}")
                                            else:
                                                print(f"       通知设置详情 - ID: {notification_setting.id}, 是否启用: {notification_setting.is_enabled}, 失败通知: {notification_setting.notify_on_failure}")
                                        else:
                                            print("       没有找到通知设置")
                                    except Exception as e:
                                        print(f"       获取任务通知设置时出错: {e}", file=sys.stderr)
                                        import traceback
                                        traceback.print_exc()
                                else:
                                    print("       任务没有notification_settings属性")

                                if notification_setting and notification_setting.is_enabled:
                                    print("       通知设置已启用，准备发送通知")
                                    if success and notification_setting.notify_on_success:
                                        print("       调用 _send_task_notification 方法发送成功通知")
                                        try:
                                            from apps.ui_automation.views import UiScheduledTaskViewSet
                                            viewset = UiScheduledTaskViewSet()
                                            viewset._send_task_notification(task, success=True)
                                            print(f"       ✓ 成功通知已发送 (成功:{success_count}, 失败:{failed_count})")
                                        except Exception as e:
                                            print(f"       ✗ 发送UI定时任务 {task.name} 成功通知失败: {e}", file=sys.stderr)
                                    elif not success and notification_setting.notify_on_failure:
                                        print("       调用 _send_task_notification 方法发送失败通知")
                                        try:
                                            from apps.ui_automation.views import UiScheduledTaskViewSet
                                            viewset = UiScheduledTaskViewSet()
                                            viewset._send_task_notification(task, success=False)
                                            print(f"       ✓ 失败通知已发送 (成功:{success_count}, 失败:{failed_count})")
                                        except Exception as e:
                                            print(f"       ✗ 发送UI定时任务 {task.name} 失败通知失败: {e}", file=sys.stderr)
                                    else:
                                        if success:
                                            print("       通知设置中未启用成功通知")
                                        else:
                                            print("       通知设置中未启用失败通知")
                                else:
                                    print("       通知设置未启用或不存在，跳过通知")

                                if success:
                                    print("       === 结束检查发送成功通知 ===")
                                else:
                                    print("       === 结束检查发送失败通知 ===")

                            # 在后台线程中执行
                            thread = threading.Thread(target=run_test_cases, daemon=True)
                            thread.start()

                        executed_count += 1
                        self.stdout.write(self.style.SUCCESS(f"    ✓ 任务 {task.name} 已启动"))

                    except Exception as e:
                        logger.error(f"执行UI任务 {task.name} 时出错: {e}", exc_info=True)
                        self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 执行失败: {e}"))

            return executed_count

        except Exception as e:
            logger.error(f"调度UI任务时出错: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"[UI] 调度失败: {e}"))
            return 0

    def schedule_app_tasks(self):
        """调度 APP 自动化模块的定时任务"""
        try:
            from apps.app_automation.models import AppScheduledTask, AppTestExecution

            active_tasks = AppScheduledTask.objects.filter(status='ACTIVE')
            executed_count = 0

            if active_tasks.exists():
                now = timezone.now()
                self.stdout.write(f"  [APP] 活跃任务数: {active_tasks.count()}")
                for task in active_tasks:
                    if task.next_run_time:
                        time_diff = (task.next_run_time - now).total_seconds()
                        if time_diff > 0:
                            self.stdout.write(f"        - {task.name}: 距下次执行还有 {int(time_diff)} 秒")
                        else:
                            self.stdout.write(f"        - {task.name}: 应该立即执行！")
                    else:
                        self.stdout.write(f"        - {task.name}: 未设置下次执行时间")

            for task in active_tasks:
                if task.should_run_now():
                    self.stdout.write(f"  [APP] 执行任务: {task.name}")
                    self.stdout.write(f"       类型: {task.get_task_type_display()}, 触发方式: {task.get_trigger_type_display()}")
                    try:
                        # 更新统计
                        task.last_run_time = timezone.now()
                        task.total_runs += 1
                        task.next_run_time = task.calculate_next_run()
                        task.save()

                        device = task.device
                        if not device:
                            self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 未配置设备"))
                            continue

                        package_name = task.app_package.package_name if task.app_package else ''

                        if task.task_type == 'TEST_SUITE' and task.test_suite:
                            suite_cases = task.test_suite.suite_cases.select_related('test_case').all()
                            if not suite_cases.exists():
                                self.stdout.write(self.style.ERROR(f"    ✗ 套件 {task.test_suite.name} 无用例"))
                                continue

                            executions = []
                            for sc in suite_cases:
                                execution = AppTestExecution.objects.create(
                                    test_case=sc.test_case,
                                    test_suite=task.test_suite,
                                    device=device,
                                    user=task.created_by,
                                    status='pending'
                                )
                                executions.append(execution)

                            task.test_suite.execution_status = 'running'
                            task.test_suite.save(update_fields=['execution_status'])

                            from apps.app_automation.tasks import execute_app_suite_task
                            execute_app_suite_task.delay(
                                suite_id=task.test_suite.id,
                                execution_ids=[e.id for e in executions],
                                package_name=package_name,
                                scheduled_task_id=task.id,
                            )

                        elif task.task_type == 'TEST_CASE' and task.test_case:
                            execution = AppTestExecution.objects.create(
                                test_case=task.test_case,
                                device=device,
                                user=task.created_by,
                                status='pending'
                            )
                            from apps.app_automation.tasks import execute_app_test_task
                            celery_task = execute_app_test_task.delay(
                                execution.id,
                                package_name=package_name,
                                scheduled_task_id=task.id,
                            )
                            execution.task_id = celery_task.id
                            execution.save(update_fields=['task_id'])

                        else:
                            self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 配置不完整"))
                            continue

                        executed_count += 1
                        self.stdout.write(self.style.SUCCESS(f"    ✓ 任务 {task.name} 已启动"))

                    except Exception as e:
                        logger.error(f"执行APP任务 {task.name} 时出错: {e}", exc_info=True)
                        self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 执行失败: {e}"))

            return executed_count

        except Exception as e:
            logger.error(f"调度APP任务时出错: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"[APP] 调度失败: {e}"))
            return 0

    def schedule_perf_tasks(self):
        """调度性能测试模块的定时压测任务。

        压测是异步长任务，调度器只负责「到点拉起子进程」：
        - 派发成功后调用 task.mark_dispatched() 累加 run_count、推进 next_run_at
          （ONCE 任务自动暂停）；
        - 真正的 success_count/fail_count 由压测子进程收尾时回写
          （见 services/executor._update_task_stats），避免两处重复计数。
        """
        try:
            from apps.perf_testing.models import PerfScheduledTask
            from apps.perf_testing.services import executor

            active_tasks = PerfScheduledTask.objects.filter(status='ACTIVE').select_related('scenario', 'created_by')
            executed_count = 0

            if active_tasks.exists():
                now = timezone.now()
                self.stdout.write(f"  [性能] 活跃任务数: {active_tasks.count()}")
                for task in active_tasks:
                    if task.next_run_at:
                        time_diff = (task.next_run_at - now).total_seconds()
                        if time_diff > 0:
                            self.stdout.write(f"        - {task.name}: 距下次执行还有 {int(time_diff)} 秒")
                        else:
                            self.stdout.write(f"        - {task.name}: 应该立即执行！")
                    else:
                        self.stdout.write(f"        - {task.name}: 未设置下次执行时间")

            for task in active_tasks:
                if not task.should_run_now():
                    continue

                self.stdout.write(f"  [性能] 执行任务: {task.name}")
                self.stdout.write(f"       触发方式: {task.get_trigger_type_display()}")
                try:
                    scenario = task.scenario
                    if scenario.has_active_execution():
                        # 场景已有正在执行的压测，跳过本轮，不推进 next_run_at，
                        # 下个调度周期再尝试，避免重复加压。
                        self.stdout.write(self.style.WARNING(
                            f"    ! 任务 {task.name} 所属场景已有执行中的压测，本轮跳过"))
                        continue

                    # trigger_type 固定 SCHEDULED，便于执行记录归属与通知判定
                    execution, check = executor.start_execution(
                        scenario, user=task.created_by,
                        trigger_type='SCHEDULED', scheduled_task=task)

                    if execution is None:
                        # preflight 未通过，属于派发阶段失败
                        errors = (check or {}).get('errors') or []
                        error_msg = '; '.join(errors) if errors else '执行前检查未通过'
                        task.mark_dispatched(error=error_msg)
                        self.stdout.write(self.style.ERROR(
                            f"    ✗ 任务 {task.name} 前置检查未通过: {error_msg}"))
                        continue

                    task.mark_dispatched()
                    executed_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"    ✓ 任务 {task.name} 已启动 (执行 {execution.execution_no})"))

                except Exception as e:
                    logger.error(f"执行性能任务 {task.name} 时出错: {e}", exc_info=True)
                    # 派发阶段异常，计入失败并推进调度，避免卡死
                    try:
                        task.mark_dispatched(error=str(e))
                    except Exception:  # noqa: BLE001
                        logger.error(f"回写性能任务 {task.name} 失败状态时出错", exc_info=True)
                    self.stdout.write(self.style.ERROR(f"    ✗ 任务 {task.name} 执行失败: {e}"))

            return executed_count

        except Exception as e:
            logger.error(f"调度性能任务时出错: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"[性能] 调度失败: {e}"))
            return 0

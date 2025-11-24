#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
from pathlib import Path
from utils.config_reader import WebUIConfReader
from utils.date_time_tool import DateTimeTool
import argparse
import pytest
from datetime import datetime
from loguru import logger
import shutil


log_dir = Path(__file__).parent / 'test-results' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"run_test_detail_{datetime.now().strftime('%Y%m%d')}.log"
logger.add(str(log_file), rotation="00:00", encoding="utf-8", retention="7 days", enqueue=True, level="INFO")


def main():
    # 日志文件路径 test-results/logs/run_test_detail_YYYYMMDD.log

    parser = argparse.ArgumentParser(description="UI自动化测试执行器")
    parser.add_argument('-k', '--keyword', help='只执行匹配关键字的用例，会匹配文件名', type=str)
    parser.add_argument('-d', '--dir', help='指定要测试的目录', type=str, default='test_cases/adts/')
    parser.add_argument('-m', '--markexpr', help='只运行符合给定的mark表达式的测试', type=str)
    parser.add_argument('-s', '--capture', help='是否在标准输出流中输出日志', action='store_true')
    parser.add_argument('-r', '--reruns', help='失败重跑次数', type=int, default=0)
    parser.add_argument('-lf', '--lf', help='是否运行上一次失败的用例', action='store_true')
    parser.add_argument('--clean-alluredir', help='是否清空已有测试结果', action='store_true')
    parser.add_argument('-n', '--n', help='n是指定并发数', type=str)
    parser.add_argument('-task_id', '--task_id', help='task_id-任务编号', type=str)
    parser.add_argument('-case_id', '--case_id', help='case_id-用例编号', type=str)
    parser.add_argument('--tracing', '--tracing', help='开启追踪', type=str)

    args = parser.parse_args()

    logger.info("加载UI自动化测试配置...")
    web_ui_config = WebUIConfReader().config
    logger.info("UI自动化测试配置加载完成")

    logger.info("开始测试...")
    # 在pytest执行前清理report目录
    report_dir = Path(__file__).parent / 'test-results' / 'report'
    if report_dir.exists():
        shutil.rmtree(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    exit_code = 0
    for current_browser in web_ui_config['test_browsers']:
        logger.info(f"开始 {current_browser} 浏览器测试...")
        
        pytest_execute_params = ['-c', 'config/pytest.ini', '-v']
        
        if web_ui_config['is_headed']:
            pytest_execute_params.append('--headed')
        if web_ui_config['slowmo'] > 0:
            pytest_execute_params.extend(['--slowmo', str(web_ui_config['slowmo'])])
        if web_ui_config['trace'] == 'on':
            pytest_execute_params.extend(['--tracing', "on"])

        if args.keyword:
            pytest_execute_params.extend(['-k', args.keyword])

        if args.n:
            pytest_execute_params.extend(['-n', args.n])
            
        if args.markexpr:
            pytest_execute_params.extend(['-m', args.markexpr])
            
        if args.capture:
            pytest_execute_params.append('-s')
            
        if args.reruns > 0:
            pytest_execute_params.extend(['--reruns', str(args.reruns)])
            
        if args.lf:
            pytest_execute_params.append('--lf')
            
        if args.clean_alluredir:
            pytest_execute_params.append('--clean-alluredir')
            
        pytest_execute_params.append(args.dir)

        try:
            tmp_exit_code = pytest.main(pytest_execute_params)
            if tmp_exit_code != 0:
                exit_code = tmp_exit_code
        except Exception as e:
            logger.error(f"执行pytest时发生错误: {e}")
            exit_code = 1

        logger.info(f"结束 {current_browser} 浏览器测试...")


    logger.info(f"结束测试，退出码: {exit_code}")
    # 生成并打开allure报告
    try:
        logger.info("生成Allure测试报告...")
        os.system(f"allure generate {report_dir} -o ./test-results/allure-report --clean")
        logger.info("打开Allure测试报告...")
        os.system("allure open ./test-results/allure-report")
    except Exception as e:
        logger.error(f"Allure报告生成或打开失败: {e}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

"""
BaseExecutor测试用例
展示如何使用BaseExecutor执行YAML测试用例
"""

import allure
import pytest
from playwright.sync_api import Page
from base.BaseExecutor import BaseExecutor
from loguru import logger
from pathlib import Path
import os
from datetime import datetime

# 日志文件路径 test-results/logs/test_executor_detail_YYYYMMDD.log
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test-results', 'logs')
os.makedirs(log_dir, exist_ok=True)

@allure.feature('测试***demo')
class TestBaseExecutor:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, pages: dict):
        self.page = page
        locations_path = str(Path(__file__).parent.parent.parent / 'config' / 'msfs_locations.yaml')
        self.executor = BaseExecutor(page, pages, locations_path=locations_path)
        self.logger = logger.bind(name=self.__class__.__name__)
        self.test_data_path = os.path.join(os.path.dirname(__file__), "../../test_data/msfs/test_anliku.yml")

    @pytest.mark.P2
    @allure.story('***查询')
    @allure.title('***查询-模糊查询正确')
    @allure.description('***查询-模糊查询-查看结果是否正确')
    def test_02(self):
        result = self.executor.execute_test_case('msfs_search_02', self.executor.load_test_case(self.test_data_path))
        assert result['success'] is True, f"测试用例执行失败: {result.get('error_message', '')}"
        allure.attach.file("test-results/screenshot/search_CZtest.png", name="***模糊查询-截图01", attachment_type=allure.attachment_type.PNG)

    @pytest.mark.P2
    @allure.story('***导入')
    @allure.title('***导入-已导入的anan不能重复导入')
    @allure.description('***导入-已导入的anan不能重复导入')
    def test_03(self):
        result = self.executor.execute_test_case('msfs_import_03', self.executor.load_test_case(self.test_data_path))
        assert result['success'] is True, f"测试用例执行失败: {result.get('error_message', '')}"
        allure.attach.file("test-results/screenshot/import01.png", name="***导入-截图01", attachment_type=allure.attachment_type.PNG)

    @pytest.mark.P1
    @allure.story('***导入')
    @allure.title('***导入-***导入成功')
    @allure.description('***导入-新anan导入成功')
    def test_05(self):
        result = self.executor.execute_test_case('msfs_import_05', self.executor.load_test_case(self.test_data_path))
        assert result['success'] is True, f"测试用例执行失败: {result.get('error_message', '')}"
        allure.attach.file("test-results/screenshot/import03.png", name="***导入-截图01", attachment_type=allure.attachment_type.PNG)
        allure.attach.file("test-results/screenshot/import_success.png", name="***导入-截图01", attachment_type=allure.attachment_type.PNG)

    @pytest.mark.P1
    @allure.story('***列表')
    @allure.title('***列表-anan移除成功')
    @allure.description('***列表-anan移除成功')
    def test_09(self):
        result = self.executor.execute_test_case('msfs_list_09', self.executor.load_test_case(self.test_data_path))
        assert result['success'] is True, f"测试用例执行失败: {result.get('error_message', '')}"
        allure.attach.file("test-results/screenshot/remove_success.png", name="***导入-截图01", attachment_type=allure.attachment_type.PNG)

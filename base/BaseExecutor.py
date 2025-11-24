"""
BaseExecutor类 - UI自动化测试执行器
解析YAML测试用例并使用BasePage和BaseAssert执行UI自动化操作
"""

import yaml
import os
from datetime import datetime
from loguru import logger
from typing import Dict, List, Any, Optional
from playwright.sync_api import Page
from base.BasePage import BasePage
from base.BaseAssert import Assertion, PageAssertion
from pathlib import Path
import re
import allure
import time


class BaseExecutor:
    """UI自动化测试执行器"""
    
    def __init__(self, page: Page, pages: Optional[Dict[str, str]] = None, locations_path: Optional[str] = None):
        """
        初始化执行器

        """
        self.page = page
        self.base_page = BasePage(page)
        self.page_assertion = PageAssertion(page)
        
        # 修复日志配置
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test-results', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"executor_detail_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 移除之前的日志处理器（如果存在）
        logger.remove()
        
        # 重新配置日志
        logger.add(
            log_file, 
            rotation="00:00", 
            encoding="utf-8", 
            retention="7 days", 
            enqueue=True, 
            level="INFO",
            backtrace=True,
            diagnose=True
        )
        
        self.logger = logger.bind(name=self.__class__.__name__)
        self.pages_dict = pages or {}
        self.current_input_value = ""  # 添加当前输入值跟踪
        self.screenshot_files = {}  # 添加截图文件路径跟踪
        
        # 智能等待配置
        self.enable_smart_wait = True  # 是否启用智能等待
        self.smart_wait_timeout = 10000  # 智能等待超时时间（毫秒）
        self.smart_wait_interval = 0.5  # 智能等待检查间隔（秒）
        
        # 加载 adts_locations.yaml（现在通过参数传入）
        if locations_path is None:
            locations_path = str(Path(__file__).parent.parent / 'config' / 'adts_locations.yaml')
        with open(locations_path, 'r', encoding='utf-8') as f:
            self.locations_dict = yaml.safe_load(f)
        
        # 操作映射字典
        self.action_handlers = {
            'navigate': self._handle_navigate,
            'click': self._handle_click,
            'input': self._handle_input,
            'clear_and_input': self._handle_clear_and_input,
            'select': self._handle_select,
            'select_option_by_label': self._handle_select_option_by_label,
            'check': self._handle_check,
            'uncheck': self._handle_uncheck,
            'upload': self._handle_upload,
            'hover': self._handle_hover,
            'double_click': self._handle_double_click,
            'right_click': self._handle_right_click,
            'wait': self._handle_wait,
            'wait_for_element': self._handle_wait_for_element,
            'wait_for_element_hidden': self._handle_wait_for_element_hidden,
            'wait_for_load_state': self._handle_wait_for_load_state,
            'wait_for_network_idle': self._handle_wait_for_network_idle,
            'scroll_to_element': self._handle_scroll_to_element,
            'scroll_to_bottom': self._handle_scroll_to_bottom,
            'scroll_to_top': self._handle_scroll_to_top,
            'press_key': self._handle_press_key,
            'press_enter': self._handle_press_enter,
            'press_tab': self._handle_press_tab,
            'press_escape': self._handle_press_escape,
            'type_text': self._handle_type_text,
            'refresh_page': self._handle_refresh_page,
            'go_back': self._handle_go_back,
            'go_forward': self._handle_go_forward,
            'take_screenshot': self._handle_take_screenshot,
            'execute_script': self._handle_execute_script,
            'accept_dialog': self._handle_accept_dialog,
            'dismiss_dialog': self._handle_dismiss_dialog,
            'get_dialog_text': self._handle_get_dialog_text,
            # 获取信息类操作
            'get_text': self._handle_get_text,
            'get_attribute': self._handle_get_attribute,
            'get_value': self._handle_get_value,
            'is_visible': self._handle_is_visible,
            'is_enabled': self._handle_is_enabled,
            'get_page_title': self._handle_get_page_title,
            'get_current_url': self._handle_get_current_url,
        }
        
        # 断言映射字典
        self.assertion_handlers = {
            'assert_element_visible': self._handle_assert_element_visible,
            'assert_element_hidden': self._handle_assert_element_hidden,
            'assert_text_contains': self._handle_assert_text_contains,
            'assert_text_equals': self._handle_assert_text_equals,
            'assert_value_equals': self._handle_assert_value_equals,
            'assert_url_contains': self._handle_assert_url_contains,
            'assert_title_contains': self._handle_assert_title_contains,
            'assert_element_enabled': self._handle_assert_element_enabled,
            'assert_element_disabled': self._handle_assert_element_disabled,
            'assert_element_checked': self._handle_assert_element_checked,
            'assert_element_not_checked': self._handle_assert_element_not_checked,
            'assert_count': self._handle_assert_count,
            'assert_equal': self._handle_assert_equal,
            'assert_not_equal': self._handle_assert_not_equal,
            'assert_true': self._handle_assert_true,
            'assert_false': self._handle_assert_false,
            'assert_in': self._handle_assert_in,
            'assert_not_in': self._handle_assert_not_in,
            'assert_is_none': self._handle_assert_is_none,
            'assert_is_not_none': self._handle_assert_is_not_none,
            'assert_greater': self._handle_assert_greater,
            'assert_less': self._handle_assert_less,
            # 新增：断言元素属性包含子串
            'attribute_include': self._handle_assert_attribute_include,
        }
    
    def load_test_case(self, yaml_file_path: str) -> Dict[str, Any]:
        """
        加载YAML测试用例文件
        
        Args:
            yaml_file_path: YAML文件路径
            
        Returns:
            测试用例数据字典
        """
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as file:
                test_data = yaml.safe_load(file)
            self.logger.info(f"成功加载测试用例文件: {yaml_file_path}")
            return test_data
        except Exception as e:
            self.logger.error(f"加载测试用例文件失败: {e}")
            raise
    
    def execute_test_case(self, test_case_name: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行指定的测试用例（支持test_anliku.yml格式）
        
        Returns:
            包含执行结果的字典:
            {
                'success': bool,  # 整体执行是否成功
                'test_cases': [   # 每个测试用例的执行结果
                    {
                        'case_name': str,  # 测试用例名称
                        'input_value': str,  # 输入值
                        'success': bool,  # 是否成功
                        'steps': [  # 步骤执行详情
                            {
                                'step_num': int,  # 步骤编号
                                'action': str,  # 操作类型
                                'selector': str,  # 选择器
                                'value': Any,  # 操作值
                                'expected': Any,  # 期望值
                                'success': bool,  # 是否成功
                                'error_message': str,  # 错误信息
                                'duration_ms': float  # 执行时长
                            }
                        ],
                        'error_message': str,  # 整体错误信息
                        'duration_ms': float  # 总执行时长
                    }
                ],
                'total_success': int,  # 成功的测试用例数量
                'total_failed': int,  # 失败的测试用例数量
                'error_message': str  # 整体错误信息
            }
        """
        start_time = time.time()
        try:
            test_case = test_data.get(test_case_name)
            if not test_case:
                error_msg = f"未找到测试用例: {test_case_name}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'test_cases': [],
                    'total_success': 0,
                    'total_failed': 0,
                    'error_message': error_msg
                }
            
            steps = test_case.get('steps', [])
            
            # 检查是否有需要循环的input步骤，生成独立的测试用例数据
            test_cases = self._generate_test_cases(test_case_name, test_case)
            
            # 如果有多个测试用例（数据驱动），添加Allure步骤提示
            if len(test_cases) > 1:
                @allure.step("---遍历执行多条用例---")
                def execute_multiple_cases():
                    return self._execute_multiple_test_cases(test_cases)
                
                result = execute_multiple_cases()
            else:
                # 单个测试用例，直接执行
                case_data = test_cases[0]
                case_steps = case_data['steps']
                result = self._execute_steps_with_details(case_steps)
            
            # 计算总执行时长
            total_duration = (time.time() - start_time) * 1000
            
            # 统计成功和失败数量
            total_success = sum(1 for case in result['test_cases'] if case['success'])
            total_failed = len(result['test_cases']) - total_success
            
            # 整体成功判断
            overall_success = total_failed == 0
            
            return {
                'success': overall_success,
                'test_cases': result['test_cases'],
                'total_success': total_success,
                'total_failed': total_failed,
                'error_message': result.get('error_message', ''),
                'duration_ms': total_duration
            }
                
        except Exception as e:
            error_msg = f"执行测试用例失败: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'test_cases': [],
                'total_success': 0,
                'total_failed': 0,
                'error_message': error_msg,
                'duration_ms': (time.time() - start_time) * 1000
            }
    
    def _generate_test_cases(self, test_case_name: str, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成测试用例列表，处理input value为列表的情况，支持loop_steps
        
        Args:
            test_case_name: 测试用例名称
            test_case: 原始测试用例数据
            
        Returns:
            测试用例列表，每个元素是一个独立的测试用例
        """
        steps = test_case.get('steps', [])
        loop_steps_config = test_case.get('loop_steps', {})  # 获取loop_steps配置
        test_cases = []
        
        self.logger.info(f"开始生成测试用例: {test_case_name}")
        self.logger.info(f"原始步骤数量: {len(steps)}")
        self.logger.info(f"loop_steps配置: {loop_steps_config}")
        
        # 检查是否有需要循环的input步骤
        input_loop_steps = []
        for step in steps:
            if isinstance(step, dict) and 'input' in step:
                input_step = step['input']
                if isinstance(input_step, dict) and 'value' in input_step:
                    value = input_step['value']
                    if isinstance(value, list):
                        # 找到需要循环的步骤
                        input_loop_steps.append((step, value))
                        self.logger.info(f"找到循环input步骤，值列表: {value}")
        
        if input_loop_steps:
            # 有循环步骤，为每个值生成独立的测试用例
            for loop_step, values in input_loop_steps:
                for i, value in enumerate(values):
                    # 创建当前循环的测试用例
                    case_copy = test_case.copy()
                    case_copy['case_name'] = f"{test_case.get('case_name', test_case_name)}_{i+1}"
                    case_copy['input_value'] = value  # 记录当前输入值
                    
                    self.logger.info(f"生成测试用例 {i+1}: {case_copy['case_name']}, 输入值: {value}")
                    
                    # 创建修改后的步骤，确保正确的执行顺序
                    modified_steps = []
                    input_step_index = steps.index(loop_step)
                    
                    # 1. 先添加input步骤之前的所有步骤
                    for j in range(input_step_index):
                        modified_steps.append(steps[j])
                    
                    # 2. 添加当前循环的input步骤（替换值为单个值）
                    step_copy = loop_step.copy()
                    step_copy['input'] = step_copy['input'].copy()
                    step_copy['input']['value'] = value
                    modified_steps.append(step_copy)
                    
                    # 3. 添加该循环值对应的loop_steps步骤
                    if value in loop_steps_config:
                        loop_steps_for_value = loop_steps_config[value]
                        if isinstance(loop_steps_for_value, list):
                            self.logger.info(f"为输入值 {value} 添加 {len(loop_steps_for_value)} 个loop_steps步骤")
                            for step_idx, loop_step_item in enumerate(loop_steps_for_value):
                                self.logger.info(f"  loop_step {step_idx + 1}: {loop_step_item}")
                            modified_steps.extend(loop_steps_for_value)
                        else:
                            self.logger.warning(f"循环值 {value} 的loop_steps格式不正确，应为列表")
                    else:
                        self.logger.warning(f"未找到输入值 {value} 对应的loop_steps配置")
                    
                    # 4. 添加input步骤之后的所有剩余步骤
                    for j in range(input_step_index + 1, len(steps)):
                        modified_steps.append(steps[j])
                    
                    case_copy['steps'] = modified_steps
                    self.logger.info(f"测试用例 {case_copy['case_name']} 最终步骤数量: {len(modified_steps)}")
                    test_cases.append(case_copy)
        else:
            # 无循环步骤，直接使用原始测试用例
            test_case['input_value'] = ''  # 无输入值
            test_cases.append(test_case)
            self.logger.info("无循环步骤，使用原始测试用例")
        
        self.logger.info(f"总共生成 {len(test_cases)} 个测试用例")
        return test_cases
    
    def _execute_steps(self, steps: List[Dict[str, Any]]) -> bool:
        """
        执行步骤列表
        
        Args:
            steps: 步骤列表
            
        Returns:
            执行结果
        """
        for i, step in enumerate(steps, 1):
            if not isinstance(step, dict):
                self.logger.error(f"步骤格式错误: {step}")
                return False
            # 兼容 input: xxx + value: yyy 这种格式
            if len(step) > 1:
                action = list(step.keys())[0]
                params = {k: v for k, v in step.items()}
            else:
                action, params = list(step.items())[0]

            # 处理参数
            if isinstance(params, dict):
                # 对于input操作，优先从selector字段获取元素路径
                if action == 'input':
                    element_path = params.get('selector') or params.get('element') or params.get('target') or params.get('locator')
                else:
                    element_path = params.get(action) or params.get('element') or params.get('target') or params.get('locator')
                value = params.get('value')
                expected = params.get('expected')
            else:
                element_path = params
                value = step.get('value')
                expected = step.get('expected')
            
            # 调试日志
            self.logger.debug(f"步骤 {i}: action={action}, element_path={element_path}, value={value}")
            
            # 判断是否为元素路径
            def is_element_path(path: str) -> bool:
                return isinstance(path, str) and 'Path' in path

            selector = None
            if element_path and is_element_path(element_path):
                try:
                    t1 = re.search(r'Path\((.*?)\)', element_path)
                    tmp_path = t1.group(1) if t1 else None
                    # 支持 .f(...) 形式动态传参
                    t2 = re.search(r'\.f\((.*?)\)', element_path)
                    tmp_value = t2.group(1) if t2 else None

                    selector = self.resolve_selector(self.locations_dict, tmp_path)
                    if tmp_value is not None:
                        selector = selector.format(tmp_value)
                except Exception as e:
                    self.logger.error(f"元素路径解析失败: {element_path}, 错误: {e}")
                    return False
            else:
                selector = element_path  # 直接用原始值（如文件路径）
            
            # 检查selector是否为空
            if action in ['click', 'hover', 'input', 'clear_and_input', 'select', 'select_option_by_label', 'check', 'uncheck', 'upload', 'double_click', 'right_click', 'wait_for_element', 'wait_for_element_hidden', 'scroll_to_element', 'execute_script', 'get_text', 'get_attribute', 'get_value', 'is_visible', 'is_enabled', 'assert'] and not selector:
                self.logger.error(f"步骤 {i}: {action} 操作的selector为空，element_path={element_path}")
                return False
            
            # 使用allure.step装饰器记录每个步骤
            step_description = self._get_step_description(action, selector, value, expected, i)
            
            @allure.step(step_description)
            def execute_single_step():
                return self._execute_single_step(action, selector, value, expected, i)
            
            # 执行步骤
            if not execute_single_step():
                return False
                
        return True
    
    def _get_step_description(self, action: str, selector: str, value: Any, expected: Any, step_num: int) -> str:
        """
        生成步骤描述，用于Allure报告
        
        Args:
            action: 操作类型
            selector: 元素选择器
            value: 操作值
            expected: 期望值
            step_num: 步骤编号
            
        Returns:
            步骤描述字符串
        """
        descriptions = {
            'navigate': f"步骤{step_num}: 导航到 {selector or '页面'}",
            'click': f"步骤{step_num}: 点击元素 {selector}",
            'hover': f"步骤{step_num}: 悬停元素 {selector}",
            'input': f"步骤{step_num}: 输入文本到元素 {selector}，内容: {value}",
            'clear_and_input': f"步骤{step_num}: 清空并输入文本到元素 {selector}，内容: {value}",
            'select': f"步骤{step_num}: 选择下拉框 {selector} 的选项: {value}",
            'select_option_by_label': f"步骤{step_num}: 通过标签选择下拉框 {selector} 的选项: {value}",
            'check': f"步骤{step_num}: 勾选复选框 {selector}",
            'uncheck': f"步骤{step_num}: 取消勾选复选框 {selector}",
            'upload': f"步骤{step_num}: 上传文件到 {selector}，文件: {value}",
            'double_click': f"步骤{step_num}: 双击元素 {selector}",
            'right_click': f"步骤{step_num}: 右键点击元素 {selector}",
            'wait': f"步骤{step_num}: 等待 {value or 1000} 毫秒",
            'wait_for_element': f"步骤{step_num}: 等待元素出现 {selector}",
            'wait_for_element_hidden': f"步骤{step_num}: 等待元素隐藏 {selector}",
            'wait_for_load_state': f"步骤{step_num}: 等待页面加载状态: {value}",
            'wait_for_network_idle': f"步骤{step_num}: 等待网络空闲",
            'scroll_to_element': f"步骤{step_num}: 滚动到元素 {selector}",
            'scroll_to_bottom': f"步骤{step_num}: 滚动到页面底部",
            'scroll_to_top': f"步骤{step_num}: 滚动到页面顶部",
            'press_key': f"步骤{step_num}: 按下按键 {value or 'Enter'}",
            'press_enter': f"步骤{step_num}: 按下Enter键",
            'press_tab': f"步骤{step_num}: 按下Tab键",
            'press_escape': f"步骤{step_num}: 按下Escape键",
            'type_text': f"步骤{step_num}: 输入文本: {value}",
            'refresh_page': f"步骤{step_num}: 刷新页面",
            'go_back': f"步骤{step_num}: 返回上一页",
            'go_forward': f"步骤{step_num}: 前进到下一页",
            'take_screenshot': f"步骤{step_num}: 截图保存到 {value or selector}",
            'execute_script': f"步骤{step_num}: 执行JavaScript脚本: {value}",
            'accept_dialog': f"步骤{step_num}: 接受对话框",
            'dismiss_dialog': f"步骤{step_num}: 取消对话框",
            'get_dialog_text': f"步骤{step_num}: 获取对话框文本",
            'get_text': f"步骤{step_num}: 获取元素 {selector} 的文本",
            'get_attribute': f"步骤{step_num}: 获取元素 {selector} 的属性 {value}",
            'get_value': f"步骤{step_num}: 获取元素 {selector} 的值",
            'is_visible': f"步骤{step_num}: 检查元素 {selector} 是否可见",
            'is_enabled': f"步骤{step_num}: 检查元素 {selector} 是否启用",
            'get_page_title': f"步骤{step_num}: 获取页面标题",
            'get_current_url': f"步骤{step_num}: 获取当前URL",
            'assert': f"步骤{step_num}: 断言元素 {selector} {expected} {value or ''}",
        }
        
        return descriptions.get(action, f"步骤{step_num}: 执行{action}操作")
    
    def _get_current_input_value(self) -> str:
        """获取当前测试用例的输入值，用于生成唯一文件名"""
        return self.current_input_value or "default"
    
    def get_screenshot_path(self, step_num: int = None, base_name: str = None) -> str:
        """
        获取截图文件路径
        
        Args:
            step_num: 步骤编号，如果指定则返回该步骤的截图路径
            base_name: 基础文件名，如果指定则返回匹配的截图路径
            
        Returns:
            截图文件路径，如果未找到则返回None
        """
        if step_num is not None:
            return self.screenshot_files.get(step_num)
        
        if base_name is not None:
            # 根据基础文件名查找匹配的截图
            for step_num, path in self.screenshot_files.items():
                if base_name in path:
                    return path
        
        # 如果没有找到，返回最后一个截图路径
        if self.screenshot_files:
            return list(self.screenshot_files.values())[-1]
        
        return None
    
    def get_screenshot_by_base_name(self, base_name: str) -> str:
        """
        根据基础文件名获取截图路径
        
        Args:
            base_name: 基础文件名（不包含扩展名），如 'search_task_CZtest06'
            
        Returns:
            截图文件路径，如果未找到则返回None
        """
        key = f"{base_name}_path"
        return self.screenshot_files.get(key)
    
    def verify_screenshot_exists(self, base_name: str) -> bool:
        """
        验证指定基础文件名的截图是否存在
        
        Args:
            base_name: 基础文件名（不包含扩展名）
            
        Returns:
            截图文件是否存在
        """
        screenshot_path = self.get_screenshot_by_base_name(base_name)
        if screenshot_path:
            return os.path.exists(screenshot_path)
        return False
    
    def get_all_screenshot_paths(self) -> Dict[int, str]:
        """
        获取所有截图文件路径
        
        Returns:
            步骤编号到截图路径的映射字典
        """
        return self.screenshot_files.copy()
    
    def _execute_single_step(self, action: str, selector: str, value: Any, expected: Any, step_num: int) -> bool:
        """
        执行单个步骤（被allure.step装饰器包装）
        
        Args:
            action: 操作类型
            selector: 元素选择器
            value: 操作值
            expected: 期望值
            step_num: 步骤编号
            
        Returns:
            执行结果
        """
        try:
            # 动作分流
            if action in ['navigate']:
                self.logger.info(f"步骤 {step_num}: 导航到 {selector or '页面'}")
                url = self.pages_dict.get(selector, selector)
                self.base_page.navigate_to(url)
            elif action in ['click']:
                self.logger.info(f"步骤 {step_num}: 点击元素 {selector}")
                self.base_page.click(selector)
            elif action in ['hover']:
                self.logger.info(f"步骤 {step_num}: 悬停元素 {selector}")
                self.base_page.hover(selector)
            elif action in ['input']:
                # 确保value是字符串类型
                if value is not None:
                    value_str = str(value)
                else:
                    value_str = ""
                self.logger.info(f"步骤 {step_num}: 输入到元素 {selector}，内容: {value_str}")
                self.base_page.input_text(selector, value_str)
                
                # 输入完成后等待一小段时间，让可能的输入事件处理完成
                self.logger.info(f"步骤 {step_num}: 输入完成，等待输入事件处理...")
                try:
                    self.base_page.wait_for_time(0.2)
                    self.logger.info(f"步骤 {step_num}: 输入事件处理完成")
                except Exception as e:
                    self.logger.warning(f"步骤 {step_num}: 等待输入事件处理时出现异常（继续执行）: {e}")
            elif action in ['wait']:
                # 修复wait步骤的value处理
                if value is not None:
                    wait_time = value
                elif selector and selector.isdigit():
                    wait_time = selector
                else:
                    wait_time = 1000  # 默认等待1秒
                
                self.logger.info(f"步骤 {step_num}: 等待 {wait_time} 毫秒")
                self.base_page.wait_for_time(float(wait_time)/1000)
            elif action in ['take_screenshot']:
                # 使用YAML文件中指定的文件路径，只处理相对路径转换
                base_path = value if value is not None else selector
                
                # 确保路径在 test-results/screenshot 下
                if not base_path.startswith('test-results/'):
                    if base_path.startswith('screenshot/'):
                        path = base_path.replace('screenshot/', 'test-results/screenshot/')
                    else:
                        path = f"test-results/screenshot/{base_path}"
                else:
                    path = base_path
                
                # 确保目录存在
                os.makedirs(os.path.dirname(path), exist_ok=True)
                
                self.logger.info(f"步骤 {step_num}: 截图保存到 {path}")
                self.base_page.take_screenshot(path)
                self.screenshot_files[step_num] = path  # 记录截图文件路径
                
                # 记录基于基础文件名的路径，方便后续引用
                if base_path.endswith('.png') or base_path.endswith('.jpg'):
                    base_name = os.path.splitext(os.path.basename(base_path))[0]
                    self.screenshot_files[f"{base_name}_path"] = path
            elif action in ['press_key']:
                # 处理按键操作
                if value is not None:
                    key = str(value)
                else:
                    key = "Enter"  # 默认按键
                self.logger.info(f"步骤 {step_num}: 按下按键 {key}")
                self.base_page.press_key(key)
                
                # 如果是 Enter 键，等待页面数据刷新
                if key.lower() == 'enter':
                    self.logger.info(f"步骤 {step_num}: 按下Enter键后等待页面数据刷新...")
                    try:
                        # 等待网络空闲，确保接口请求完成
                        self.base_page.wait_for_network_idle()
                        self.logger.info(f"步骤 {step_num}: 页面数据刷新完成")
                        
                        # 等待一小段时间让DOM更新完成
                        self.base_page.wait_for_time(0.3)
                        self.logger.info(f"步骤 {step_num}: DOM更新完成")
                    except Exception as e:
                        self.logger.warning(f"步骤 {step_num}: 等待页面数据刷新时出现异常（继续执行）: {e}")
            elif action in ['press_enter']:
                self.logger.info(f"步骤 {step_num}: 按下Enter键")
                self.base_page.press_enter()
                
                # 按下Enter键后等待页面数据刷新
                self.logger.info(f"步骤 {step_num}: 按下Enter键后等待页面数据刷新...")
                try:
                    # 等待网络空闲，确保接口请求完成
                    self.base_page.wait_for_network_idle()
                    self.logger.info(f"步骤 {step_num}: 页面数据刷新完成")
                    
                    # 等待一小段时间让DOM更新完成
                    self.base_page.wait_for_time(0.3)
                    self.logger.info(f"步骤 {step_num}: DOM更新完成")
                except Exception as e:
                    self.logger.warning(f"步骤 {step_num}: 等待页面数据刷新时出现异常（继续执行）: {e}")
            elif action in ['press_tab']:
                self.logger.info(f"步骤 {step_num}: 按下Tab键")
                self.base_page.press_tab()
            elif action in ['press_escape']:
                self.logger.info(f"步骤 {step_num}: 按下Escape键")
                self.base_page.press_escape()
            elif action in ['type_text']:
                self.logger.info(f"步骤 {step_num}: 输入文本: {value}")
                self.base_page.type_text(str(value) if value else "")
            elif action in ['clear_and_input']:
                self.logger.info(f"步骤 {step_num}: 清空并输入文本到元素 {selector}，内容: {value}")
                self.base_page.clear_and_input(selector, str(value) if value else "")
            elif action in ['select_option_by_label']:
                self.logger.info(f"步骤 {step_num}: 通过标签选择下拉框 {selector} 的选项: {value}")
                self.base_page.select_option_by_label(selector, str(value) if value else "")
            elif action in ['wait_for_network_idle']:
                self.logger.info(f"步骤 {step_num}: 等待网络空闲")
                self.base_page.wait_for_network_idle()
            elif action in ['scroll_to_element']:
                self.logger.info(f"步骤 {step_num}: 滚动到元素 {selector}")
                self.base_page.scroll_to_element(selector)
            elif action in ['scroll_to_bottom']:
                self.logger.info(f"步骤 {step_num}: 滚动到页面底部")
                self.base_page.scroll_to_bottom()
            elif action in ['scroll_to_top']:
                self.logger.info(f"步骤 {step_num}: 滚动到页面顶部")
                self.base_page.scroll_to_top()
            elif action in ['execute_script']:
                self.logger.info(f"步骤 {step_num}: 执行JavaScript脚本: {value}")
                self.base_page.execute_script(str(value) if value else "")
            elif action in ['refresh_page']:
                self.logger.info(f"步骤 {step_num}: 刷新页面")
                self.base_page.refresh_page()
            elif action in ['go_back']:
                self.logger.info(f"步骤 {step_num}: 返回上一页")
                self.base_page.go_back()
            elif action in ['go_forward']:
                self.logger.info(f"步骤 {step_num}: 前进到下一页")
                self.base_page.go_forward()
            elif action in ['get_text']:
                self.logger.info(f"步骤 {step_num}: 获取元素 {selector} 的文本")
                text = self.base_page.get_text(selector)
                self.logger.info(f"步骤 {step_num}: 获取到的文本: {text}")
            elif action in ['get_attribute']:
                self.logger.info(f"步骤 {step_num}: 获取元素 {selector} 的属性 {value}")
                attribute = self.base_page.get_attribute(selector, str(value) if value else "")
                self.logger.info(f"步骤 {step_num}: 获取到的属性值: {attribute}")
            elif action in ['get_value']:
                self.logger.info(f"步骤 {step_num}: 获取元素 {selector} 的值")
                actual_value = self.base_page.get_value(selector)
                self.logger.info(f"步骤 {step_num}: 获取到的值: {actual_value}")
            elif action in ['is_visible']:
                self.logger.info(f"步骤 {step_num}: 检查元素 {selector} 是否可见")
                visible = self.base_page.is_visible(selector)
                self.logger.info(f"步骤 {step_num}: 元素可见性: {visible}")
            elif action in ['is_enabled']:
                self.logger.info(f"步骤 {step_num}: 检查元素 {selector} 是否启用")
                enabled = self.base_page.is_enabled(selector)
                self.logger.info(f"步骤 {step_num}: 元素启用状态: {enabled}")
            elif action in ['get_page_title']:
                self.logger.info(f"步骤 {step_num}: 获取页面标题")
                title = self.base_page.get_page_title()
                self.logger.info(f"步骤 {step_num}: 页面标题: {title}")
            elif action in ['get_current_url']:
                self.logger.info(f"步骤 {step_num}: 获取当前URL")
                url = self.base_page.get_current_url()
                self.logger.info(f"步骤 {step_num}: 当前URL: {url}")
            elif action in ['get_dialog_text']:
                self.logger.info(f"步骤 {step_num}: 获取对话框文本")
                text = self.base_page.get_dialog_text()
                self.logger.info(f"步骤 {step_num}: 对话框文本: {text}")
            elif action in ['assert']:
                # 增强断言步骤的执行和日志记录
                self.logger.info(f"步骤 {step_num}: 执行断言 - 选择器: {selector}, 期望: {expected}, 值: {value}")
                
                # 断言前智能等待：等待网络空闲和页面稳定
                if expected in ['包含', '等于']:
                    self.logger.info(f"步骤 {step_num}: 断言前等待页面数据稳定...")
                    try:
                        # 等待网络空闲，确保接口请求完成
                        self.base_page.wait_for_network_idle()
                        self.logger.info(f"步骤 {step_num}: 网络空闲，等待完成")
                        
                        # 使用智能等待方法等待元素内容稳定
                        if expected == '包含' and value:
                            self.logger.info(f"步骤 {step_num}: 等待元素内容包含期望值: {value}")
                            self._wait_for_element_content_stable(selector, expected_content=value)
                        else:
                            self.logger.info(f"步骤 {step_num}: 等待元素内容稳定")
                            self._wait_for_element_content_stable(selector)
                        
                        self.logger.info(f"步骤 {step_num}: 页面数据稳定，开始执行断言")
                    except Exception as e:
                        self.logger.warning(f"步骤 {step_num}: 等待页面稳定时出现异常（继续执行）: {e}")
                
                # 支持多种断言格式
                if expected == '属性':
                    # 断言属性包含：默认断言 class 属性包含 value 作为子串
                    self.logger.info(f"步骤 {step_num}: 断言元素属性包含子串 - 选择器: {selector}, 属性: class, 子串: {value}")
                    locator = self.page.locator(selector)
                    substring = str(value) if value is not None else ''
                    self.page_assertion.assert_element_attribute_contains(locator, 'class', substring)
                elif expected == '包含':
                    actual_text = self.base_page.get_text(selector)
                    self.logger.info(f"步骤 {step_num}: 断言元素文本包含 '{value}', 实际文本: '{actual_text}'")
                    Assertion.assert_in(value, actual_text, f"断言元素文本包含: {value}")
                elif expected == '等于':
                    actual_text = self.base_page.get_text(selector)
                    self.logger.info(f"步骤 {step_num}: 断言元素文本等于 '{value}', 实际文本: '{actual_text}'")
                    Assertion.assert_equal(actual_text, value, f"断言元素文本等于: {value}")
                elif expected == '可见':
                    self.logger.info(f"步骤 {step_num}: 断言元素可见 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_visible(locator)
                elif expected == '不可见':
                    self.logger.info(f"步骤 {step_num}: 断言元素不可见 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_hidden(locator)
                elif expected == '启用':
                    self.logger.info(f"步骤 {step_num}: 断言元素启用 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_enabled(locator)
                elif expected == '禁用':
                    self.logger.info(f"步骤 {step_num}: 断言元素禁用 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_disabled(locator)
                elif expected == '已勾选':
                    self.logger.info(f"步骤 {step_num}: 断言元素已勾选 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_checked(locator)
                elif expected == '未勾选':
                    self.logger.info(f"步骤 {step_num}: 断言元素未勾选 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_not_checked(locator)
                elif expected == 'assert_element_visible':
                    # 支持 assert_element_visible 格式
                    self.logger.info(f"步骤 {step_num}: 断言元素可见 - 选择器: {selector}")
                    locator = self.page.locator(selector)
                    self.page_assertion.assert_element_is_visible(locator)
                else:
                    self.logger.error(f"不支持的断言类型: {expected}")
                    return False
                
                self.logger.info(f"步骤 {step_num}: 断言执行成功")
            else:
                self.logger.error(f"不支持的动作: {action}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"步骤 {step_num} 执行失败: {e}")
            return False

    def _execute_multiple_test_cases(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行多个测试用例（数据驱动测试）
        
        Args:
            test_cases: 测试用例列表
            
        Returns:
            包含执行结果的字典
        """
        all_success = True
        test_case_results = []
        error_messages = []
        
        for i, case_data in enumerate(test_cases):
            case_name = case_data['case_name']
            case_steps = case_data['steps']
            input_value = case_data.get('input_value', '')
            
            # 设置当前输入值，供截图等方法使用
            self.current_input_value = str(input_value) if input_value else "default"
            
            self.logger.info(f"执行第 {i+1}/{len(test_cases)} 个测试用例，输入值: {input_value}")
            
            # 为每个测试用例添加Allure步骤
            step_description = f"执行测试用例 {i+1}/{len(test_cases)} (输入值: {input_value})"
            
            @allure.step(step_description)
            def execute_single_case():
                try:
                    # 执行当前测试用例的步骤
                    case_result = self._execute_steps_with_details(case_steps)
                    return case_result
                except Exception as e:
                    error_msg = f"测试用例 {case_name} (输入值: {input_value}) 执行异常: {e}"
                    self.logger.error(error_msg)
                    return {
                        'test_cases': [{
                            'case_name': case_name,
                            'input_value': input_value,
                            'success': False,
                            'steps': [],
                            'error_message': error_msg,
                            'duration_ms': 0
                        }],
                        'error_message': error_msg
                    }
            
            # 执行当前测试用例
            case_result = execute_single_case()
            
            # 更新测试用例信息
            if case_result['test_cases']:
                test_case_result = case_result['test_cases'][0]
                test_case_result['case_name'] = case_name
                test_case_result['input_value'] = input_value
                
                if not test_case_result['success']:
                    all_success = False
                    error_messages.append(f"测试用例 {case_name} (输入值: {input_value}): {test_case_result['error_message']}")
                
                test_case_results.append(test_case_result)
            else:
                # 如果没有返回测试用例结果，创建一个失败的结果
                failed_result = {
                    'case_name': case_name,
                    'input_value': input_value,
                    'success': False,
                    'steps': [],
                    'error_message': '未返回测试用例结果',
                    'duration_ms': 0
                }
                test_case_results.append(failed_result)
                all_success = False
                error_messages.append(f"测试用例 {case_name} (输入值: {input_value}): 未返回测试用例结果")
        
        return {
            'test_cases': test_case_results,
            'error_message': '; '.join(error_messages) if error_messages else ''
        }

    def _execute_action(self, action: Dict[str, Any], step_name: str, action_index: int) -> bool:
        """
        执行单个操作
        
        Args:
            action: 操作字典
            step_name: 步骤名称
            action_index: 操作索引
            
        Returns:
            执行结果
        """
        try:
            action_type = action.get('action', '')
            target = action.get('target', '')
            value = action.get('value', '')
            expected = action.get('expected', '')
            description = action.get('description', '')
            timeout = action.get('timeout', 30000)
            
            self.logger.info(f"  执行操作 {action_index}: {action_type} - {description}")
            
            # 判断是操作还是断言
            if action_type.startswith('assert'):
                return self._execute_assertion(action_type, target, expected, value, timeout, description)
            else:
                return self._execute_operation(action_type, target, value, timeout, description)
                
        except Exception as e:
            self.logger.error(f"执行操作失败: {e}")
            return False
    
    def _execute_operation(self, action_type: str, target: str, value: Any, timeout: int, description: str) -> bool:
        """
        执行操作
        
        Args:
            action_type: 操作类型
            target: 目标元素
            value: 操作值
            timeout: 超时时间
            description: 操作描述
            
        Returns:
            执行结果
        """
        try:
            handler = self.action_handlers.get(action_type)
            if handler:
                handler(target, value, timeout, description)
                return True
            else:
                self.logger.error(f"不支持的操作类型: {action_type}")
                return False
        except Exception as e:
            self.logger.error(f"执行操作 {action_type} 失败: {e}")
            return False
    
    def _execute_assertion(self, assertion_type: str, target: str, expected: Any, value: Any, timeout: int, description: str) -> bool:
        """
        执行断言
        
        Args:
            assertion_type: 断言类型
            target: 目标元素
            expected: 期望值
            value: 实际值
            timeout: 超时时间
            description: 断言描述
            
        Returns:
            执行结果
        """
        try:
            handler = self.assertion_handlers.get(assertion_type)
            if handler:
                handler(target, expected, value, timeout, description)
                return True
            else:
                self.logger.error(f"不支持的断言类型: {assertion_type}")
                return False
        except Exception as e:
            self.logger.error(f"执行断言 {assertion_type} 失败: {e}")
            return False
    
    # ==================== 操作处理器 ====================
    
    def _handle_navigate(self, target: str, value: Any, timeout: int, description: str):
        """处理导航操作"""
        self.base_page.navigate_to(target)
    
    def _handle_click(self, target: str, value: Any, timeout: int, description: str):
        """处理点击操作"""
        self.base_page.click(target, timeout)
    
    def _handle_input(self, target: str, value: str, timeout: int, description: str):
        """处理输入操作"""
        self.base_page.input_text(target, value, timeout)
    
    def _handle_clear_and_input(self, target: str, value: str, timeout: int, description: str):
        """处理清除并输入操作"""
        self.base_page.clear_and_input(target, value, timeout)
    
    def _handle_select(self, target: str, value: str, timeout: int, description: str):
        """处理选择操作"""
        self.base_page.select_option(target, value, timeout)
    
    def _handle_select_option_by_label(self, target: str, value: str, timeout: int, description: str):
        """处理根据标签选择选项操作"""
        self.base_page.select_option_by_label(target, value, timeout)
    
    def _handle_check(self, target: str, value: Any, timeout: int, description: str):
        """处理勾选操作"""
        self.base_page.check_checkbox(target, timeout)
    
    def _handle_uncheck(self, target: str, value: Any, timeout: int, description: str):
        """处理取消勾选操作"""
        self.base_page.uncheck_checkbox(target, timeout)
    
    def _handle_upload(self, target: str, value: str, timeout: int, description: str):
        """处理文件上传操作"""
        self.base_page.upload_file(target, value, timeout)
    
    def _handle_hover(self, target: str, value: Any, timeout: int, description: str):
        """处理悬停操作"""
        self.base_page.hover(target, timeout)
    
    def _handle_double_click(self, target: str, value: Any, timeout: int, description: str):
        """处理双击操作"""
        self.base_page.double_click(target, timeout)
    
    def _handle_right_click(self, target: str, value: Any, timeout: int, description: str):
        """处理右键点击操作"""
        self.base_page.right_click(target, timeout)
    
    def _handle_wait(self, target: str, value: float, timeout: int, description: str):
        """处理等待操作"""
        self.base_page.wait_for_time(value)
    
    def _handle_wait_for_element(self, target: str, value: Any, timeout: int, description: str):
        """处理等待元素操作"""
        self.base_page.wait_for_element(target, timeout)
    
    def _handle_wait_for_element_hidden(self, target: str, value: Any, timeout: int, description: str):
        """处理等待元素隐藏操作"""
        self.base_page.wait_for_element_hidden(target, timeout)
    
    def _handle_wait_for_load_state(self, target: str, value: str, timeout: int, description: str):
        """处理等待加载状态操作"""
        self.base_page.wait_for_load_state(value, timeout)
    
    def _handle_wait_for_network_idle(self, target: str, value: Any, timeout: int, description: str):
        """处理等待网络空闲操作"""
        self.base_page.wait_for_network_idle(timeout)
    
    def _handle_scroll_to_element(self, target: str, value: Any, timeout: int, description: str):
        """处理滚动到元素操作"""
        self.base_page.scroll_to_element(target, timeout)
    
    def _handle_scroll_to_bottom(self, target: str, value: Any, timeout: int, description: str):
        """处理滚动到底部操作"""
        self.base_page.scroll_to_bottom()
    
    def _handle_scroll_to_top(self, target: str, value: Any, timeout: int, description: str):
        """处理滚动到顶部操作"""
        self.base_page.scroll_to_top()
    
    def _handle_press_key(self, target: str, value: str, timeout: int, description: str):
        """处理按键操作"""
        self.base_page.press_key(value)
    
    def _handle_press_enter(self, target: str, value: Any, timeout: int, description: str):
        """处理按下Enter键操作"""
        self.base_page.press_enter()
    
    def _handle_press_tab(self, target: str, value: Any, timeout: int, description: str):
        """处理按下Tab键操作"""
        self.base_page.press_tab()
    
    def _handle_press_escape(self, target: str, value: Any, timeout: int, description: str):
        """处理按下Escape键操作"""
        self.base_page.press_escape()
    
    def _handle_type_text(self, target: str, value: str, timeout: int, description: str):
        """处理输入文本操作"""
        self.base_page.type_text(value)
    
    def _handle_refresh_page(self, target: str, value: Any, timeout: int, description: str):
        """处理刷新页面操作"""
        self.base_page.refresh_page()
    
    def _handle_go_back(self, target: str, value: Any, timeout: int, description: str):
        """处理返回操作"""
        self.base_page.go_back()
    
    def _handle_go_forward(self, target: str, value: Any, timeout: int, description: str):
        """处理前进操作"""
        self.base_page.go_forward()
    
    def _handle_take_screenshot(self, target: str, value: str, timeout: int, description: str):
        """处理截图操作"""
        self.base_page.take_screenshot(value)
    
    def _handle_execute_script(self, target: str, value: str, timeout: int, description: str):
        """处理执行脚本操作"""
        self.base_page.execute_script(value)
    
    def _handle_accept_dialog(self, target: str, value: Any, timeout: int, description: str):
        """处理接受对话框操作"""
        self.base_page.accept_dialog()
    
    def _handle_dismiss_dialog(self, target: str, value: Any, timeout: int, description: str):
        """处理取消对话框操作"""
        self.base_page.dismiss_dialog()
    
    def _handle_get_dialog_text(self, target: str, value: Any, timeout: int, description: str):
        """处理获取对话框文本操作"""
        text = self.base_page.get_dialog_text()
        self.logger.info(f"获取对话框文本: {text}")
        if value:
            Assertion.assert_equal(text, value, description)
    
    # 获取信息类操作
    def _handle_get_text(self, target: str, value: Any, timeout: int, description: str):
        """处理获取文本操作"""
        text = self.base_page.get_text(target)
        self.logger.info(f"获取文本 - 选择器: {target}, 文本: {text}")
        if value:
            Assertion.assert_equal(text, value, description)
    
    def _handle_get_attribute(self, target: str, value: str, timeout: int, description: str):
        """处理获取属性操作"""
        attribute = self.base_page.get_attribute(target, value)
        self.logger.info(f"获取属性 - 选择器: {target}, 属性: {attribute}")
        if value:
            Assertion.assert_equal(attribute, value, description)
    
    def _handle_get_value(self, target: str, value: Any, timeout: int, description: str):
        """处理获取值操作"""
        actual_value = self.base_page.get_value(target)
        self.logger.info(f"获取值 - 选择器: {target}, 值: {actual_value}")
        if value:
            Assertion.assert_equal(actual_value, value, description)
    
    def _handle_is_visible(self, target: str, value: Any, timeout: int, description: str):
        """处理断言元素可见操作"""
        actual = self.base_page.is_visible(target)
        self.logger.info(f"断言元素可见 - 选择器: {target}, 实际: {actual}")
        Assertion.assert_true(actual, description)
    
    def _handle_is_enabled(self, target: str, value: Any, timeout: int, description: str):
        """处理断言元素启用操作"""
        actual = self.base_page.is_enabled(target)
        self.logger.info(f"断言元素启用 - 选择器: {target}, 实际: {actual}")
        Assertion.assert_true(actual, description)
    
    def _handle_get_page_title(self, target: str, value: Any, timeout: int, description: str):
        """处理获取页面标题操作"""
        title = self.base_page.get_page_title()
        self.logger.info(f"获取页面标题: {title}")
        if value:
            Assertion.assert_equal(title, value, description)
    
    def _handle_get_current_url(self, target: str, value: Any, timeout: int, description: str):
        """处理获取当前URL操作"""
        url = self.base_page.get_current_url()
        self.logger.info(f"获取当前URL: {url}")
        if value:
            Assertion.assert_equal(url, value, description)
    
    # ==================== 断言处理器 ====================
    
    def _handle_assert_element_visible(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素可见"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_is_visible(locator, description, timeout)
    
    def _handle_assert_element_hidden(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素隐藏"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_is_hidden(locator, description, timeout)
    
    def _handle_assert_text_contains(self, target: str, expected: str, value: Any, timeout: int, description: str):
        """处理断言文本包含"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_text_contains(locator, expected, description, timeout)
    
    def _handle_assert_text_equals(self, target: str, expected: str, value: Any, timeout: int, description: str):
        """处理断言文本等于"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_text_equals(locator, expected, description, timeout)
    
    def _handle_assert_value_equals(self, target: str, expected: str, value: Any, timeout: int, description: str):
        """处理断言值等于"""
        locator = self.page.locator(target)
        self.page_assertion.assert_input_value_equals(locator, expected, description, timeout)
    
    def _handle_assert_url_contains(self, target: str, expected: str, value: Any, timeout: int, description: str):
        """处理断言URL包含"""
        self.page_assertion.assert_url_contains(expected, description, timeout)
    
    def _handle_assert_title_contains(self, target: str, expected: str, value: Any, timeout: int, description: str):
        """处理断言标题包含"""
        self.page_assertion.assert_title_contains(expected, description, timeout)
    
    def _handle_assert_element_enabled(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素启用"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_is_enabled(locator, description, timeout)
    
    def _handle_assert_element_disabled(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素禁用"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_is_disabled(locator, description, timeout)
    
    def _handle_assert_element_checked(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素已勾选"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_is_checked(locator, description, timeout)
    
    def _handle_assert_element_not_checked(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素未勾选"""
        locator = self.page.locator(target)
        self.page_assertion.assert_element_is_not_checked(locator, description, timeout)
    
    def _handle_assert_count(self, target: str, expected: int, value: Any, timeout: int, description: str):
        """处理断言元素数量"""
        locator = self.page.locator(target)
        self.page_assertion.assert_count_of_elements(locator, expected, description, timeout)
    
    def _handle_assert_equal(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言相等"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_equal(actual, expected, description)
    
    def _handle_assert_not_equal(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言不相等"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_not_equal(actual, expected, description)
    
    def _handle_assert_true(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言为真"""
        actual = self.base_page.is_visible(target) if target else value
        Assertion.assert_true(actual, description)
    
    def _handle_assert_false(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言为假"""
        actual = self.base_page.is_visible(target) if target else value
        Assertion.assert_false(actual, description)
    
    def _handle_assert_in(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言包含"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_in(actual, expected, description)
    
    def _handle_assert_not_in(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言不包含"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_not_in(actual, expected, description)
    
    def _handle_assert_is_none(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言为空"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_is_none(actual, description)
    
    def _handle_assert_is_not_none(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言不为空"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_is_not_none(actual, description)
    
    def _handle_assert_greater(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言大于"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_greater(actual, expected, description)
    
    def _handle_assert_less(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言小于"""
        actual = self.base_page.get_text(target) if target else value
        Assertion.assert_less(actual, expected, description)

    def _handle_assert_attribute_include(self, target: str, expected: Any, value: Any, timeout: int, description: str):
        """处理断言元素属性包含子串
        如果未明确给出属性名，则默认断言 class 属性包含 value
        """
        locator = self.page.locator(target)
        # 允许 expected/value 互换写法；若未提供属性名，默认 'class'
        # 情况1：expected 是属性名，value 是子串
        # 情况2：expected 为空，value 是子串（默认 class）
        # 情况3：expected 是子串（误放到 expected），value 为空（默认 class）
        if expected and value:
            attribute_name = str(expected)
            substring = str(value)
        elif expected and not value:
            attribute_name = 'class'
            substring = str(expected)
        else:
            attribute_name = 'class'
            substring = str(value) if value is not None else ''
        self.page_assertion.assert_element_attribute_contains(locator, attribute_name, substring, description, timeout)
    
    def execute_all_test_cases(self, yaml_file_path: str) -> Dict[str, Any]:
        """
        执行YAML文件中的所有测试用例
        
        Args:
            yaml_file_path: YAML文件路径
            
        Returns:
            测试结果字典，键为测试用例名，值为执行结果字典
        """
        try:
            test_data = self.load_test_case(yaml_file_path)
            results = {}
            
            for test_case_name in test_data.keys():
                self.logger.info(f"开始执行测试用例: {test_case_name}")
                result = self.execute_test_case(test_case_name, test_data)
                results[test_case_name] = result
                
                if result['success']:
                    self.logger.info(f"测试用例 {test_case_name} 执行成功")
                else:
                    self.logger.error(f"测试用例 {test_case_name} 执行失败: {result.get('error_message', '')}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"执行所有测试用例失败: {e}")
            return {}

    @staticmethod
    def resolve_selector(locations_dict: dict, path: str) -> str:
        """
        根据'页面.模块.元素'路径解析selector
        """
        keys = path.split('.')
        node = locations_dict
        for key in keys:
            node = node[key]
        return node

    def _execute_steps_with_details(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行步骤列表并返回详细信息
        
        Args:
            steps: 步骤列表
            
        Returns:
            包含执行结果的字典
        """
        start_time = time.time()
        test_case_result = {
            'case_name': 'single_case',
            'input_value': '',
            'success': True,
            'steps': [],
            'error_message': '',
            'duration_ms': 0
        }
        
        for i, step in enumerate(steps, 1):
            step_start_time = time.time()
            step_result = {
                'step_num': i,
                'action': '',
                'selector': '',
                'value': None,
                'expected': None,
                'success': False,
                'error_message': '',
                'duration_ms': 0
            }
            
            try:
                if not isinstance(step, dict):
                    step_result['error_message'] = f"步骤格式错误: {step}"
                    test_case_result['steps'].append(step_result)
                    test_case_result['success'] = False
                    test_case_result['error_message'] = step_result['error_message']
                    break
                
                # 兼容 input: xxx + value: yyy 这种格式
                if len(step) > 1:
                    action = list(step.keys())[0]
                    params = {k: v for k, v in step.items()}
                else:
                    action, params = list(step.items())[0]

                # 处理参数 - 修复wait步骤的参数解析
                if isinstance(params, dict):
                    # 对于input操作，优先从selector字段获取元素路径
                    if action == 'input':
                        element_path = params.get('selector') or params.get('element') or params.get('target') or params.get('locator')
                    elif action == 'assert':
                        # 对于断言操作，从selector字段获取元素路径
                        element_path = params.get('selector') or params.get('element') or params.get('target') or params.get('locator')
                    else:
                        element_path = params.get(action) or params.get('element') or params.get('target') or params.get('locator')
                    value = params.get('value')
                    expected = params.get('expected')
                else:
                    # 对于非字典参数（如 wait: 1000）
                    if action == 'wait':
                        # wait步骤特殊处理：params就是等待时间
                        element_path = None
                        value = params
                        expected = None
                    else:
                        element_path = params
                        value = step.get('value')
                        expected = step.get('expected')
                
                # 设置步骤结果基本信息
                step_result['action'] = action
                step_result['value'] = value
                step_result['expected'] = expected
                
                # 调试日志
                self.logger.debug(f"步骤 {i}: action={action}, element_path={element_path}, value={value}")
                
                # 判断是否为元素路径
                def is_element_path(path: str) -> bool:
                    return isinstance(path, str) and 'Path' in path

                selector = None
                if element_path and is_element_path(element_path):
                    try:
                        self.logger.info(f"步骤 {i}: 解析Path路径: {element_path}")
                        t1 = re.search(r'Path\((.*?)\)', element_path)
                        tmp_path = t1.group(1) if t1 else None
                        self.logger.info(f"步骤 {i}: 提取的路径: {tmp_path}")
                        
                        # 支持 .f(...) 形式动态传参
                        t2 = re.search(r'\.f\((.*?)\)', element_path)
                        tmp_value = t2.group(1) if t2 else None
                        if tmp_value:
                            self.logger.info(f"步骤 {i}: 动态参数: {tmp_value}")

                        selector = self.resolve_selector(self.locations_dict, tmp_path)
                        self.logger.info(f"步骤 {i}: 解析后的selector: {selector}")
                        
                        if tmp_value is not None:
                            selector = selector.format(tmp_value)
                            self.logger.info(f"步骤 {i}: 格式化后的selector: {selector}")
                    except Exception as e:
                        step_result['error_message'] = f"元素路径解析失败: {element_path}, 错误: {e}"
                        step_result['duration_ms'] = (time.time() - step_start_time) * 1000
                        test_case_result['steps'].append(step_result)
                        test_case_result['success'] = False
                        test_case_result['error_message'] = step_result['error_message']
                        break
                elif element_path:
                    # 对于非Path格式的元素路径，直接使用
                    selector = element_path
                    self.logger.info(f"步骤 {i}: 直接使用element_path作为selector: {selector}")
                else:
                    self.logger.warning(f"步骤 {i}: element_path为空，action={action}")
                
                step_result['selector'] = selector
                self.logger.info(f"步骤 {i}: 最终selector: {selector}")
                
                # 检查selector是否为空
                if action in ['click', 'hover', 'input', 'clear_and_input', 'select', 'select_option_by_label', 'check', 'uncheck', 'upload', 'double_click', 'right_click', 'wait_for_element', 'wait_for_element_hidden', 'scroll_to_element', 'execute_script', 'get_text', 'get_attribute', 'get_value', 'is_visible', 'is_enabled', 'assert'] and not selector:
                    step_result['error_message'] = f"步骤 {i}: {action} 操作的selector为空，element_path={element_path}"
                    step_result['duration_ms'] = (time.time() - step_start_time) * 1000
                    test_case_result['steps'].append(step_result)
                    test_case_result['success'] = False
                    test_case_result['error_message'] = step_result['error_message']
                    break
                
                # 使用allure.step装饰器记录每个步骤
                step_description = self._get_step_description(action, selector, value, expected, i)
                
                @allure.step(step_description)
                def execute_single_step():
                    return self._execute_single_step(action, selector, value, expected, i)
                
                # 执行步骤
                if execute_single_step():
                    step_result['success'] = True
                else:
                    step_result['error_message'] = f"步骤 {i} 执行失败"
                    test_case_result['success'] = False
                    test_case_result['error_message'] = step_result['error_message']
                
            except Exception as e:
                step_result['error_message'] = f"步骤 {i} 执行异常: {e}"
                test_case_result['success'] = False
                test_case_result['error_message'] = step_result['error_message']
            
            # 计算步骤执行时长
            step_result['duration_ms'] = (time.time() - step_start_time) * 1000
            test_case_result['steps'].append(step_result)
            
            # 如果步骤失败，停止执行
            if not step_result['success']:
                break
        
        # 计算总执行时长
        test_case_result['duration_ms'] = (time.time() - start_time) * 1000
        
        return {
            'test_cases': [test_case_result],
            'error_message': test_case_result['error_message']
        }

    def _wait_for_element_content_stable(self, selector: str, expected_content: str = None, timeout: int = None, check_interval: float = None) -> bool:
        """
        智能等待元素内容稳定
        
        Args:
            selector: 元素选择器
            expected_content: 期望的内容（可选，如果提供则等待内容匹配）
            timeout: 超时时间（毫秒），如果为None则使用配置值
            check_interval: 检查间隔（秒），如果为None则使用配置值
            
        Returns:
            是否成功等待到内容稳定
        """
        if not self.enable_smart_wait:
            self.logger.info("智能等待已禁用，跳过等待")
            return True
            
        timeout = timeout or self.smart_wait_timeout
        check_interval = check_interval or self.smart_wait_interval
        
        start_time = time.time()
        last_content = None
        stable_count = 0
        required_stable_count = 2  # 需要连续2次内容相同才认为稳定
        
        self.logger.info(f"开始等待元素内容稳定: {selector}, 超时: {timeout}ms, 检查间隔: {check_interval}s")
        
        while (time.time() - start_time) * 1000 < timeout:
            try:
                current_content = self.base_page.get_text(selector)
                
                # 如果提供了期望内容，检查是否匹配
                if expected_content and expected_content in current_content:
                    self.logger.info(f"元素内容已匹配期望值: {expected_content}")
                    return True
                
                # 检查内容是否稳定（连续两次相同）
                if current_content == last_content:
                    stable_count += 1
                    if stable_count >= required_stable_count:
                        self.logger.info(f"元素内容已稳定: {current_content}")
                        return True
                else:
                    stable_count = 0
                    last_content = current_content
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.warning(f"等待元素内容稳定时出现异常: {e}")
                time.sleep(check_interval)
        
        self.logger.warning(f"等待元素内容稳定超时: {selector}")
        return False

    def configure_smart_wait(self, enable: bool = None, timeout: int = None, interval: float = None) -> None:
        """
        配置智能等待参数
        
        Args:
            enable: 是否启用智能等待
            timeout: 超时时间（毫秒）
            interval: 检查间隔（秒）
        """
        if enable is not None:
            self.enable_smart_wait = enable
            self.logger.info(f"智能等待已{'启用' if enable else '禁用'}")
        
        if timeout is not None:
            self.smart_wait_timeout = timeout
            self.logger.info(f"智能等待超时时间设置为: {timeout}ms")
        
        if interval is not None:
            self.smart_wait_interval = interval
            self.logger.info(f"智能等待检查间隔设置为: {interval}s")
    
    def get_smart_wait_config(self) -> dict:
        """
        获取智能等待配置
        
        Returns:
            智能等待配置字典
        """
        return {
            'enable_smart_wait': self.enable_smart_wait,
            'smart_wait_timeout': self.smart_wait_timeout,
            'smart_wait_interval': self.smart_wait_interval
        }


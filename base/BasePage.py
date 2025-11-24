"""
BasePage类 - Playwright UI自动化基础页面类
提供常见的UI自动化通用功能，其他页面可以继承并使用
"""

from playwright.sync_api import Page, expect, TimeoutError
from typing import Optional, Union, List
import time
import logging


class BasePage:
    """基础页面类，提供通用的UI自动化功能"""
    
    def __init__(self, page: Page):
        """
        初始化BasePage
        
        Args:
            page: Playwright的Page对象
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
    
    # ==================== 基础操作方法 ====================
    
    def navigate_to(self, url: str) -> None:
        """
        导航到指定URL
        
        Args:
            url: 目标URL
        """
        self.logger.info(f"导航到页面: {url}")
        self.page.goto(url)
    
    def click(self, selector: str, timeout: int = 30000) -> None:
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"点击元素: {selector}")
        self.page.click(selector, timeout=timeout)
    
    def input_text(self, selector: str, text: str, timeout: int = 30000) -> None:
        """
        在输入框中输入文本
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"在元素 {selector} 中输入文本: {text}")
        self.page.fill(selector, text, timeout=timeout)
    
    def clear_and_input(self, selector: str, text: str, timeout: int = 30000) -> None:
        """
        清空输入框并输入文本
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"清空并输入文本到元素 {selector}: {text}")
        self.page.fill(selector, "", timeout=timeout)
        self.page.fill(selector, text, timeout=timeout)
    
    def select_option(self, selector: str, value: str, timeout: int = 30000) -> None:
        """
        选择下拉框选项
        
        Args:
            selector: 下拉框选择器
            value: 要选择的选项值
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"选择下拉框 {selector} 的选项: {value}")
        self.page.select_option(selector, value, timeout=timeout)
    
    def select_option_by_label(self, selector: str, label: str, timeout: int = 30000) -> None:
        """
        通过标签选择下拉框选项
        
        Args:
            selector: 下拉框选择器
            label: 要选择的选项标签
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"通过标签选择下拉框 {selector} 的选项: {label}")
        self.page.select_option(selector, label=label, timeout=timeout)
    
    def check_checkbox(self, selector: str, timeout: int = 30000) -> None:
        """
        勾选复选框
        
        Args:
            selector: 复选框选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"勾选复选框: {selector}")
        self.page.check(selector, timeout=timeout)
    
    def uncheck_checkbox(self, selector: str, timeout: int = 30000) -> None:
        """
        取消勾选复选框
        
        Args:
            selector: 复选框选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"取消勾选复选框: {selector}")
        self.page.uncheck(selector, timeout=timeout)
    
    def upload_file(self, selector: str, file_path: str, timeout: int = 30000) -> None:
        """
        上传文件
        
        Args:
            selector: 文件输入框选择器
            file_path: 文件路径
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"上传文件到 {selector}: {file_path}")
        self.page.set_input_files(selector, file_path, timeout=timeout)
    
    def hover(self, selector: str, timeout: int = 30000) -> None:
        """
        鼠标悬停
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"鼠标悬停在元素: {selector}")
        self.page.hover(selector, timeout=timeout)
    
    def double_click(self, selector: str, timeout: int = 30000) -> None:
        """
        双击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"双击元素: {selector}")
        self.page.dblclick(selector, timeout=timeout)
    
    def right_click(self, selector: str, timeout: int = 30000) -> None:
        """
        右键点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"右键点击元素: {selector}")
        self.page.click(selector, button="right", timeout=timeout)
    
    # ==================== 等待方法 ====================
    
    def wait_for_element(self, selector: str, timeout: int = 30000) -> None:
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"等待元素出现: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def wait_for_element_hidden(self, selector: str, timeout: int = 30000) -> None:
        """
        等待元素隐藏
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"等待元素隐藏: {selector}")
        self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
    
    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000) -> None:
        """
        等待页面加载状态
        
        Args:
            state: 加载状态 ("load", "domcontentloaded", "networkidle")
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"等待页面加载状态: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)
    
    def wait_for_time(self, seconds: float) -> None:
        """
        等待指定时间
        
        Args:
            seconds: 等待秒数
        """
        self.logger.info(f"等待 {seconds} 秒")
        time.sleep(seconds)
    
    # ==================== 获取元素信息 ====================
    
    def get_text(self, selector: str, timeout: int = 30000) -> str:
        """
        获取元素文本内容
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            元素文本内容
        """
        self.logger.info(f"获取元素文本: {selector}")
        return self.page.text_content(selector, timeout=timeout)
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = 30000) -> Optional[str]:
        """
        获取元素属性值
        
        Args:
            selector: 元素选择器
            attribute: 属性名
            timeout: 超时时间（毫秒）
            
        Returns:
            属性值
        """
        self.logger.info(f"获取元素 {selector} 的属性 {attribute}")
        return self.page.get_attribute(selector, attribute, timeout=timeout)

    def get_locator_attribute(self, selector: str, attribute: str, timeout: int = 30000) -> Optional[str]:
        """
        通过 Locator API 获取元素属性值（支持超时）
        """
        self.logger.info(f"通过Locator获取元素 {selector} 的属性 {attribute}")
        locator = self.page.locator(selector)
        return locator.get_attribute(attribute, timeout=timeout)
    
    def get_value(self, selector: str, timeout: int = 30000) -> str:
        """
        获取输入框的值
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            输入框的值
        """
        self.logger.info(f"获取输入框的值: {selector}")
        return self.page.input_value(selector, timeout=timeout)
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            是否可见
        """
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except TimeoutError:
            return False
    
    def is_enabled(self, selector: str, timeout: int = 5000) -> bool:
        """
        检查元素是否启用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            是否启用
        """
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            return element.is_enabled()
        except TimeoutError:
            return False
    
    # ==================== 断言方法 ====================
    
    def assert_element_visible(self, selector: str, timeout: int = 30000) -> None:
        """
        断言元素可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"断言元素可见: {selector}")
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
    
    def assert_element_hidden(self, selector: str, timeout: int = 30000) -> None:
        """
        断言元素隐藏
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"断言元素隐藏: {selector}")
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)
    
    def assert_text_contains(self, selector: str, text: str, timeout: int = 30000) -> None:
        """
        断言元素文本包含指定内容
        
        Args:
            selector: 元素选择器
            text: 期望包含的文本
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"断言元素 {selector} 包含文本: {text}")
        expect(self.page.locator(selector)).to_contain_text(text, timeout=timeout)
    
    def assert_text_equals(self, selector: str, text: str, timeout: int = 30000) -> None:
        """
        断言元素文本等于指定内容
        
        Args:
            selector: 元素选择器
            text: 期望的文本
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"断言元素 {selector} 文本等于: {text}")
        expect(self.page.locator(selector)).to_have_text(text, timeout=timeout)
    
    def assert_value_equals(self, selector: str, value: str, timeout: int = 30000) -> None:
        """
        断言输入框的值等于指定内容
        
        Args:
            selector: 元素选择器
            value: 期望的值
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"断言元素 {selector} 的值等于: {value}")
        expect(self.page.locator(selector)).to_have_value(value, timeout=timeout)
    
    def assert_url_contains(self, url_part: str) -> None:
        """
        断言当前URL包含指定部分
        
        Args:
            url_part: URL的一部分
        """
        self.logger.info(f"断言URL包含: {url_part}")
        expect(self.page).to_have_url(f"**{url_part}**")
    
    def assert_title_contains(self, title_part: str) -> None:
        """
        断言页面标题包含指定部分
        
        Args:
            title_part: 标题的一部分
        """
        self.logger.info(f"断言页面标题包含: {title_part}")
        expect(self.page).to_have_title(f"**{title_part}**")
    
    # ==================== 键盘操作 ====================
    
    def press_key(self, key: str) -> None:
        """
        按下键盘按键
        
        Args:
            key: 按键名称
        """
        self.logger.info(f"按下按键: {key}")
        self.page.keyboard.press(key)
    
    def type_text(self, text: str) -> None:
        """
        输入文本（当前焦点位置）
        
        Args:
            text: 要输入的文本
        """
        self.logger.info(f"输入文本: {text}")
        self.page.keyboard.type(text)
    
    def press_enter(self) -> None:
        """按下回车键"""
        self.press_key("Enter")
    
    def press_tab(self) -> None:
        """按下Tab键"""
        self.press_key("Tab")
    
    def press_escape(self) -> None:
        """按下Escape键"""
        self.press_key("Escape")
    
    # ==================== 页面操作 ====================
    
    def refresh_page(self) -> None:
        """刷新页面"""
        self.logger.info("刷新页面")
        self.page.reload()
    
    def go_back(self) -> None:
        """返回上一页"""
        self.logger.info("返回上一页")
        self.page.go_back()
    
    def go_forward(self) -> None:
        """前进到下一页"""
        self.logger.info("前进到下一页")
        self.page.go_forward()
    
    def take_screenshot(self, path: str) -> None:
        """
        截图
        
        Args:
            path: 截图保存路径
        """
        self.logger.info(f"截图保存到: {path}")
        self.page.screenshot(path=path)
    
    def get_page_title(self) -> str:
        """
        获取页面标题
        
        Returns:
            页面标题
        """
        return self.page.title()
    
    def get_current_url(self) -> str:
        """
        获取当前URL
        
        Returns:
            当前URL
        """
        return self.page.url
    
    # ==================== 高级操作方法 ====================
    
    def scroll_to_element(self, selector: str, timeout: int = 30000) -> None:
        """
        滚动到指定元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.logger.info(f"滚动到元素: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed(timeout=timeout)
    
    def scroll_to_bottom(self) -> None:
        """滚动到页面底部"""
        self.logger.info("滚动到页面底部")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    def scroll_to_top(self) -> None:
        """滚动到页面顶部"""
        self.logger.info("滚动到页面顶部")
        self.page.evaluate("window.scrollTo(0, 0)")
    
    def execute_script(self, script: str) -> any:
        """
        执行JavaScript脚本
        
        Args:
            script: JavaScript脚本
            
        Returns:
            脚本执行结果
        """
        self.logger.info(f"执行JavaScript脚本: {script}")
        return self.page.evaluate(script)
    
    def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """
        等待网络空闲
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.logger.info("等待网络空闲")
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def accept_dialog(self) -> None:
        """接受对话框"""
        self.logger.info("接受对话框")
        self.page.on("dialog", lambda dialog: dialog.accept())
    
    def dismiss_dialog(self) -> None:
        """取消对话框"""
        self.logger.info("取消对话框")
        self.page.on("dialog", lambda dialog: dialog.dismiss())
    
    def get_dialog_text(self) -> str:
        """
        获取对话框文本
        
        Returns:
            对话框文本
        """
        dialog_text = []
        self.page.on("dialog", lambda dialog: dialog_text.append(dialog.message))
        return dialog_text[0] if dialog_text else ""

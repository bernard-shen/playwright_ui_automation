import pytest
from playwright.sync_api import Page, Locator, expect


class Assertion:
    """通用断言类"""

    @staticmethod
    def assert_equal(actual, expected, message=""):
        try:
            assert actual == expected
        except AssertionError:
            pytest.fail(f"{message} - 期望值: '{expected}', 实际值: '{actual}'")

    @staticmethod
    def assert_not_equal(actual, expected, message=""):
        try:
            assert actual != expected
        except AssertionError:
            pytest.fail(f"{message} - 期望值不为: '{expected}', 实际值: '{actual}'")

    @staticmethod
    def assert_true(expr, message=""):
        try:
            assert expr
        except AssertionError:
            pytest.fail(f"{message} - 期望表达式为 True, 实际为 False")

    @staticmethod
    def assert_false(expr, message=""):
        try:
            assert not expr
        except AssertionError:
            pytest.fail(f"{message} - 期望表达式为 False, 实际为 True")

    @staticmethod
    def assert_in(member, container, message=""):
        try:
            assert member in container
        except AssertionError:
            pytest.fail(f"{message} - 期望 '{member}' 在 '{container}' 中, 但实际不在")

    @staticmethod
    def assert_not_in(member, container, message=""):
        try:
            assert member not in container
        except AssertionError:
            pytest.fail(f"{message} - 期望 '{member}' 不在 '{container}' 中, 但实际在")

    @staticmethod
    def assert_is_none(expr, message=""):
        try:
            assert expr is None
        except AssertionError:
            pytest.fail(f"{message} - 期望为 None, 实际为 '{expr}'")

    @staticmethod
    def assert_is_not_none(expr, message=""):
        try:
            assert expr is not None
        except AssertionError:
            pytest.fail(f"{message} - 期望不为 None, 但实际为 None")

    @staticmethod
    def assert_greater(a, b, message=""):
        try:
            assert a > b
        except AssertionError:
            pytest.fail(f"{message} - 期望 {a} > {b}, 但实际不成立")

    @staticmethod
    def assert_less(a, b, message=""):
        try:
            assert a < b
        except AssertionError:
            pytest.fail(f"{message} - 期望 {a} < {b}, 但实际不成立")

    @staticmethod
    def assert_is_instance(obj, cls, message=""):
        """
        断言对象是指定类的实例
        """
        try:
            assert isinstance(obj, cls)
        except AssertionError:
            pytest.fail(f"{message} - 期望对象是 {cls.__name__} 的实例, 实际是 {type(obj).__name__}")

    @staticmethod
    def assert_not_is_instance(obj, cls, message=""):
        try:
            assert not isinstance(obj, cls)
        except AssertionError:
            pytest.fail(f"{message} - 期望对象不是 {cls.__name__} 的实例, 但实际是")


class PageAssertion:
    """页面断言类，基于Playwright的expect"""

    def __init__(self, page: Page):
        self.page = page

    def assert_url_contains(self, substring: str, message="", timeout=5000):
        try:
            expect(self.page).to_have_url(f".*{substring}.*", timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_url_equals(self, url: str, message="", timeout=5000):
        try:
            expect(self.page).to_have_url(url, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_title_contains(self, substring: str, message="", timeout=5000):
        try:
            expect(self.page).to_have_title(f".*{substring}.*", timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_title_equals(self, title: str, message="", timeout=5000):
        try:
            expect(self.page).to_have_title(title, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_visible(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).to_be_visible(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_hidden(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).to_be_hidden(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_text_equals(self, locator: Locator, text: str, message="", timeout=5000):
        try:
            expect(locator).to_have_text(text, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_text_contains(self, locator: Locator, text: str, message="", timeout=5000):
        try:
            expect(locator).to_contain_text(text, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_has_attribute(self, locator: Locator, attribute: str, value, message="", timeout=5000):
        try:
            expect(locator).to_have_attribute(attribute, value, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_attribute_contains(self, locator: Locator, attribute: str = 'class', substring: str = '', message="", timeout=5000):
        """
        断言元素指定属性的值包含给定子串；attribute 默认 'class'
        """
        actual = None
        try:
            actual = locator.get_attribute(attribute, timeout=timeout)
            assert actual is not None and substring in actual
        except AssertionError:
            pytest.fail(f"{message} - 期望属性 {attribute} 包含 '{substring}', 实际: '{actual}'")

    def assert_element_is_enabled(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).to_be_enabled(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_disabled(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).to_be_disabled(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_count_of_elements(self, locator: Locator, count: int, message="", timeout=5000):
        try:
            expect(locator).to_have_count(count, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_screenshot(self, locator: Locator = None, name: str = "screenshot.png", threshold: float = 0.1, max_diff_pixels: int = None, message=""):

        target = self.page if locator is None else locator
        try:
            expect(target).to_have_screenshot(name, threshold=threshold, max_diff_pixels=max_diff_pixels)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_input_value_equals(self, locator: Locator, value: str, message="", timeout=5000):

        try:
            expect(locator).to_have_value(value, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_checked(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).to_be_checked(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_not_checked(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).not_to_be_checked(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_editable(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).to_be_editable(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

    def assert_element_is_not_editable(self, locator: Locator, message="", timeout=5000):
        try:
            expect(locator).not_to_be_editable(timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")


    def assert_hover_and_text_equals(self, hover_locator: Locator, text_locator: Locator, expected_text: str, message="", timeout=5000):
        try:
            hover_locator.hover(timeout=timeout)
            expect(text_locator).to_have_text(expected_text, timeout=timeout)
        except AssertionError as e:
            pytest.fail(f"{message} - {e}")

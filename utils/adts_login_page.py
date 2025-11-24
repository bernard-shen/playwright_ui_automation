import time

from playwright.sync_api import Page
from utils.config_reader import WebUIConfReader


class LoginPage:
    def __init__(self, base_url, page: Page):
        self.base_url = base_url
        self.page = page
        self.pages = (WebUIConfReader().config)["pages"]
        self.s = lambda css: self.page.query_selector(css)

    def login(self, username, password):
        self.page.goto(self.base_url)
        time.sleep(1)
        self.page.locator('input[type="text"]').first.fill(username)
        self.page.locator('input[type="password"]').fill(password)
        self.page.locator('input[type="password"]').press('Enter')
        time.sleep(1)
        return self.page 
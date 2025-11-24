
import pytest
import time
import random
from utils.config_reader import WebUIConfReader, ConfigReader
from utils.adts_login_page import LoginPage



@pytest.fixture(scope='session')
def pages():
    return WebUIConfReader().config['pages']

@pytest.fixture(autouse=True)
def login(page, pages):
    username = ConfigReader().get_ini_conf(file_path='pwd.conf', section='EIIR', key='username')
    password = ConfigReader().get_ini_conf(file_path='pwd.conf', section='EIIR', key='password')
    LoginPage(pages['uuam_to_adts'], page).login(username, password)
    time.sleep(1)






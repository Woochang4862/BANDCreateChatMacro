import urllib
import time
from selenium import webdriver
from selenium.webdriver.support.ui import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pyperclip
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

chromedriver_autoinstaller.install()
co = Options()
co.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=co)

'''
디버깅 변수
'''
id = 'chad0706'
pw = 'asdf0706'
url = 'https://band.us/band/83539360' #홍보하고 싶은 밴드

def login(id,pw):
    driver.find_element_by_class_name('uBtn.-icoType.-naver.externalLogin').click()

    """
    네이버 로그인
    """
    user_id = driver.find_element_by_id("id")
    password = driver.find_element_by_id("pw")
    time.sleep(1)

    user_id.click()
    pyperclip.copy(id)
    user_id.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    password.click()
    pyperclip.copy(pw)
    password.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    password.submit()


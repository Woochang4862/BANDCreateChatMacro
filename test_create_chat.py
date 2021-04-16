import time
from selenium import webdriver
from selenium.webdriver.support.ui import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pyperclip
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

chromedriver_autoinstaller.install(cwd=True)
co = Options()
co.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=co)

'''
디버깅 변수
'''
id = 'chad0706'
pw = 'asdf0706'
profile_image = r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg'
chat_name = '테스트'

def findElementByXpath(xpath):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except TimeoutException as e:
        return

def login(id,pw):
    login_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="header"]/div/div/a[2]'))
    )
    login_btn.click()
    naver_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'uBtn.-icoType.-naver.externalLogin'))
    )
    naver_btn.click()

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
    time.sleep(3)

driver.get('https://band.us/home')

#login(id, pw)

driver.get('https://band.us/band/55170325') # 홍보할 밴드 링크

try:
    new_chat_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="bannerInner"]/div/section[1]/div[1]/button'))
    )
    new_chat_btn.click()
    
    check_btns = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div/div/div[3]/ul/li[*]/label/span[3]/span/input'))
    )
    for check_btn in check_btns:
        check_btn.click()
    driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/section/div/footer/button[2]').click()
    
    open_chat = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div[3]/button[2]'))
    )
    open_chat.click()

    driver.switch_to.window(driver.window_handles[1])

    option_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/header/button[2]'))
    )
    option_btn.click()

    setting_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div/section/div/footer/div/button[1]'))
    )
    setting_btn.click()

    edit_info_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/div/div/div/button'))
    )
    edit_info_btn.click()

    edit_info_image_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/div/div[1]/div/label/input'))
    )
    edit_info_image_input.send_keys(profile_image)

    edit_info_image_done_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[4]/section/div/footer/button[2]'))
    )
    edit_info_image_done_btn.click()

    edit_info_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[4]/div/div[3]/div/section/div/div/div[2]/input'))
    )
    edit_info_name_input.clear()
    edit_info_name_input.send_keys(chat_name)

    edit_info_done_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/footer/button[1]'))
    )
    edit_info_done_btn.click()

    message_period_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[2]/a'))
    )
    message_period_btn.click()

    message_preiod_min_radio = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ex_radio_min"]'))
    )
    message_preiod_min_radio.click()

    message_period_done_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/footer/div/button'))
    )
    message_period_done_btn.click()

    driver.switch_to_alert().accept()

    setting_close_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/footer/button'))
    )
    setting_close_btn.click()

except NoSuchElementException as e:
    print('Error: ', e)
except NoAlertPresentException as e:
    print('Error: ', e)
finally:
    driver.quit()




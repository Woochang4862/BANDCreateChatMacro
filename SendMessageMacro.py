import time
from selenium.webdriver.support.ui import *
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, NoAlertPresentException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from DriverProvider import *
from LoginMacro import *

def sendMessage(driver, url, text, onlyAction=False):
    if not onlyAction:
        driver.get(url)

    try:
        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/div[1]/textarea'))
        )
        textarea.send_keys(text)

        send_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/section/div[2]/div[2]/button'))
        )
        send_btn.click()
        
        
    except NoSuchElementException as e:
        print('Error: ', e)

driver = setup_driver()
result = login(driver, 'chad0706','asdf0706')
if result == LOGIN_SUCCESS or result == LOGGED_IN:
    sendMessage(driver, 'https://band.us/band/83546235/chat/CYc6J0', time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
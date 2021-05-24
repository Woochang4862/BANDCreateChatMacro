import time
import logging
from selenium.webdriver.support.ui import *
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, NoAlertPresentException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from DriverProvider import *
from LoginMacro import *

from PyQt5.QtCore import *

logger = logging.getLogger()
FORMAT = "[%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)

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

def getChatUrls(driver, url, keyword, onlyAction=False):
    if not onlyAction:
        driver.get(url)

    time.sleep(3)

    chats = driver.find_elements_by_xpath('//ul[@class="chat"]/li[*]')

    len_of_chats = len(chats)

    #print(len_of_chats, chats[0].get_attribute('innerHTML'))

    result = []

    if len_of_chats > 1:
        i = 1
        while True:
            done = False
            err_cnt = 0
            timeout = False
            while not done:
                try:
                    chat = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f'//ul[@class="chat"]/li[{i}]/a'))
                    )
                
                    chat_title = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f'//ul[@class="chat"]/li[{i}]/a/span[2]/strong'))
                    ).text
                    chat.click()
                    done = True
                except TimeoutException:
                    timeout = True
                    break
                except Exception:
                    err_cnt+=1
                    logger.exception(f"채팅방 찾는데 문제발생 {err_cnt}")

            if timeout:
                break
            driver.switch_to.window(driver.window_handles[1])
            if keyword in chat_title:
                url = driver.current_url
                result.append((chat_title,url))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            i+=1

    elif len_of_chats == 1:
        try:
            chat = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//ul[@class="chat"]/li/a'))
            )
            chat_title = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//ul[@class="chat"]/li/a/span[2]/strong'))
            ).text
            chat.click()
            driver.switch_to.window(driver.window_handles[1])
            if keyword in chat_title:
                url = driver.current_url
                result.append((chat_title,url))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception:
            logger.exception("채팅방 찾는데 문제발생")

    return result

def getBandUrls(driver, onlyAction=False):
    if not onlyAction:
        driver.get('https://band.us/')

    result = []

    i = 1
    while True:
        try:
            item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="content"]/div/section/div[2]/div/div/ul/li[{i}]'))
            )
        except:
            break
        
        if item.get_attribute('data-item-type') == 'band':
            title = driver.find_element_by_xpath(f'//*[@id="content"]/div/section/div[2]/div/div/ul/li[{i}]/div/div/a/div[2]/p').text
            item.click()
            url = driver.current_url
            result.append((title, url))
            driver.get('https://band.us/')
        i+=1
    
    return result

# driver = setup_driver()
# result = loginWithPhone(driver, '01038554671','asdf0706')
# if result == LOGIN_SUCCESS or result == LOGGED_IN:
#     # chat_urls = getChatUrls(driver, 'https://band.us/band/60518206', '공부')
#     # print(chat_urls)
#     start = time.time()
#     logging.info('밴드 주소 가져오는 중...')
#     bands = getBandUrls(driver)
#     logging.info(f'가져온 밴드 주소 개수 : "{len(bands)}"')
#     keyword = '마카롱'
#     logging.info(f'"{keyword}"이/가 들어간 채팅 주소 가져오는 중...')
#     chats = []
#     for title, url in bands:
#         _chats = getChatUrls(driver, url, keyword)
#         for chat in _chats:
#             chats.append((title, chat[0], chat[1]))
#     logging.info(f'가져온 채팅 주소 개수 : "{len(chats)}"')
#     for band_title, chat_title, chat_url in chats:
#         sendMessage(driver, chat_url, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
#     logging.info(f'실행시간 : {time.time()-start}초')
# driver.close()

class GetChatThread(QThread):
    
    on_finished_get_chat = pyqtSignal(list)
    on_error_get_chat = pyqtSignal()

    id = ''
    pw = ''
    keyword = ''

    def __init__(self, parent=None):
        super().__init__()

    def run(self):
        self.driver = setup_driver()
        result = loginWithPhone(self.driver, self.id,self.pw)
        if result == LOGIN_SUCCESS or result == LOGGED_IN:
            start = time.time()
            logging.info('밴드 주소 가져오는 중...')
            bands = getBandUrls(self.driver)
            logging.info(f'가져온 밴드 주소 개수 : "{len(bands)}"')
            logging.info(f'"{self.keyword}"이/가 들어간 채팅 주소 가져오는 중...')
            chats = []
            for title, url in bands:
                _chats = getChatUrls(self.driver, url, self.keyword)
                for chat in _chats:
                    chats.append((title, chat[0], chat[1], self.id))
            logging.info(f'가져온 채팅 주소 개수 : "{len(chats)}"')
            logging.info(f'실행시간 : {time.time()-start}초')
            self.on_finished_get_chat.emit(chats)
        elif result == LOGIN_ERROR:
            self.on_error_get_chat.emit()
        self.driver.close() # TODO : 여기에서 취소 누르면 죽음

    def stop(self):
        self.driver.close()
        self.quit()
        self.wait(5000) #5000ms = 5s

class SendMessageThread(QThread):

    id = ''
    pw = ''
    chat_urls = []
    content = ''
    on_finished_send_msg = pyqtSignal()
    on_error_send_msg = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()

    def run(self):
        self.driver = setup_driver()
        result = loginWithPhone(self.driver, self.id,self.pw)
        if result == LOGIN_SUCCESS or result == LOGGED_IN:
            start = time.time()
            logging.info('채팅 보내는 중...')
            for chat_url in self.chat_urls:
                sendMessage(self.driver, chat_url, self.content)
            logging.info(f'실행시간 : {time.time()-start}초')
            self.on_finished_send_msg.emit()
        elif result == LOGIN_ERROR:
            self.on_error_send_msg.emit()
        self.driver.close()

    def stop(self):
        self.driver.close()
        self.quit()
        self.wait(5000) #5000ms = 5s

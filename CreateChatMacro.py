from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import time
from selenium import webdriver
from selenium.webdriver.support.ui import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pyperclip
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import subprocess
from selenium.webdriver.common.action_chains import ActionChains

MAX_MEMBER_COUNT = 100

profile_image = r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg'
chat_name = '테스트'

def open_chrome_with_debug_mode(path='C:\Program Files\Google\Chrome\Application\chrome.exe'):
    result = subprocess.Popen(f'{path} --remote-debugging-port=9222 --user-data-dir=C:/ChromeTEMP --daemon')

def setup_driver():
    global driver
    chromedriver_autoinstaller.install(cwd=True)
    co = Options()
    co.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    driver = webdriver.Chrome(options=co)

class ValidateAccountThread(QThread):
        state_logged_in = pyqtSignal()
        state_login_success = pyqtSignal()
        state_login_fail = pyqtSignal()
        def __init__(self, id, pw, parent=None):
            super().__init__()
            self.id = id
            self.pw = pw
 
        def run(self):
            result = False
            driver.get('https://band.us/home')
            
            time.sleep(3)

            if driver.current_url != 'https://band.us/home': # 로그인이 된 상태
                self.state_logged_in.emit()
            else:
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
                pyperclip.copy(self.id)
                user_id.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)

                password.click()
                pyperclip.copy(self.pw)
                password.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)

                password.submit()
                
                time.sleep(3)

                if driver.current_url == 'https://band.us/':
                    result = True
            
                if result: # 올바른 아이디
                    self.state_login_success.emit()
                else: # 올바르지 못한 아이디
                    self.state_login_fail.emit()

keywords = [
    '강','고','공','곽','구','권','금','기','김','나',
    '남','노','도','라','류','마','맹','문','민','박',
    '반','방','배','백','사','서','설','성','소','손',
    '송','신','심','아','안','양','어','엄','여','연',
    '염','오','우','원','유','윤','이','임','장','전',
    '정','조','주','지','진','차','채','천','철','청',
    '최','추','탁','표','피','하','한','함','허','현',
    '호','홍','황','건','경','광','근','금','기','나',
    '남','노','대','덕','도','동','두','명','미','민',
    '범','병','보','봉','삼','상','서','석','선','성',
    '소','수','숙','순','승','시','연','영','오','옥',
    '완','용','우','원','유','윤','은','의','인','일',
    '재','정','종','주','준','중','지','진','찬','창',
    '철','태','하','한','해','현','형','혜','호','홍',
    '화','효','희','간','간','갈','감','갑','개','거',
    '건','검','겨','견','겸','경','게','계','골','곰',
    '관','광','까','깜','꼬','꽃','귀','교','국','꽁',
    '궁','꿍','규','그','근','글','금','기','꾸','꿀',
    '꿈','꿍','난','날','낭','내','너','넌','네','녹',
    '농','누','눈','늘','니','다','단','달','대','댄',
    '데','돈','돌','동','다','딸','또','똘','똥','달',
    '당','딸','땅','두','들','랄','러','레','로','롤',
    '룰','루','막','만','말','맛','망','매','맥','멋',
    '멍','멜','모','몽','무','물','미','벌','베','병',
    '보','복','부','분','불','붉','블','비','삐','생',
    '석','수','승','세','시','실','싸','야','언','연',
    '영','예','용','울','율','은','재','제','짱','철',
    '칠','커','태','토','통','혜','휴','희'
]

def createChat(url):
    driver.get(url) # 홍보할 밴드 링크

    try:
        new_chat_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="bannerInner"]/div/section[1]/div[1]/button'))
        )
        new_chat_btn.click()
        
        # 검색 과정 추가
        cnt = 0
        members = []
        for keyword in keywords:
            print(keyword, "작업중")
            search_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/section/div/div/div/form/span/input'))
            )
            search_field.send_keys(keyword)
            search_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div/div/form/button'))
            )
            search_btn.click()

            time.sleep(1)

            check_btns = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div/div/div[3]/ul/li[*]/label/span[3]/span/input'))
            )
            print(len(check_btns))
            for i in range(len(check_btns)+1):
                check_btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="wrap"]/div[3]/div/section/div/div/div/div[3]/ul/li[{i+1}]/label/span[3]/span/input'))
                )
                member = check_btn.get_attribute('value')
                if not member in members:
                    if cnt < MAX_MEMBER_COUNT:
                        check_btn.click()
                        cnt+=1
                        members.append(member)
                        print(members)
                    else:
                        break
            if cnt >= MAX_MEMBER_COUNT:
                break
        
        
        driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/section/div/footer/button[2]').click()
        
        open_chat = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div[3]/button[2]'))
        )
        open_chat.click()

        # TODO: members 업데이트

        #driver.switch_to.window(driver.window_handles[1])


    except NoSuchElementException as e:
        print('Error: ', e)
    finally:
        driver.quit()

def applyChatOption(url):
    try:
        driver.get(url)

        option_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/header/button[2]'))
        )
        option_btn.click()

        setting_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div/section/div/footer/div/button[1]'))
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
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[4]/div/div[3]/div/section/div/div/div[2]/input'))
        )
        edit_info_name_input.clear()
        edit_info_name_input.send_keys(chat_name)

        edit_info_done_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/footer/button[1]'))
        )
        edit_info_done_btn.click()

        readers_view_describe = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[2]/div/div[1]/p'))
        )
        if readers_view_describe.text == '메시지 읽음수만 표시되고\n누가 읽었는지 확인할 수 없습니다.':
            print("꺼져있음")
        elif readers_view_describe.text == '메시지 읽음수를 눌러\n읽음 멤버를 확인할 수 있어요.':
            print("켜져있음")
        else:
            print('오류')

        readers_view = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[2]/div/div[2]'))
        )
        print(readers_view.get_attribute('checked'))
        driver.implicitly_wait(10)
        ActionChains(driver).move_to_element(readers_view).click(readers_view).perform()

        readers_view_ok_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/section/div/div[3]/button[2]'))
        )
        readers_view_ok_btn.click()
        
        time.sleep(3)

        message_period_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[3]/a'))
        )
        message_period_btn.click()

        message_preiod_min_radio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/div/ul[1]/li[1]'))
        )
        message_preiod_min_radio.click()

        message_period_done_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/footer/div/button'))
        )
        message_period_done_btn.click()

        try:
            driver.switch_to_alert().accept()
        except NoAlertPresentException as e:
            print('Error: ', e)

        time.sleep(3)

        setting_close_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/footer/button'))
        )
        setting_close_btn.click()

    except NoSuchElementException as e:
        print('Error: ', e)
    except NoAlertPresentException as e:
        print('Error: ', e)
    finally:
        driver.quit()
    

#open_chrome_with_debug_mode()
setup_driver()
applyChatOption('https://band.us/band/55170325/chat/CYkXzX')
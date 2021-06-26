import time
import logging
from selenium.webdriver.support.ui import *
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, NoAlertPresentException, NoAlertPresentException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from DriverProvider import *
from LoginMacro import *
from DBHelper import *

from PyQt5.QtCore import *

logger = logging.getLogger()
FORMAT = "[%(asctime)s][%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT, filename='./log/create_chat_macro.log')
logger.setLevel(logging.INFO)

MAX_MEMBER_COUNT = 10
WAIT_SECONDS = 10

# 디버깅 변수
profile_image = r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg'
#profile_image = r'/Users/jeong-woochang/Desktop/sample.jpeg'
chat_name = '테스트'
id = 'chad0706@naver.com'
pw = 'asdf0706'

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

members = []

class SendMessageThread(QThread):

    path = ''
    id = ''
    pw = ''
    chat_setting_id = 0

    on_error_send_msg = pyqtSignal(str, str)
    on_logging_send_msg = pyqtSignal(int, str)

    LOGGING_INFO = 0
    LOGGING_WARNING = 1
    LOGGING_ERROR = 2

    def __init__(self, parent=None):
        super().__init__()

    def run(self):
        pass

    def stop(self):
        try:
            #self.wait(5000) #5000ms = 5s
            self.isRunning = False
            self.quit()
            self.driver.close()
            self.driver.quit()
            self.on_logging_send_msg.emit(self.LOGGING_INFO, "작업이 취소됨")
        except Exception as e:
            self.on_logging_send_msg.emit(self.LOGGING_WARNING, "제거할 드라이버 없음 : "+str(e))

def getNextBand(driver):
    wait = WebDriverWait(driver, WAIT_SECONDS)

    driver.get("https://band.us")

    i = 1
    while True:
        try:
            item = wait.until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="content"]/div/section/div[2]/div/div/ul/li[{i}]'))
            )
        except:
            break
        
        if item.get_attribute('data-item-type') == 'band':
            title = driver.find_element_by_xpath(f'//*[@id="content"]/div/section/div[2]/div/div/ul/li[{i}]/div/div/a/div[2]/p').text
            item.click()
            url = driver.current_url
            band_id = url[21:]
            connect()
            t = not hasBand(id, band_id)
            close()
            if t:
                connect()
                addBand(band_id, id, title, url)
                close()
                return (band_id, id, title, url)
            connect()
            t = not isCompleted(id, band_id)
            close()
            if t:
                return (band_id, id, title, url)
            driver.get('https://band.us/')
        i+=1

    return None

def getLeaders(driver, band_id):
    wait = WebDriverWait(driver, WAIT_SECONDS)

    driver.get(f"https://band.us/band/{band_id}") # 홍보할 밴드 링크

    done=False
    err_cnt = 0
    start = time.time()
    while not done:
        try:
            # 리더 선별
            members_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="lnb"]/ul/li[5]/a/span[1]'))
            )
            members_btn.click()

            leaders = []
            member_list = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]/div/div[3]/div[2]/div/ul/li[*]'))
            )
            for i,member in enumerate(member_list):
                if i==0:
                    continue
                try:
                    em_class = member.find_element_by_xpath(f'./div[1]/span[1]/em').get_attribute('class')
                    if em_class == 'leader' or em_class == 'coleader':
                        leaders.append((member.get_attribute('data-user_no'), id, driver.current_url[21:].split('/')[0], None, time.strftime("%Y-%m-%d")))
                except:
                    break
            logging.info(leaders)
            done = True
        except Exception:
            #페이지 무한 로딩 문제 발견
            err_cnt+=1
            logger.exception(f"리더 선별시 문제발생 {err_cnt}")
            if time.time() - start >= 10:
                driver.refresh()

    return leaders

def createChat(driver, url, onlyAction=False):
    wait = WebDriverWait(driver, WAIT_SECONDS)
    
    connect()
    remainings = getRemainings(id, time.strftime("%Y-%m-%d")) 
    close()

    logging.info(url)

    if not onlyAction:
        driver.get(url) # 홍보할 밴드 링크

    done=False
    err_cnt = 0
    while not done:
        try:
            # 만들기 시작
            new_chat_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="bannerInner"]/div/section[1]/div[1]/button'))
            )
            new_chat_btn.click()
            done = True
        except Exception:
            err_cnt += 1
            logger.exception(f"'새채팅'버튼 누를때 문제발생 {err_cnt}")
    
    member_to_add = []
    try:
        cnt = 0
        for keyword in keywords:
            logging.info(keyword+" 작업중")
            search_field = wait.until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/section/div/div/div/form/span/input'))
            )
            search_field.clear()
            search_field.send_keys(keyword)
            search_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div/div/form/button'))
            )
            search_btn.click()

            time.sleep(1)

            check_btns = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div/div/div[3]/ul/li[*]/label/span[3]/span/input'))
            )
            for i in range(len(check_btns)+1):
                try:
                    check_btn = driver.find_element_by_xpath(f'//*[@id="wrap"]/div[3]/div/section/div/div/div/div[3]/ul/li[{i+1}]/label/span[3]/span/input')
                except NoSuchElementException: #list 끝
                    break
                member = (int(check_btn.get_attribute('value')), id, driver.current_url[21:], time.strftime("%Y-%m-%d"))
                logging.info(str(member))
                connect()
                members = getMembers(id)
                close()
                overlap = False
                for _member in members:
                    if _member[0] == member[0]:
                        overlap = True
                        break
                if not overlap:
                    if cnt < MAX_MEMBER_COUNT and remainings-cnt-1>=0:
                        ActionChains(driver).move_to_element(driver.find_element_by_xpath(f'//*[@id="wrap"]/div[3]/div/section/div/div/div/div[3]/ul/li[{i+1}]/label/span[3]/span/input')).click().perform()
                        cnt+=1
                        member_to_add.append(member)
                    else:
                        break
            if cnt >= MAX_MEMBER_COUNT or remainings-cnt-1<0: # 최대 멤버스 or 초대 가능 인원 수 초과
                break
            elif keywords[-1] == keyword: #모든 체크 버튼을 돌았을 때(더이상 체크 버튼이 남아 있지 않음)
                updateBandCompleted(id, url[21:], 1)
            else:
                continue

        
        logging.info(f"남은 인원 수 : {remainings - cnt}")
        
        driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/section/div/footer/button[2]').click()
    except Exception:
        logging.exception("")
        raise

    connect()
    getRemainings(id, time.strftime("%Y-%m-%d"))
    close()

    try:
        open_chat = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="wrap"]/div[3]/div/section/div/div[3]/button[2]'))
        )
        open_chat.click()
    except Exception:
        # 한도수 초과 뜸
        logging.exception("")
        raise

    driver.switch_to.window(driver.window_handles[1])

    chat_id = driver.current_url[35:]

    for member in member_to_add:
        connect()
        addMember(member[0], member[1], member[2], chat_id, member[3])
        close()

    applyChatOption(driver=driver, chat_setting_id = 4, onlyAction=True)

    driver.close()

    driver.switch_to.window(driver.window_handles[0])

def applyChatOption(driver, chat_setting_id, url=None, onlyAction=False):
    wait = WebDriverWait(driver, WAIT_SECONDS)

    connect()
    setting = getChatSetting(chat_setting_id)
    close()

    if not onlyAction:
        driver.get(url)
    
    while True:
        try:    
            option_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/header/button[2]'))
            )
            option_btn.click()

            setting_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div/section/div/footer/div/button[1]'))
            )
            setting_btn.click()
            break
        except TimeoutExceptio:
            pass
        except Exception:
            logging.exception("")
            raise

    try:
        edit_info_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/div/div/div/button'))
        )
        edit_info_btn.click()

        edit_info_image_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/div/div[1]/div/label/input'))
        )
        edit_info_image_input.send_keys(profile_image)
    except Exception:
        logging.exception("")
        raise

    try:
        edit_info_image_done_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[4]/section/div/footer/button[2]'))
        )
        #ActionChains(driver).move_to_element(edit_info_image_done_btn).click().perform()
        edit_info_image_done_btn.click()
    except Exception:
        logging.exception("")
        raise

    done=False
    err_cnt = 0
    while not done:
        try:
            edit_info_name_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[4]/div/div[3]/div/section/div/div/div[2]/input'))
            )
            edit_info_name_input.clear()
            #chat_name = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            edit_info_name_input.send_keys(chat_name)

            edit_info_done_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/footer/button[1]'))
            )
            edit_info_done_btn.click()
            done = True
        except Exception:
            #이미지 완료 못 누를시 여기서 걸려있음
            err_cnt+=1
            logger.exception(f"채팅방 이름 변경시 문제발생 {err_cnt}")
            edit_info_image_done_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[4]/section/div/footer/button[2]'))
            )
            #ActionChains(driver).move_to_element(edit_info_image_done_btn).click().perform()
            edit_info_image_done_btn.click()

    try:
        readers_view_describe = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[2]/div/div[1]/p'))
        )
        if readers_view_describe.text == '메시지 읽음수만 표시되고\n누가 읽었는지 확인할 수 없습니다.':
            
            logging.info("꺼져있음")
            readers_view = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[2]/div/div[2]'))
            )
            driver.implicitly_wait(10)
            ActionChains(driver).move_to_element(readers_view).click(readers_view).perform()

            readers_view_ok_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/section/div/div[3]/button[2]'))
            )
            readers_view_ok_btn.click()
        elif readers_view_describe.text == '메시지 읽음수를 눌러\n읽음 멤버를 확인할 수 있어요.':
            logging.info("켜져있음")
            readers_view = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[2]/div/div[2]'))
            )
            driver.implicitly_wait(10)
            ActionChains(driver).move_to_element(readers_view).click(readers_view).perform()

            readers_view_ok_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/section/div/div[3]/button[2]'))
            )
            readers_view_ok_btn.click()
        else:
            logging.info('오류')
    except Exception:
        logger.exception("메시지 읽은 멤버 확인하기 설정시 문제발생")
        raise

    done=False
    err_cnt = 0
    while not done:
        try:
            message_period_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/div/div/div/ul/li[3]/a'))
            )
            message_period_btn.click()

            message_preiod_min_radio = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/div/ul[1]/li[1]'))
            )
            message_preiod_min_radio.click()

            message_period_done_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[3]/div/section/div/footer/div/button'))
            )
            message_period_done_btn.click()

            try:
                driver.switch_to_alert().accept()
            except NoAlertPresentException:
                logging.info('보관기간 변경사항 없음')
            done = True
        except Exception:
            err_cnt+=1
            logger.exception(f"보관기간 변경시 문제발생 {err_cnt}")

    done=False
    err_cnt = 0
    while not done:
        try:
            setting_close_btn = wait.until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="layerContainer"]/div/div[2]/section/div/footer/button'))
            )
            setting_close_btn.click()
            done = True
        except Exception:
            err_cnt+=1
            logger.exception(f"설정 닫기 문제 발생 {err_cnt}")
    
driver = setup_driver("C:\Program Files\Google\Chrome\Application\chrome.exe")
result = loginWithEmail(driver, id, pw)
if result == LOGIN_SUCCESS or result == LOGGED_IN:
    #applyChatOption(driver=driver, url='https://band.us/band/60518206/chat/CYlHvZ')
    while True:
        band = getNextBand(driver)
        if band is None:
            break
        leaders = getLeaders(driver, band[0])

        connect()
        for leader in leaders:
            if not hasMember(id, leader[0]):
                logging.info(leader)
                addMember(*leader)
        close()
        createChat(driver, band[3])
        


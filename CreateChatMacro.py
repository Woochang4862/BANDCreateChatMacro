import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from DriverProvider import ChromeDriverException, setup_driver
from LoginMacro import LOGIN_IDENTIFICATION, loginWithEmail, LOGIN_ERROR, LOGIN_SUCCESS, LOGGED_IN
from DBHelper import *

from PyQt5.QtCore import *

logger = logging.getLogger()
FORMAT = "[%(asctime)s][%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logger.setLevel(logging.INFO)

MAX_MEMBER_COUNT = 100
WAIT_SECONDS = 10

# # 디버깅 변수
# profile_image = r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg'
# #profile_image = r'/Users/jeong-woochang/Desktop/sample.jpeg'
# chat_name = '테스트'
# id = 'chad0706@naver.com'
# pw = 'asdf0706'

keywords = [
    '강','고','공','곽','구','권','김','라','류','마',
    '맹','문','박','반','방','배','백','사','설','손',
    '송','신','심','아','안','양','어','엄','여','염',
    '이','임','장','전','조','차','채','천','청','최',
    '추','탁','표','피','함','허','황','나','남','노',
    '덕','도','명','민','범','봉','삼','상','서','선',
    '성','소','숙','순','오','옥','완','우','원','유',
    '윤','의','인','일','정','종','주','준','중','지',
    '진','찬','창','하','한','해','현','형','호','홍',
    '화','효','간','갈','감','갑','개','거','건','검',
    '겨','견','겸','경','게','계','골','곰','관','광',
    '까','깜','꼬','꽃','귀','교','국','꽁','궁','규',
    '그','근','글','금','기','꾸','꿀','꿈','꿍','난',
    '날','낭','내','너','넌','네','녹','농','누','눈',
    '늘','니','단','대','댄','데','돈','돌','동','다',
    '또','똘','똥','달','당','딸','땅','두','들','랄',
    '러','레','로','롤','룰','루','막','만','말','맛',
    '망','매','맥','멋','멍','멜','모','몽','무','물',
    '미','벌','베','병','보','복','부','분','불','붉',
    '블','비','삐','생','석','수','승','세','시','실',
    '싸','야','언','연','영','예','용','울','율','은',
    '재','제','짱','철','칠','커','태','토','통','혜'
]

class MemberExceededException(Exception):
    def __str__(self):
        return "멤버수 초과!"

class ChatRestrictionBandException(Exception):
    def __str__(self):
        return "체팅 제한 밴드!"

class PrivateChatRestrictionBandException(Exception):
    def __str__(self):
        return "비공개 채팅 제한 밴드!"

class NoMemberSelectedException(Exception):
    def __str__(self):
        return "멤버가 초대되지 않음"

class InfinityLoadingException(Exception):
    def __str__(self) -> str:
        return "무한 로딩 에러"


class CreateChatThread(QThread):

    path = ''
    id = ''
    pw = ''
    ip = ''
    chat_setting_id = 0

    
    on_finished_create_chat = pyqtSignal(str)
    on_update_progressbar = pyqtSignal(int)
    on_error_create_chat = pyqtSignal(str, str) # 발생한 계정, 오류 메시지

    def __init__(self, parent=None):
        super().__init__()

    def run(self):
        connect()
        remainings = getRemainings(self.id, time.strftime("%Y-%m-%d"))    
        close()
        try:
            if remainings != 0:
                self.driver = setup_driver(self.ip)
                result = loginWithEmail(self.driver, self.id, self.pw)
                if result == LOGIN_SUCCESS or result == LOGGED_IN:
                    pinned_bands = self.getPinnedBands(self.driver)               
                    connect()
                    for band in pinned_bands:
                        if not hasBand(self.id, band[0]):
                            addBand(*band)
                        else:
                            updateBandCompleted(self.id, band[0], 1)
                    close()
                    for band_id, account_id, title, url in self.getBandList(self.driver):
                        connect()
                        if not hasBand(account_id, band_id):
                            addBand(band_id, account_id, title, url)
                            band_id, account_id, name, url, completed, latest_keyword = getBand(band_id, account_id)
                            leaders = self.getLeaders(self.driver, band_id)
                            for leader in leaders:
                                leader_id, account_id, band_id, chat_id, date = leader
                                if not hasMember(account_id, leader_id):
                                    logging.info(leader)
                                    addMember(*leader)
                        else:
                            band_id, account_id, name, url, completed, latest_keyword = getBand(band_id, account_id)
                            if completed == 1:
                                continue
                        close()
                        
                        done = False
                        while self.isRunning and not done:
                            try:
                                self.createChat(self.driver, band_id)
                                connect()
                                remainings = getRemainings(account_id, time.strftime("%Y-%m-%d"))
                                close()
                                self.on_update_progressbar.emit(remainings)

                                connect()
                                if isCompleted(account_id, band_id):
                                    self.pinBand(self.driver, band_id, title)
                                    done = False
                                close()

                                if remainings == 0:
                                    self.driver.close()
                                    self.driver.quit()
                                    self.on_finished_create_chat.emit(account_id)
                                    return
                            except InfinityLoadingException:
                                self.on_error_create_chat.emit(self.id, "검색하는 중 로딩이 완료되지 않아서 중지되었습니다")
                                self.driver.close()
                                self.driver.quit()
                                return  
                            except ChatRestrictionBandException:
                                connect()
                                if isCompleted(account_id, band_id):
                                    self.pinBand(self.driver, band_id)
                                close()
                                done = True
                            except PrivateChatRestrictionBandException:
                                connect()
                                if isCompleted(account_id, band_id):
                                    self.pinBand(self.driver, band_id)
                                close()
                                done = True
                            except NoMemberSelectedException:
                                connect()
                                if isCompleted(account_id, band_id):
                                    self.pinBand(self.driver, band_id)
                                close()  
                                done = True   
                            except MemberExceededException:
                                self.on_error_create_chat.emit(account_id, "하루 한도 수 초과")
                                self.driver.close()
                                self.driver.quit()
                                self.on_finished_create_chat.emit(account_id)
                                return          
                else: # 로그인 실패
                    self.on_error_create_chat.emit(self.id, "로그인 실패")
                self.driver.close()
                self.driver.quit()
            else:
                self.on_error_create_chat.emit(self.id, "하루 한도 수 초과")
            self.on_finished_create_chat.emit(self.id)
        except ChromeDriverException:
            logging.exception("CreateChatMacro.py")
            self.on_error_create_chat.emit(self.id, "크롬 드라이버를 얻어오는데 실패하였습니다.")
        except: # 혹시나 에러 발생시 잡아내기 위해
            logging.exception("")
            self.stop()

    def stop(self):
        try:
            self.isRunning = False
            self.quit()
            self.driver.close()
            self.driver.quit()
        except:
            logging.exception("CreateChatMacro.py::stop")

    def pinBand(self, driver, band_id):
        wait = WebDriverWait(driver, WAIT_SECONDS)

        driver.get("https://band.us")

        list_edit = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="area"]/button'))
        )
        list_edit.click()

        pinned_list_edit = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="_btnBandOrder"]'))
        )
        pinned_list_edit.click()

        i = 1
        while self.isRunning:
            try:
                # 아이템 존재 여부 확인용
                wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@data-viewname="DUnpinnedBandListView"]/li[{i}]/span[@class="text"]/span')))
                ActionChains(driver).move_to_element(driver.find_element_by_xpath(f'//*[@data-viewname="DUnpinnedBandListView"]/li[{i}]/span[@class="etc"]/button')).click().perform()
                pinned_band = wait.until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@data-viewname="DPinnedBandListView"]/li[last()]'))
                )
                _band_id = int(pinned_band.get_attribute('data-band_no'))
                if _band_id == band_id:
                    done_btn = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@class="footer"]/button[2]'))
                    )
                    done_btn.click()
                    return
                else:
                    cancel_btn = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@class="footer"]/button[1]'))
                    )
                    cancel_btn.click()
            except TimeoutException:
                logging.exception("")
                break
            
            i+=1

    def getPinnedBands(self, driver):
        wait = WebDriverWait(driver, WAIT_SECONDS)

        driver.get("https://band.us")

        list_edit = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="area"]/button'))
        )
        list_edit.click()

        pinned_list_edit = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="_btnBandOrder"]'))
        )
        pinned_list_edit.click()

        result = []

        i = 1
        while self.isRunning:
            try:
                pinned_band = wait.until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@data-viewname="DPinnedBandListView"]/li[{i}]'))
                )
                band_id = int(pinned_band.get_attribute('data-band_no'))
                band_title = wait.until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@data-viewname="DPinnedBandListView"]/li[{i}]/span[@class="text"]/span'))
                ).text
                band_url = f"https://band.us/band/{band_id}"
            except TimeoutException:
                logging.exception("")
                break
            
            result.append((band_id, self.id, band_title, band_url, 1))
            i+=1
        
        return result

    def getBandList(self, driver):
        wait = WebDriverWait(driver, WAIT_SECONDS)

        driver.get("https://band.us/my/profiles")

        result = []

        bands = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, f'//*[@class="bandList _bands"]/li'))
        )
        for band in bands:
            band_id = band.get_attribute('data-band-no')
            title = band.text
            result.append((band_id, self.id, title, f'https://band.us/band/{band_id}'))

        return result

    def getLeaders(self, driver, band_id):
        wait = WebDriverWait(driver, WAIT_SECONDS)

        driver.get(f"https://band.us/band/{band_id}/member") # 홍보할 밴드 링크

        done=False
        err_cnt = 0
        start = time.time()
        while not done:
            try:
                # 리더 선별
                leaders = []
                member_list = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]/div/div[3]/div[2]/div/ul/li[*]'))
                )
                for i,member in enumerate(member_list):
                    if i==0:
                        continue
                    try:
                        em_class = member.find_element_by_xpath('./div[1]/span[1]/em').get_attribute('class')
                        if em_class == 'leader' or em_class == 'coleader':
                            leaders.append((member.get_attribute('data-user_no'), self.id, band_id, None, time.strftime("%Y-%m-%d")))
                    except:
                        break
                logging.info(leaders)
                done = True
            except Exception:
                # TODO : 페이지 무한 로딩 문제 발견
                err_cnt+=1
                logger.exception(f"리더 선별시 문제발생 {err_cnt}")
                if time.time() - start >= 10:
                    driver.refresh()

        return leaders

    def createChat(self, driver, band_id, onlyAction=False):
        wait = WebDriverWait(driver, WAIT_SECONDS)
        
        connect()
        remainings = getRemainings(self.id, time.strftime("%Y-%m-%d")) 
        close()

        if remainings == 0:
            raise MemberExceededException()

        logging.info(f"채팅방 만들려는 밴드 아이디 : {band_id}")

        if not onlyAction:
            driver.get(f"https://band.us/band/{band_id}") # 홍보할 밴드 링크

        err_cnt = 0
        while self.isRunning:
            try:
                # 만들기 시작
                new_chat_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@class="newChatWrap"]/button'))
                )
                new_chat_btn.click()
                break
            except Exception:
                if err_cnt == 6:
                    logging.exception("새채팅 버튼 누를 수 없음")
                    connect()
                    updateBandCompleted(self.id, band_id, 1)
                    close() 
                    raise ChatRestrictionBandException()
                err_cnt += 1
                logger.exception(f"'새채팅'버튼 누를때 문제발생 {err_cnt}")
                
        
        member_to_add = []
        connect()
        k = getLatestKeyword(self.id, band_id)
        close()
        _keywords = keywords
        if not k is None:
            _keywords = keywords[keywords.index(k):]
        
        latest_keyword = k
        try:
            for keyword in _keywords:
                logging.info(keyword+" 작업중")
                latest_keyword = keyword
                try:
                    search_field = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@class="inputWrap"]/input'))
                    )
                except UnexpectedAlertPresentException: # 채팅 제한 밴드
                    connect()
                    updateBandCompleted(self.id, band_id, 1)
                    close() 
                    raise ChatRestrictionBandException()
                except TimeoutException: # 비공개 채팅방 만들기 나올때
                    try:
                        driver.find_element_by_xpath('//*[@data-viewname="DBandChattingChannelListView"]/div[1]/div/ul/li[1]/a').click()
                        search_field = wait.until(
                            EC.presence_of_element_located((By.XPATH, '//*[@class="inputWrap"]/input'))
                        )
                    except:
                        logging.exception("")
                        connect()
                        updateBandCompleted(self.id, band_id, 1)
                        close() 
                        raise PrivateChatRestrictionBandException()
                search_field.clear()
                search_field.send_keys(keyword)
                search_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@data-uiselector="btnSearch"]'))
                )
                search_btn.click()

                try:
                    wait.until_not(
                        EC.presence_of_element_located((By.XPATH, '//*[@data-viewname="DMemberSelectItemView"]/p[@class="uLoading"]'))
                    )
                except:
                    logging.exception("")
                    raise InfinityLoadingException()

                isEmpty = False
                try:
                    driver.find_element_by_xpath(f'//*[@class="uEmpty  columnFlexible"]/span')
                    isEmpty = True
                except:
                    logging.exception("")
                    isEmpty = False

                if isEmpty:
                    continue

                check_btns = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@data-viewname="DMemberSelectItemView"]'))
                )
                
                for i in range(1, len(check_btns)+1):
                    err_cnt = 0
                    while self.isRunning:
                        try:
                            check_btn = driver.find_element_by_xpath(f'//*[@data-viewname="DMemberSelectItemView" and position()={i}]/label/span[3]/span/input')
                            member = (int(check_btn.get_attribute('value')), self.id, band_id, time.strftime("%Y-%m-%d"))
                            logging.info(f"현재 멤버 정보 : {str(member)}")
                            break
                        except:
                            err_cnt+=1
                            logging.exception(f"멤버 정보 가져오는데 문제발생 {err_cnt}")
                    connect()
                    members = getMembers(self.id, band_id)
                    close()
                    overlap_on_db = False
                    for _member in members:
                        if _member[0] == member[0]:
                            overlap_on_db = True
                            break
                    overlap_on_local = False 
                    for _member in member_to_add:
                        if _member[0] == member[0]:
                            overlap_on_local = True
                            break
                    if (not overlap_on_db) and (not overlap_on_local):
                        if len(member_to_add) == MAX_MEMBER_COUNT or remainings==len(member_to_add):
                            break
                        ActionChains(driver).move_to_element(driver.find_element_by_xpath(f'//*[@data-viewname="DMemberSelectItemView" and position()={i}]/label/span[3]/span/input')).click().perform()
                        member_to_add.append(member)

                if len(member_to_add) == MAX_MEMBER_COUNT or remainings==len(member_to_add): # 최대 멤버 수 or 초대 가능 인원 수 초과
                    break
                else:
                    if keywords[-1] == keyword: #모든 체크 버튼을 돌았을 때(더이상 체크 버튼이 남아 있지 않음)
                        connect()
                        updateBandCompleted(self.id, band_id, 1)
                        close()
                    continue
            
            logging.info(f"남은 인원 수 : {remainings - len(member_to_add)}")
            
            # 초대하기 버튼 누르기
            if len(member_to_add)>0:
                driver.find_element_by_xpath('//*[@data-uiselector="btnInvite"]').click()
            else:
                connect()
                updateBandCompleted(self.id, band_id, 1)
                close() 
                raise NoMemberSelectedException()
        except:
            logging.exception("")
            raise 

        try:
            open_chat = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class="modalFooter"]/button[2]'))
            )
            open_chat.click()
        except UnexpectedAlertPresentException:
            # 혹시나 한도수 초과 뜨면
            raise MemberExceededException()
        except AttributeError:
            raise MemberExceededException()
        except TimeoutException:
            connect()
            updateBandCompleted(self.id, band_id, 1)
            close()
            return
        except Exception: # TODO : 여기에서 마지막까지 갔을때 멈춤 #436 왜 실행 안됨?
            logging.exception("")
            raise

        driver.switch_to.window(driver.window_handles[1])

        chat_id = driver.current_url[35:]

        for member in member_to_add:
            connect()
            addMember(member[0], member[1], member[2], chat_id, member[3])
            close()

        connect()
        updateLatestKeyword(self.id, band_id, latest_keyword)
        close()

        self.applyChatOption(driver=driver, chat_setting_id=self.chat_setting_id, onlyAction=True)

        driver.close()

        driver.switch_to.window(driver.window_handles[0])

    def applyChatOption(self, driver, chat_setting_id, url=None, onlyAction=False):
        wait = WebDriverWait(driver, WAIT_SECONDS)

        connect()
        id, name, chat_name, chat_image, chat_readers_view, chat_message_period = getChatSetting(chat_setting_id)
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
            except TimeoutException:
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
            edit_info_image_input.send_keys(chat_image)
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
            if readers_view_describe.text == '메시지 읽음수만 표시되고\n누가 읽었는지 확인할 수 없습니다.' and chat_readers_view == 1:
                
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
            elif readers_view_describe.text == '메시지 읽음수를 눌러\n읽음 멤버를 확인할 수 있어요.' and chat_readers_view == 0:
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
                logging.info(f'변경할 필요 없음 (표시된 텍스트 : {readers_view_describe.text})')
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

                idx = 1
                if chat_message_period == "min":
                    idx = 1
                elif chat_message_period == "month":
                    idx = 2
                elif chat_message_period == "year":
                    idx = 3

                message_preiod_radio = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@id="layerContainer"]/div/div[3]/div/section/div/div/ul[1]/li[{idx}]'))
                )
                message_preiod_radio.click()

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

            

# driver = setup_driver(None)
# result = loginWithEmail(driver, "hungsung0234@gmail.com", "hung0804288")
# if result == LOGIN_SUCCESS or result == LOGGED_IN:
#     #applyChatOption(driver=driver, url='https://band.us/band/60518206/chat/CYlHvZ')
#     print(getBandList(driver))
        


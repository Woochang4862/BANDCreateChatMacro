import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from CreateChatMacro import CreateChatThread
from DBHelper import *
from LoginMacro import ValidateAccountThread

import logging
import time
import os

logger = logging.getLogger()
FORMAT = "[%(asctime)s][%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT, filename=f'./log/{time.strftime("%Y-%m-%d")}.log')
logger.setLevel(logging.INFO)

form_class = uic.loadUiType(os.path.abspath("./ui/create_chat_macro_v2.ui"))[0]

class MyWindow(QMainWindow, form_class):

    """
    시그널
    ::START::
    """
    state_validation_finished = pyqtSignal()
    state_identification_finished = pyqtSignal()
    """
    ::END::
    """

    """
    변수
    ::START::
    """
    accounts = []
    settings = []
    isRunning = False
    """
    ::END::
    """

    """
    상수
    ::START::
    """
    """
    ::END::
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon('icon.ico'))

        """
        스레드
        ::START::
        """
        self.validateAccountThread = ValidateAccountThread(parent=self)
        self.validateAccountThread.state_logged_in.connect(self.state_logged_in)
        self.validateAccountThread.state_login_success.connect(self.state_login_success)
        self.validateAccountThread.state_login_fail.connect(self.state_login_fail)
        self.validateAccountThread.state_login_error.connect(self.state_login_error)
        self.validateAccountThread.state_login_validation.connect(self.state_login_validation)
        self.validateAccountThread.state_login_identification.connect(self.state_login_identification)
        """
        ::END::
        """

        connect()
        self.accounts = getAccounts()
        self.settings = getChatSettings()
        close()
        self.bindToAccountTable()
        self.bindToChatSettingTable()
        self.bindToChatSettingComboBox()

    # """
    # 크롬 경로 설정
    # ::START::
    # """
    # def on_chrome_route_edited(self, text):
    #     if self.isRunning:
    #         return
    #     connect()
    #     putStringExtra(KEY_CHROME_ROUTE, text)
    #     close()

    # def on_validation_chrome_clicked(self):
    #     logging.info("크롬 확인 : 크롬 경로 확인 중 ...")
    #     try:
    #         driver = setup_driver(self.chrome_edit.text().strip())
    #         driver.close()
    #         driver.quit()
    #         logging.info("크롬 확인 : 올바른 크롬 경로")
    #         QMessageBox.information(self.centralwidget, '크롬 경로 확인', '올바른 크롬 경로입니다', QMessageBox.Ok, QMessageBox.Ok)
    #     except:
    #         logging.exception("")
    #         logging.info("크롬 확인 : 올바르지 않은 크롬 경로")
    #         QMessageBox.critical(self.centralwidget, '크롬 경로 오류', '크롬 경로를 확인해 주세요', QMessageBox.Ok, QMessageBox.Ok)
    # """
    # ::END::
    # """

    """
    계정 화면 설정
    ::START::
    """
    def on_id_changed(self, text):
        logging.info(text)
        self.toggleAddButton(False)

    def on_pw_changed(self, text):
        logging.info(text)
        self.toggleAddButton(False)
    
    def on_ip_changed(self, text):
        logging.info(text)
        self.toggleAddButton(False)

    def toggleAddButton(self, enabled=None):
        if enabled is None:
            self.add_btn.setEnabled(not self.add_btn.isEnabled())
        else:
            self.add_btn.setEnabled(enabled)

    def on_validation_account_clicked(self):
        logging.info("계정 확인")
        if self.isRunning:
            return
        id = self.id_edit.text().strip()
        pw = self.pw_edit.text().strip()
        ip = self.ip_edit.text().strip()

        if id != '' and pw != '':
            self.validateAccountThread.id = id
            self.validateAccountThread.pw = pw
            self.validateAccountThread.ip = ip
            self.validateAccountThread.start()
        else:
            logging.info("계정 확인 : 이메일 혹은 비밀번호가 비어 있음")

    def on_add_account_clicked(self):
        logging.info("계정 추가")
        if self.isRunning:
            return
        id = self.id_edit.text().strip()
        pw = self.pw_edit.text().strip()
        ip = self.ip_edit.text().strip()
        
        for _id, _, _ in self.accounts:
            if _id == id:
                logging.info("계정 추가 : 동일한 이메일이 이미 존재함")
                return

        connect()
        addAccount(id, pw, ip)
        self.accounts = getAccounts()
        close()

        self.bindToAccountTable()
        self.bindToAccountComboBox()

        self.id_edit.clear()
        self.pw_edit.clear()
        self.ip_edit.clear()

        self.toggleAddButton(False)

        self.validateRunButton()

    def on_delete_account_clicked(self):
        logging.info("계정 삭제")
        if self.isRunning:
            return
        
        for _range in self.account_table.selectedRanges():
            topRow = _range.topRow()
            bottomRow = _range.bottomRow()

            for row in range(topRow, bottomRow+1):
                id = self.account_table.item(row, 0).text()
                pw = self.account_table.item(row, 1).text()
                connect()
                deleteAccount(id)
                close()

        connect()
        self.accounts = getAccounts()
        close()
        
        self.bindToAccountTable()

        self.validateRunButton()


    def bindToAccountTable(self):
        self.account_table.clear()
        self.account_table.setColumnCount(3)
        self.account_table.setRowCount(len(self.accounts))
        self.account_table.setHorizontalHeaderLabels(["이메일", "비밀번호", "아이피"])

        for idx, (id, pw, ip) in enumerate(self.accounts): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 

            self.account_table.setItem(idx, 0, QTableWidgetItem(id)) 
            self.account_table.setItem(idx, 1, QTableWidgetItem(pw)) 
            self.account_table.setItem(idx, 2, QTableWidgetItem(ip)) 

        self.account_table.setSortingEnabled(False)  # 정렬기능
        self.account_table.resizeRowsToContents()
        self.account_table.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.

        logging.info(f"계정 로딩 : {len(self.accounts)} 개가 로딩됨")

    def bindToAccountComboBox(self):
        self.account_combobox.clear()
        self.account_combobox.addItem("계정")

        for (id, _, _) in self.accounts:
            self.account_combobox.addItem(id)

    @pyqtSlot()
    def state_logged_in(self):
        self.toggleAddButton(False)
        QMessageBox.warning(self.centralwidget, '로그인 상태', '로그아웃 후 다시 시도해 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_success(self):
        self.toggleAddButton(True)
        QMessageBox.information(self.centralwidget, '로그인 성공', '아래 추가 버튼을 눌러 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_fail(self):
        self.toggleAddButton(False)
        QMessageBox.critical(self, '로그인 실패', '이메일 또는 비밀번호를 확인해 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_error(self):
        self.toggleAddButton(False)
        QMessageBox.critical(self, '로그인 오류', '로그인 시도 중 문제가 발생하였습니다', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_validation(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("이메일 인증 후 아래 확인 버튼을 눌러 주세요")
        msgBox.setWindowTitle("이메일 인증 요청")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.buttonClicked.connect(lambda _ : self.state_validation_finished.emit())
        msgBox.exec()

    @pyqtSlot()
    def state_login_identification(self):
        new_pw, ok = QInputDialog.getText(self, 'IP 변경 감지됨', '본인확인 후 변경된 비밀번호를 입력해주세요')

        if ok:
            self.pw_edit.setText(new_pw)
            self.state_identification_finished.emit()
    """
    ::END::
    """

    """
    채팅 설정 화면
    ::START:: 
    """
    message_period = {
        "보관안함" : "min",
        "30일" : "month",
        "1년" : "year"
    }

    def on_open_image_picker(self):
        fname = QFileDialog.getOpenFileName(self, filter="Images (*.png *.jpg *.jpeg)")
        logging.info(f"불러온 파일 경로 : {fname[0]}")
        self.chat_image_btn.setText(fname[0])

    def on_add_chat_setting_clicked(self):
        logging.info("설정 추가")
        if self.isRunning:
            return

        mp = ""

        if self.radio_min.isChecked():
            mp = self.radio_min.text().strip()
        elif self.radio_month.isChecked():
            mp = self.radio_month.text().strip()
        elif self.radio_year.isChecked():
            mp = self.radio_year.text().strip()

        if self.chat_setting_name_edit.text().strip() != "" and self.chat_name_edit.text().strip() != "" and self.chat_image_btn.text().strip() != "찾아보기":
            connect()
            id = addChatSetting(self.chat_setting_name_edit.text().strip(), self.chat_name_edit.text().strip(), self.chat_image_btn.text().strip(), 1 if self.chat_reader_view_chkbox.isChecked() else 0, self.message_period.get(mp))
            close()
            #self.settings.append((id))
            #self.oper_settings.append((self.OPER_ADD,(id)))
        else: # 빈칸 혹은 이미지가 선택되지 않음
            pass

        connect()
        self.settings = getChatSettings()
        close()
        self.bindToChatSettingTable()
        self.bindToChatSettingComboBox()

    def on_delete_chat_setting_clicked(self):
        logging.info("설정 삭제")
        if self.isRunning:
            return
        deletedSettings = 0
        for _range in self.chat_setting_table.selectedRanges():
            topRow = _range.topRow()
            bottomRow = _range.bottomRow()

            for row in range(topRow, bottomRow+1):
                id = self.settings[row][0]
                #self.settings.remove((id,pw))
                #self.oper_accounts.append((self.OPER_DELETE, (id,pw)))
                deletedSettings+=1
                connect()
                deleteChatSetting(id)
                close()

        logging.info(f"계정 삭제 : {deletedSettings} 개를 삭제 시킴")

        connect()
        self.settings = getChatSettings()
        close()
        self.bindToChatSettingTable()
        self.bindToChatSettingComboBox()

    def bindToChatSettingTable(self):
        self.chat_setting_table.clear()
        self.chat_setting_table.setColumnCount(5)
        self.chat_setting_table.setRowCount(len(self.settings))
        self.chat_setting_table.setHorizontalHeaderLabels(["설정 이름", "채팅방 이름", "채팅방 이미지", "읽은 멤버 보기", "보관기간"])

        for idx, (id, name, chatName, chatImage, chatReadersView, chatMessagePeriod) in enumerate(self.settings): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 

            self.chat_setting_table.setItem(idx, 0, QTableWidgetItem(name)) 
            self.chat_setting_table.setItem(idx, 1, QTableWidgetItem(chatName)) 
            self.chat_setting_table.setItem(idx, 2, QTableWidgetItem(chatImage)) 
            self.chat_setting_table.setItem(idx, 3, QTableWidgetItem("읽음 멤버 보기" if chatReadersView == 1 else "읽은 멤버 보지 않기")) 
            self.chat_setting_table.setItem(idx, 4, QTableWidgetItem(list(self.message_period.keys())[list(self.message_period.values()).index(chatMessagePeriod)])) 

        self.chat_setting_table.setSortingEnabled(False)  # 정렬기능
        self.chat_setting_table.resizeRowsToContents()
        self.chat_setting_table.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.

        logging.info(f"계정 로딩 : {len(self.settings)} 개가 로딩됨")

    def bindToChatSettingComboBox(self):
        self.setting_combobox.clear()
        self.setting_combobox.addItem("설정")

        for (_,name,_,_,_,_) in self.settings:
            self.setting_combobox.addItem(name)

    """
    ::END::
    """

    """
    멤버 목록 화면
    ::START::
    """
    def on_account_combobox_changed(self, account_id):
        if self.isRunning:
            return
        logging.info(f"선택된 아이디 : {account_id}")

        self.member_tree.clear()

        if account_id == "계정":
            return

        connect()
        self.bands = getBands(account_id)
        close()

        for (band_id, account_id, name, url, completed, latest_keyword) in self.bands:
            band_node = QTreeWidgetItem(self.member_tree)
            band_node.setText(0,f"{name}({'완료' if completed==1 else f'미완료({latest_keyword})'})")
            connect()
            members = getMembers(account_id, band_id)
            close()
            for (member_id, _, _, chat_id, date) in members:
                member_node = QTreeWidgetItem(band_node)
                member_node.setText(0,f"{member_id}({chat_id}/{date})")
            
                

            
    """
    ::END::
    """

    """
    탭 설정
    ::START::
    """
    def on_tab_changed(self, index):
        if self.isRunning:
            return
        logging.info(f"선택된 탭 : {index}")
        if index == 0:
            connect()
            self.accounts = getAccounts()
            close()
            self.bindToAccountTable()
        elif index == 1:
            connect()
            self.settings = getChatSettings()
            close()
            self.bindToChatSettingTable()
        elif index == 2:
            connect()
            self.accounts = getAccounts()
            close()
            self.bindToAccountComboBox()

    """
    ::END::
    """

    """
    실행/중단 설정
    ::START::
    """
    def on_chat_setting_combobox_changed(self, chat_setting):
        self.validateRunButton()

    def on_run_clicked(self):
        logging.info("실행")

        logging.info(f"현재 실행 환경 (계정 : {self.accounts}, 설정 : {self.settings[self.setting_combobox.currentIndex()-1]})")

        image_path = self.settings[self.setting_combobox.currentIndex()-1][3]
        if not os.path.isfile(image_path):
            QMessageBox.critical(self.centralwidget, '채팅 이미지 경로 오류', '채팅 이미지 경로를 확인해 주세요', QMessageBox.Ok, QMessageBox.Ok)
            return

        self.toggleRunButton(False)
        self.toggleStopButton(True)
        
        self.i = 0
        self.isRunning = True

        if self.i < len(self.accounts) and self.isRunning:
            id,pw,ip = self.accounts[self.i]
            self.i+=1
            self.progressBar.reset()
            connect()
            self.progressBar.setValue((1000-getRemainings(id, time.strftime("%Y-%m-%d")))//10)
            close()
            self.createChatThread = CreateChatThread(parent=self)
            self.createChatThread.on_finished_create_chat.connect(self.on_finished_create_chat)
            self.createChatThread.on_update_progressbar.connect(self.on_update_progressbar)
            self.createChatThread.on_error_create_chat.connect(self.on_error_create_chat)
            self.createChatThread.id = id
            self.createChatThread.pw = pw
            self.createChatThread.ip = ip
            self.createChatThread.chat_setting_id = self.settings[self.setting_combobox.currentIndex()-1][0]
            self.createChatThread.start()
            self.current_id_label.setText(f"현재 아이디 : {id}")
            self.current_ip_label.setText(f"현재 아이피 : {ip}") #현재 아이피 주소 바꿈
        
    def on_stop_clicked(self):
        logging.info("중단")
        if self.createChatThread.isRunning:
            self.createChatThread.stop()
        self.isRunning = False
        self.toggleStopButton(False)
        self.toggleRunButton(True)

    def validateRunButton(self):
        if len(self.accounts) == 0 or self.setting_combobox.currentText() == "설정":
            self.toggleRunButton(False)
        else:
            self.toggleRunButton(True)

    def toggleRunButton(self, enabled=None):
        if enabled is None:
            self.run_btn.setEnabled(not self.run_btn.isEnabled())
        else:
            self.run_btn.setEnabled(enabled)

    def toggleStopButton(self, enabled=None):
        if enabled is None:
            self.stop_btn.setEnabled(not self.stop_btn.isEnabled())
        else:
            self.stop_btn.setEnabled(enabled)

    def on_update_progressbar(self, remainings):
        self.progressBar.setValue((1000-remainings)//10)

    def on_finished_create_chat(self, id):
        if self.i < len(self.accounts) and self.isRunning:
            id,pw,ip = self.accounts[self.i]
            self.i+=1
            if self.createChatThread.isRunning:
                self.createChatThread.stop()
            self.progressBar.reset()
            connect()
            self.progressBar.setValue((1000-getRemainings(id, time.strftime("%Y-%m-%d")))//10)
            close()
            self.createChatThread = CreateChatThread(parent=self)
            self.createChatThread.on_finished_create_chat.connect(self.on_finished_create_chat)
            self.createChatThread.on_update_progressbar.connect(self.on_update_progressbar)
            self.createChatThread.on_error_create_chat.connect(self.on_error_create_chat)
            self.createChatThread.id = id
            self.createChatThread.pw = pw
            self.createChatThread.ip = ip
            self.createChatThread.chat_setting_id = self.settings[self.setting_combobox.currentIndex()-1][0]
            self.createChatThread.start()
            self.current_id_label.setText(f"현재 아이디 : {id}")
            self.current_ip_label.setText(f"현재 아이피 : {ip}") #현재 아이피 주소 바꿈
        else:
            self.on_stop_clicked()
            self.validateRunButton()
        
    def on_error_create_chat(self, id, msg):
        logging.info(f"{id}에서 {msg}")

        if msg == "한도 수 초과":
            self.on_stop_clicked()
            self.validateRunButton()
    """
    :::END::
    """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from CreateChatMacro import *
from DBHelper import *

import logging
import time
import os
from collections import deque 

logger = logging.getLogger()
FORMAT = "[%(asctime)s][%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT, filename='./log/create_chat_macro.log')
logger.setLevel(logging.DEBUG)

form_class = uic.loadUiType(os.path.abspath("./ui/create_chat_macro_v2.ui"))[0]

class MyWindow(QMainWindow, form_class):

    """
    시그널
    ::START::
    """
    state_validation_finished = pyqtSignal()
    """
    ::END::
    """

    """
    변수
    ::START::
    """
    accounts = []
    settings = []
    oper_accounts = deque([])
    oper_settings = deque([])
    """
    ::END::
    """

    """
    상수
    ::START::
    """
    OPER_DELETE = 0
    OPER_ADD = 1
    """
    ::END::
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

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
        """
        ::END::
        """

        """
        메뉴바
        ::START::
        """
        self.actionSave.triggered.connect(self.on_save_clicked)
        """
        ::END::
        """

        connect()
        self.accounts = getAccounts()
        self.settings = getChatSettings()
        #self.chrome_edit.setText(getStringExtra(KEY_CHROME_ROUTE, ""))
        close()
        self.bindToAccountTable()
        self.bindToChatSettingTable()

    """
    메뉴바
    ::START::
    """
    def on_save_clicked(self):
        logging.debug("계정 저장")
        connect()
        logging.debug(f"프로그램에 저장된 계정 목록(저장되지 않음): {self.accounts}")
        add_cnt = 0
        delete_cnt = 0
        for oper in self.oper_accounts:
            if oper[0] == self.OPER_ADD:
                addAccount(oper[1][0], oper[1][1])
                add_cnt+=1
            if oper[0] == self.OPER_DELETE:
                deleteAccount(oper[1][0])
                delete_cnt+=1
        self.accounts = getAccounts()
        close()

        if add_cnt != 0:
            logging.debug("계정 저장", f"{add_cnt} 개가 DB에 추가됨")
        if delete_cnt != 0:
            logging.debug("계정 저장", f"{delete_cnt} 개가 DB에서 삭제됨")

        self.oper_accounts.clear()

        connect()
        putStringExtra(KEY_CHROME_ROUTE, self.chrome_edit.text())
        putStringExtra(KEY_KEYWORD, self.keyword_edit.text())
        putStringExtra(KEY_CONTENT, self.content_edit.toPlainText())
        close()
    """
    ::END::
    """

    """
    크롬 경로 설정
    ::START::
    """
    def on_validation_chrome_clicked(self):
        logging.info("크롬 확인", "크롬 경로 확인 중 ...")
        try:
            driver = setup_driver(self.chrome_edit.text().strip())
            driver.close()
            logging.info("크롬 확인", "올바른 크롬 경로")
            QMessageBox.information(self.centralwidget, '크롬 경로 확인', '올바른 크롬 경로입니다', QMessageBox.Ok, QMessageBox.Ok)
        except:
            logging.exception("")
            logging.info("크롬 확인", "올바르지 않은 크롬 경로")
            QMessageBox.critical(self.centralwidget, '크롬 경로 오류', '크롬 경로를 확인해 주세요', QMessageBox.Ok, QMessageBox.Ok)
    """
    ::END::
    """

    """
    계정 화면 설정
    ::START::
    """
    def on_id_changed(self, text):
        logging.debug(text)
        self.toggleAddButton(False)

    def on_pw_changed(self, text):
        logging.debug(text)
        self.toggleAddButton(False)

    def toggleAddButton(self, enabled=None):
        if enabled is None:
            self.add_btn.setEnabled(not self.add_btn.isEnabled())
        else:
            self.add_btn.setEnabled(enabled)

    def on_validation_account_clicked(self):
        logging.debug("계정 확인")
        id = self.id_edit.text().strip()
        pw = self.pw_edit.text().strip()

        if id != '' and pw != '':
            self.validateAccountThread.id = id
            self.validateAccountThread.pw = pw
            self.validateAccountThread.path = self.chrome_edit.text().strip()
            self.validateAccountThread.start()
        else:
            logging.info("계정 확인", "이메일 혹은 비밀번호가 비어 있음")

    def on_add_account_clicked(self):
        logging.debug("계정 추가")
        id = self.id_edit.text().strip()
        pw = self.pw_edit.text().strip()
        
        for _id, _ in self.accounts:
            if _id == id:
                logging.info("계정 추가", "동일한 이메일이 이미 존재함")
                return
        self.accounts.append((id,pw))
        self.oper_accounts.append((self.OPER_ADD,(id,pw)))

        logging.info("계정 추가", f"{id} 을/를 추가함")

        self.bindToAccountTable()

        self.id_edit.clear()
        self.pw_edit.clear()

        self.toggleAddButton(False)

        self.validateRunButton()

    def on_delete_account_clicked(self):
        logging.debug("계정 삭제")
        
        deletedAccounts = 0
        for _range in self.account_table.selectedRanges():
            topRow = _range.topRow()
            bottomRow = _range.bottomRow()

            for row in range(topRow, bottomRow+1):
                id = self.account_table.item(row, 0).text()
                pw = self.account_table.item(row, 1).text()
                self.accounts.remove((id,pw))
                self.oper_accounts.append((self.OPER_DELETE, (id,pw)))
                deletedAccounts+=1

        logging.info("계정 삭제", f"{deletedAccounts} 개를 삭제 시킴")

        self.bindToAccountTable()

        self.validateRunButton()


    def bindToAccountTable(self):
        self.account_table.clear()
        self.account_table.setColumnCount(2)
        self.account_table.setRowCount(len(self.accounts))
        self.account_table.setHorizontalHeaderLabels(["이메일", "비밀번호"])

        for idx, (id, pw) in enumerate(self.accounts): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 

            self.account_table.setItem(idx, 0, QTableWidgetItem(id)) 
            self.account_table.setItem(idx, 1, QTableWidgetItem(pw)) 

        self.account_table.setSortingEnabled(False)  # 정렬기능
        self.account_table.resizeRowsToContents()
        self.account_table.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.

        logging.info("계정 로딩", f"{len(self.accounts)} 개가 로딩됨")

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
        logging.debug(f"불러온 파일 경로 : {fname[0]}")
        self.chat_image_btn.setText(fname[0])

    def on_add_chat_setting_clicked(self):
        logging.debug("설정 추가")

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

    def on_delete_chat_setting_clicked(self):
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

        logging.info("계정 삭제", f"{deletedSettings} 개를 삭제 시킴")

        connect()
        self.settings = getChatSettings()
        close()
        self.bindToChatSettingTable()

    def bindToChatSettingTable(self):
        self.chat_setting_table.clear()
        self.chat_setting_table.setColumnCount(5)
        self.chat_setting_table.setRowCount(len(self.settings))
        self.chat_setting_table.setHorizontalHeaderLabels(["설정 이름", "채팅방 이름", "채팅방 이미지", ])

        for idx, (id, name, chatName, chatImage, chatReadersView, chatMessagePeriod) in enumerate(self.settings): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 

            self.chat_setting_table.setItem(idx, 0, QTableWidgetItem(name)) 
            self.chat_setting_table.setItem(idx, 1, QTableWidgetItem(chatName)) 
            self.chat_setting_table.setItem(idx, 2, QTableWidgetItem(chatImage)) 
            self.chat_setting_table.setItem(idx, 3, QTableWidgetItem("읽음 멤버 보기" if chatReadersView == 1 else "읽은 멤버 보지 않기")) 
            self.chat_setting_table.setItem(idx, 4, QTableWidgetItem(chatMessagePeriod)) 

        self.chat_setting_table.setSortingEnabled(False)  # 정렬기능
        self.chat_setting_table.resizeRowsToContents()
        self.chat_setting_table.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.

        logging.info("계정 로딩", f"{len(self.settings)} 개가 로딩됨")

    """
    ::END::
    """

    """
    작업 목록 화면
    ::START::
    """
    def on_account_combobox_changed(self, account_id):
        logging.debug(f"선택된 아이디 : {account_id}")
    """
    ::END::
    """

    """
    탭 설정
    ::START::
    """
    def on_tab_changed(self, index):
        logging.debug(f"선택된 탭 : {index}")
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
            pass

    """
    ::END::
    """

    """
    실행/중단 설정
    ::START::
    """
    def on_run_clicked(self):
        logging.debug("실행")
        
    def on_stop_clicked(self):
        logging.debug("중단")

    def validateRunButton(self):
        if len(self.accounts) == 0 or self.current_chat_setting == "설정":
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
    """
    :::END::
    """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
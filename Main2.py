import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from SendMessageMacro import *
from SMMDBHelper import *

import logging

logger = logging.getLogger()
FORMAT = "[%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)

form_class = uic.loadUiType("./ui/send_message_macro.ui")[0]

class MyWindow(QMainWindow, form_class):

    numberOfCheckedBox = 0
    accounts = []
    accounts_to_add = []
    accounts_to_delete = []
    chats = []

    state_validation_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.add_btn.setEnabled(False)

        self.account_table.cellClicked.connect(self._cellclicked)

        # 컬럼 헤더를 click 시에만 정렬하기.
        hheader = self.account_table.horizontalHeader()  # qtablewidget --> qtableview --> horizontalHeader() --> QHeaderView
        hheader.sectionClicked.connect(self._horizontal_header_clicked)

        self.tableWidget.cellClicked.connect(self._cellclicked)

        # 컬럼 헤더를 click 시에만 정렬하기.
        hheader = self.tableWidget.horizontalHeader()  # qtablewidget --> qtableview --> horizontalHeader() --> QHeaderView
        hheader.sectionClicked.connect(self._horizontal_header_clicked)
        hheader.sectionDoubleClicked.connect(self._horizontal_header_double_clicked)

        self.getChatThread = GetChatThread(parent=self)
        self.getChatThread.on_finished_get_chat.connect(self.on_finished_get_chat)
        self.getChatThread.on_error_get_chat.connect(self.on_error_get_chat)

        self.sendMessageThread = SendMessageThread(parent=self)
        self.sendMessageThread.on_finished_send_msg.connect(self.on_finished_send_msg)
        self.sendMessageThread.on_error_send_msg.connect(self.on_error_send_msg)

        self.validateAccountThread = ValidateAccountThread(parent=self)
        self.validateAccountThread.state_logged_in.connect(self.state_logged_in)
        self.validateAccountThread.state_login_success.connect(self.state_login_success)
        self.validateAccountThread.state_login_fail.connect(self.state_login_fail)
        self.validateAccountThread.state_login_error.connect(self.state_login_error)
        self.validateAccountThread.state_login_validation.connect(self.state_login_validation)

        self.pdialog = QProgressDialog('시간이 걸릴 수 있습니다', '취소', 0, 0, self)
        self.pdialog.cancel()
        self.pdialog.setWindowTitle('채팅 정보 불러오는 중...')
        self.pdialog.canceled.connect(self.on_dialog_canceled)

        self.account_combobox.activated[str].connect(self.onComboBoxActivated)
        self.currentId = self.account_combobox.currentText()

        self.loadAccounts()

    def state_login_validation(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("휴대폰 인증 후 아래 확인 버튼을 눌러 주세요")
        msgBox.setWindowTitle("휴대폰 인증 요청")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.buttonClicked.connect(lambda _ : self.state_validation_finished.emit())
        msgBox.exec()

    def validate_account(self):
        id = self.id_edit.text().strip()
        pw = self.pw_edit.text().strip()

        if id != '' and pw != '':
            self.validateAccountThread.id = id
            self.validateAccountThread.pw = pw
            self.validateAccountThread.start()

    def onComboBoxActivated(self, text):
        self.currentId = text
        connect()
        self.chats = getChatsWithoutId(self.currentId)
        close()
        self.bindToChatTable()

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
        QMessageBox.critical(self, '로그인 실패', '아이디 또는 비밀번호를 확인해 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_error(self):
        self.toggleAddButton(False)
        QMessageBox.critical(self, '로그인 오류', '로그인 시도 중 문제가 발생하였습니다', QMessageBox.Ok, QMessageBox.Ok)

    def add_account(self):
        id = self.id_edit.text().strip()
        pw = self.pw_edit.text().strip()
        self.accounts.append((id,pw))
        self.accounts_to_add.append((id,pw))

        self.bindToAccountTable()

        self.id_edit.clear()
        self.pw_edit.clear()

        self.toggleAddButton(False)

    def save_account(self):
        connect()
        logging.info(self.accounts)
        addAccounts(self.accounts_to_add)
        deleteAccounts(self.accounts_to_delete)

        self.accounts = getAccounts()

        self.bindToAccountComboBox()
        close()

    def delete_account(self):
        for _range in self.account_table.selectedRanges():
            topRow = _range.topRow()
            bottomRow = _range.bottomRow()

            for row in range(topRow, bottomRow+1):
                id = self.account_table.item(row, 0).text()
                pw = self.account_table.item(row, 1).text()
                self.accounts.remove((id,pw))
                self.accounts_to_delete.append((id,pw))

        self.bindToAccountTable()

    def save_chat(self):
        connect()
        logging.info(self.chats)
        clearChats()
        addChats(self.chats)
        self.accounts = getChats()
        close()

    def delete_chat(self):
        for _range in self.tableWidget.selectedRanges():
            topRow = _range.topRow()
            bottomRow = _range.bottomRow()

            indexes = []
            for row in range(topRow, bottomRow+1):
                chat_url = self.tableWidget.item(row, 3).text()
                logging.info(f"chat_url : {chat_url}")
                for i, chat in enumerate(self.chats):
                    if chat[2] == chat_url: 
                        del self.chats[i]
                        break
                logging.info(f"chat_url : {self.chats}")
                

        self.bindToChatTable()

    def run(self):
        chat_urls = []
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i,0).isChecked():
                chat_urls.append(self.tableWidget.item(i, 3).text())
        self.sendMessageThread.content = self.content_edit.toPlainText().strip()
        self.sendMessageThread.chat_urls = chat_urls
        connect()
        account = getAccountById(self.currentId)
        close()
        self.sendMessageThread.id = account[0]
        self.sendMessageThread.pw = account[1]
        self.sendMessageThread.start()
        self.toggleRunButton(False)
        self.toggleStopButton(True)

    def stop(self):
        if self.sendMessageThread.isRunning():
            self.sendMessageThread.stop()
        self.toggleStopButton(False)
        self.toggleRunButton(True)

    def find(self):
        self.keyword = self.keyword_edit.text()
        if self.keyword != '':
            self.loadChats()

    def on_dialog_canceled(self):
        if self.getChatThread.isRunning():
            self.getChatThread.stop()

    def on_text_changed(self):
        self.validateRunButton()

    def on_id_edit_changed(self,text):
        self.toggleAddButton(False)

    def on_pw_edit_changed(self,text):
        self.toggleAddButton(False)

    def bindToAccountTable(self):
        self.account_table.clear()
        self.account_table.setColumnCount(2)
        self.account_table.setRowCount(len(self.accounts))
        self.account_table.setHorizontalHeaderLabels(["아이디", "비밀번호"])

        for idx, (id, pw) in enumerate(self.accounts): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 

            self.account_table.setItem(idx, 0, QTableWidgetItem(id)) 
            self.account_table.setItem(idx, 1, QTableWidgetItem(pw)) 

        self.account_table.setSortingEnabled(False)  # 정렬기능
        self.account_table.resizeRowsToContents()
        self.account_table.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.

    def bindToAccountComboBox(self):
        self.account_combobox.clear()
        self.account_combobox.addItem("계정")

        for (id, pw) in self.accounts:
            self.account_combobox.addItem(id)

    def bindToChatTable(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(len(self.chats))
        self.tableWidget.setHorizontalHeaderLabels(["", "밴드 이름", "채팅 이름", "채팅 주소"])

        for idx, (band_title, chat_title, chat_url, account_id) in enumerate(self.chats): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 
            item = MyQTableWidgetItemCheckBox() 
            self.tableWidget.setItem(idx, 0, item) 
            chbox = MyCheckBox(item) 
            self.tableWidget.setCellWidget(idx, 0, chbox) 

            chbox.stateChanged.connect(self.__checkbox_change) # sender() 확인용 예.. 
            
            self.tableWidget.setItem(idx, 1, QTableWidgetItem(band_title)) 
            self.tableWidget.setItem(idx, 2, QTableWidgetItem(chat_title)) 
            self.tableWidget.setItem(idx, 3, QTableWidgetItem(chat_url)) 

        self.tableWidget.setSortingEnabled(False)  # 정렬기능
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.
        self.tableWidget.setColumnWidth(0, 15)  # checkbox 컬럼 폭 강제 조절.


    def loadAccounts(self):
        connect()
        self.accounts = getAccounts()
        close()
        self.bindToAccountTable()
        self.bindToAccountComboBox()

    def loadChats(self):
        self.pdialog.show()
        connect()
        account = getAccountById(self.currentId)
        close()
        logging.info(f"id : {account[0]}, pw : {account[1]}")
        self.getChatThread.id = account[0]
        self.getChatThread.pw = account[1]
        self.getChatThread.keyword = self.keyword
        self.getChatThread.start()

    @pyqtSlot()
    def on_finished_send_msg(self):
        self.toggleStopButton(False)
        self.validateRunButton()

    @pyqtSlot()
    def on_error_send_msg(self):
        pass 

    @pyqtSlot()
    def on_error_get_chat(self):
        pass

    @pyqtSlot(list)
    def on_finished_get_chat(self, chats):
        self.chats.extend(chats)
        self.pdialog.cancel()
        
        self.bindToChatTable()
        
    def __checkbox_change(self, checkvalue):
        logging.info(checkvalue)
        # print("check change... ", checkvalue)
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        logging.info(f"현재 행 : {chbox.get_row()}")

        if checkvalue:
            self.numberOfCheckedBox += 1
   
        else:
            self.numberOfCheckedBox -= 1

        logging.info(f"체크된 상자 개수 : {self.numberOfCheckedBox}")

        self.validateRunButton()

    def validateRunButton(self):
        if self.numberOfCheckedBox == 0 or self.content_edit.toPlainText().strip()=='':
            self.toggleRunButton(False)
        else:
            self.toggleRunButton(True)

    def toggleAddButton(self, enabled=None):
        if enabled is None:
            self.add_btn.setEnabled(not self.add_btn.isEnabled())
        else:
            self.add_btn.setEnabled(enabled)

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

    def _cellclicked(self, row, col):
        logging.debug(f"_cellclicked... {row}, {col}")

    def _horizontal_header_clicked(self, idx):
        """
        컬럼 헤더 click 시에만, 정렬하고, 다시 정렬기능 off 시킴
         -- 정렬기능 on 시켜놓으면, 값 바뀌면 바로 자동으로 data 순서 정렬되어 바뀌어 헷갈린다..
        :param idx -->  horizontalheader index; 0, 1, 2,...
        :return:
        """
        senderName = self.sender().objectName()
        if senderName == 'tableWidget':
            # print("hedder2.. ", idx)
            if idx == 0:
                return

        self.tableWidget.setSortingEnabled(True)  # 정렬기능 on
        # time.sleep(0.2)
        self.tableWidget.setSortingEnabled(False)  # 정렬기능 off
    
    def _horizontal_header_double_clicked(self, idx):
        #logging.debug(idx)
        
        if idx == 0:
            notAllChecked = self.numberOfCheckedBox != self.tableWidget.rowCount()
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.cellWidget(i,0).setChecked(notAllChecked)

class MyCheckBox(QCheckBox):
    def __init__(self, item):
        """
        :param item: QTableWidgetItem instance
        """
        super().__init__()
        self.item = item
        self.mycheckvalue = 0   # 0 --> unchecked, 2 --> checked
        self.stateChanged.connect(self.__checkbox_change)
        self.stateChanged.connect(self.item.my_setdata)  # checked 여부로 정렬을 하기위한 data 저장

    def __checkbox_change(self, checkvalue):
        # print("myclass...check change... ", checkvalue)
        self.mycheckvalue = checkvalue
        # print("checkbox row= ", self.get_row())

    def get_row(self):
        return self.item.row()


class MyQTableWidgetItemCheckBox(QTableWidgetItem): 
    """ 
    checkbox widget 과 같은 cell 에 item 으로 들어감. 
    checkbox 값 변화에 따라, 사용자정의 data를 기준으로 정렬 기능 구현함. 
    """ 
    def __init__(self): 
        super().__init__() 
        self.setData(Qt.UserRole, 0) 
        
    def __lt__(self, other): 
        # logging.debug(type(self.data(Qt.UserRole))) 
        return self.data(Qt.UserRole) < other.data(Qt.UserRole) 
        
    def my_setdata(self, value): 
        logging.debug(f"my setdata {value}") 
        self.setData(Qt.UserRole, value) 
        logging.debug(f"row {self.row()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
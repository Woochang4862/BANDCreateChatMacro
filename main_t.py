import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from CreateChatMacro import *
from LoginMacro import *
from DBHelper import *

form_class = uic.loadUiType("./create_chat_macro.ui")[0]

driver = setup_driver()

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def validateAccount(self):
        id = self.edit_id.text().strip()
        pw = self.edit_pw.text().strip()
        if id == "" or pw == "":
            QMessageBox.warning(self.centralwidget, '경고', '빈칸을 모두 채워주세요', QMessageBox.Ok, QMessageBox.Ok)
            return
        self.validateAccountThread = ValidateAccountThread(parent=self, id=id, pw=pw)
        self.validateAccountThread.state_logged_in.connect(self.state_logged_in)
        self.validateAccountThread.state_login_success.connect(self.state_login_success)
        self.validateAccountThread.state_login_fail.connect(self.state_login_fail)
        self.validateAccountThread.state_login_error.connect(self.state_login_error)
        self.validateAccountThread.start()

    @pyqtSlot()
    def state_logged_in(self):
        QMessageBox.warning(self.centralwidget, '로그인 상태', '로그아웃 후 다시 시도해 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_success(self):
        QMessageBox.information(self.centralwidget, '로그인 성공', '아래 추가 버튼을 눌러 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_fail(self):
        QMessageBox.critical(self, '로그인 실패', '아이디 또는 비밀번호를 확인해 주세요', QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot()
    def state_login_error(self):
        pass

    def addAccount(self):
        pass

    def addBandUrl(self):
        pass

    def addChatSetting(self):
        pass

    def addTask(self):
        pass

    def openImagePicker(self):
        pass

    def validateBandUrl(self):
        pass

    def save(self):
        pass

    def export(self):
        pass

    def open(self):
        pass

    def removeSelected(self):
        pass

    def removeAll(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
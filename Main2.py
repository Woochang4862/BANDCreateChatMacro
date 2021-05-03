import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from SendMessageMacro import *

import logging

logger = logging.getLogger()
FORMAT = "[%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)

form_class = uic.loadUiType("./send_message_macro.ui")[0]

class MyWindow(QMainWindow, form_class):

    numberOfCheckedBox = 0
    checkedRow = set()
    checkBoxes = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.getChatThread = GetChatThread(parent=self)
        self.getChatThread.on_finished_get_chat.connect(self.on_finished_get_chat)
        self.getChatThread.on_error_get_chat.connect(self.on_error_get_chat)
        self.sendMessageThread = SendMessageThread(parent=self)
        self.sendMessageThread.on_finished_send_msg.connect(self.on_finished_send_msg)
        self.sendMessageThread.on_error_send_msg.connect(self.on_error_send_msg)
        self.pdialog = QProgressDialog('시간이 걸릴 수 있습니다', '취소', 0, 0, self)
        self.pdialog.cancel()
        self.pdialog.setWindowTitle('채팅 정보 불러오는 중...')
        self.pdialog.canceled.connect(self.on_dialog_canceled)

    def run(self):
        chat_urls = []
        for r in list(self.checkedRow):
            chat_urls.append(self.tableWidget.item(r, 3).text())
        self.sendMessageThread.content = self.content_edit.toPlainText().strip()
        self.sendMessageThread.chat_urls = chat_urls
        self.sendMessageThread.id = '01038554671'
        self.sendMessageThread.pw = 'asdf0706'
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
            self.loading()

    def on_dialog_canceled(self):
        if self.getChatThread.isRunning():
            self.getChatThread.stop()

    def on_text_changed(self):
        self.validateRunButton()

    def loading(self):
        self.pdialog.show()
        self.getChatThread.id = '01038554671'
        self.getChatThread.pw = 'asdf0706'
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
        self.pdialog.cancel()
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(len(chats))
        self.tableWidget.setHorizontalHeaderLabels(["", "밴드 이름", "채팅 이름", "채팅 주소"])

        self.checkBoxes.clear()

        for idx, (band_title, chat_title, chat_url) in enumerate(chats): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 
            item = MyQTableWidgetItemCheckBox() 
            self.tableWidget.setItem(idx, 0, item) 
            chbox = MyCheckBox(item) 
            self.tableWidget.setCellWidget(idx, 0, chbox) 
            
            self.checkBoxes.append(chbox)

            chbox.stateChanged.connect(self.__checkbox_change) # sender() 확인용 예.. 
            
            self.tableWidget.setItem(idx, 1, QTableWidgetItem(band_title)) 
            self.tableWidget.setItem(idx, 2, QTableWidgetItem(chat_title)) 
            self.tableWidget.setItem(idx, 3, QTableWidgetItem(chat_url)) 

        logging.debug(f'"{len(self.checkBoxes)}"개의 체크상자 만들어짐')

        self.tableWidget.setSortingEnabled(False)  # 정렬기능
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()  # 이것만으로는 checkbox 컬럼은 잘 조절안됨.
        self.tableWidget.setColumnWidth(0, 15)  # checkbox 컬럼 폭 강제 조절.

        self.tableWidget.cellClicked.connect(self._cellclicked)

        # 컬럼 헤더를 click 시에만 정렬하기.
        hheader = self.tableWidget.horizontalHeader()  # qtablewidget --> qtableview --> horizontalHeader() --> QHeaderView
        hheader.sectionClicked.connect(self._horizontal_header_clicked)
        hheader.sectionDoubleClicked.connect(self._horizontal_header_double_clicked)
        
    def __checkbox_change(self, checkvalue):
        # print("check change... ", checkvalue)
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        logging.debug(f"바뀐 행 : {chbox.get_row()}")

        if checkvalue:
            self.numberOfCheckedBox += 1
            self.checkedRow.add(chbox.get_row())
   
        else:
            self.numberOfCheckedBox -= 1
            self.checkedRow.remove(chbox.get_row())

        logging.debug(f"체크된 행 : {self.checkedRow}")

        self.validateRunButton()

        logging.debug(f'체크된 상자 개수 : {self.numberOfCheckedBox}')

    def validateRunButton(self):
        if self.numberOfCheckedBox == 0 or self.content_edit.toPlainText().strip()=='':
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

    def _cellclicked(self, row, col):
        logging.debug(f"_cellclicked... {row}, {col}")

    def _horizontal_header_clicked(self, idx):
        """
        컬럼 헤더 click 시에만, 정렬하고, 다시 정렬기능 off 시킴
         -- 정렬기능 on 시켜놓으면, 값 바뀌면 바로 자동으로 data 순서 정렬되어 바뀌어 헷갈린다..
        :param idx -->  horizontalheader index; 0, 1, 2,...
        :return:
        """
        # print("hedder2.. ", idx)
        if idx == 0:
            return

        self.tableWidget.setSortingEnabled(True)  # 정렬기능 on
        # time.sleep(0.2)
        self.tableWidget.setSortingEnabled(False)  # 정렬기능 off
    
    def _horizontal_header_double_clicked(self, idx):
        #logging.debug(idx)
        
        logging.debug(f'체크박스 개수 : {self.numberOfCheckedBox}, 체크된 행 : {self.checkedRow}')
        if idx == 0:
            if self.numberOfCheckedBox == len(self.checkBoxes):
                for chbox in self.checkBoxes: 
                    chbox.setChecked(False)

            else:
                for chbox in self.checkBoxes:
                    chbox.setChecked(True)


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
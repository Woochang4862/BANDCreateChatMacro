import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from SendMessageMacro import *

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

form_class = uic.loadUiType("./send_message_macro.ui")[0]

class MyWindow(QMainWindow, form_class):

    numberOfCheckedBox = 0

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.getChatThread = GetChatThread(parent=self)
        self.pdialog = QProgressDialog('시간이 걸릴 수 있습니다', '취소', 0, 0, self)
        self.pdialog.cancel()
        self.pdialog.setWindowTitle('채팅 정보 불러오는 중...')
        self.pdialog.canceled.connect(self.on_dialog_canceled)

    def run(self):
        pass

    def stop(self):
        pass

    def find(self):
        self.keyword = self.keyword_edit.text()
        if self.keyword != '':
            self.loading()

    def on_dialog_canceled(self):
        if self.getChatThread.isRunning():
            self.getChatThread.stop()

    def loading(self):
        self.pdialog.show()
        self.getChatThread.id = '01038554671'
        self.getChatThread.pw = 'asdf0706'
        self.getChatThread.keyword = self.keyword
        self.getChatThread.on_finished.connect(self.on_finished)
        self.getChatThread.start()

    @pyqtSlot(list)
    def on_finished(self, chats):
        self.pdialog.cancel()
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(len(chats))
        self.tableWidget.setHorizontalHeaderLabels(["", "밴드 이름", "채팅 이름", "채팅 주소"])

        for idx, (band_title, chat_title, chat_url) in enumerate(chats): # 사용자정의 item 과 checkbox widget 을, 동일한 cell 에 넣어서 , 추후 정렬 가능하게 한다. 
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

        self.tableWidget.cellClicked.connect(self._cellclicked)

        # 컬럼 헤더를 click 시에만 정렬하기.
        hheader = self.tableWidget.horizontalHeader()  # qtablewidget --> qtableview --> horizontalHeader() --> QHeaderView
        hheader.sectionClicked.connect(self._horizontal_header_clicked)
        hheader.sectionDoubleClicked.connect(self._horizontal_header_double_clicked)
        
    def __checkbox_change(self, checkvalue):
        # print("check change... ", checkvalue)
        chbox = self.sender()  # signal을 보낸 MyCheckBox instance
        logging.info(f"checkbox sender row = {chbox.get_row()}")

        # TODO : 모든 체크박스 검사 -> 적어도 하나가 체크되어 있으면 isCheckedAtLeast = True
        if checkvalue:
            self.numberOfCheckedBox += 1
        else:
            self.numberOfCheckedBox -= 1

        logging.info(f'체크된 상자 개수 : {self.numberOfCheckedBox}')

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
        self.tableWidget.setSortingEnabled(True)  # 정렬기능 on
        # time.sleep(0.2)
        self.tableWidget.setSortingEnabled(False)  # 정렬기능 off
    
    def _horizontal_header_double_clicked(self, idx):
        #logging.info(idx)
        
        if idx == 0:
            if self.numberOfCheckedBox > 0:
                for row in range(self.tableWidget.rowCount()): 
                    chbox = self.tableWidget.cellWidget(row, 0)
                    if isinstance(chbox, MyCheckBox):
                        chbox.setCheckState(2)

            else:
                for row in range(self.tableWidget.rowCount()): 
                    chbox = self.tableWidget.cellWidget(row, 0)
                    if isinstance(chbox, MyCheckBox):
                        chbox.setCheckState(0)


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
        print("checkbox row= ", self.get_row())

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
        logging.info(type(self.data(Qt.UserRole))) 
        return self.data(Qt.UserRole) < other.data(Qt.UserRole) 
        
    def my_setdata(self, value): 
        logging.info(f"my setdata {value}") 
        self.setData(Qt.UserRole, value) 
        logging.info(f"row {self.row()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
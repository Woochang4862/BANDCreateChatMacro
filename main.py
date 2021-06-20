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
    변수
    ::START::
    """
    accounts = []
    oper_accounts = deque([])
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
        메뉴바
        ::START::
        """
        self.actionSave.triggered.connect(self.on_save_clicked)
        """
        ::END::
        """

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
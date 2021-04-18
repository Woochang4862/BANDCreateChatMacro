import sqlite3
import os

DB_NAME = "create_chat_macro.db"

TABLE_ACCOUNT = "account"
ACCOUNT_ID = "_id"
ACCOUNT_PW = "pw"

TABLE_BAND = "band"
BAND_ID = "_id"
BAND_NAME = "name"
BAND_URL = "url"

TABLE_CHAT_SETTING = "chat_setting"
CHAT_SETTING_ID = "_id"
CHAT_SETTING_NAME = "name"
CHAT_SETTING_CHAT_NAME = "chat_name"
CHAT_SETTING_CHAT_IMAGE = "chat_image"
CHAT_SETTING_READERS_VIEW = "readers_view"
CHAT_SETTING_MESSAGE_PERIOD = "message_period"

TABLE_TASK = "task"
TASK_ID = "_id"
TASK_NAME = "name"
TASK_ACCOUNT_ID = "account_id"
TASK_BAND_ID = "band_id"
TASK_CHAT_SETTING_ID = "chat_setting_id"
TASK_REMAININGS = "remainings"

TABLE_MEMBERS = "members"
MEMBERS_ID = "_id"
MEMBERS_BAND_ID = "band_id"
MEMBERS_CHAT_ID = "chat_id"

def connect():
    global con
    global cursor
    if os.path.isfile(DB_NAME):
        con = sqlite3.connect(f"./{DB_NAME}")
        cursor = con.cursor()
    else:
        con = sqlite3.connect(f"./{DB_NAME}")
        cursor = con.cursor()
        cursor.execute(f"CREATE TABLE {TABLE_ACCOUNT}({ACCOUNT_ID} text primary key, {ACCOUNT_PW} text)")
        cursor.execute(f"CREATE TABLE {TABLE_BAND}({BAND_ID} integer primary key autoincrement, {BAND_NAME} text, {BAND_URL} text)")
        cursor.execute(f"CREATE TABLE {TABLE_CHAT_SETTING}({CHAT_SETTING_ID} integer primary key autoincrement, {CHAT_SETTING_NAME} text, {CHAT_SETTING_CHAT_NAME} text, {CHAT_SETTING_CHAT_IMAGE} text, {CHAT_SETTING_READERS_VIEW} integer default 1, {CHAT_SETTING_MESSAGE_PERIOD} text)")
        cursor.execute(f"CREATE TABLE {TABLE_TASK}({TASK_ID} integer primary key autoincrement, {TASK_NAME} text, {TASK_ACCOUNT_ID} integer, {TASK_BAND_ID} integer, {TASK_CHAT_SETTING_ID} integer, {TASK_REMAININGS} integer default 0)")
        cursor.execute(f"CREATE TABLE {TABLE_MEMBERS}({MEMBERS_ID} integer primary key, {MEMBERS_BAND_ID} integer, {MEMBERS_CHAT_ID} integer)")

def close():
    con.close()

def addAccount(id, pw):
    cursor.execute(f"INSERT INTO {TABLE_ACCOUNT} ({ACCOUNT_ID}, {ACCOUNT_PW}) VALUES('{id}', '{pw}')")
    con.commit()

def addBand(name, url):
    cursor.execute(f"INSERT INTO {TABLE_BAND} ({BAND_NAME}, {BAND_URL}) VALUES('{name}', '{url}')")
    con.commit()

def addChatSetting(name, chatName, chatImage, chatReadersView, chatMessagePeriod):
    cursor.execute(f"INSERT INTO {TABLE_CHAT_SETTING} ({CHAT_SETTING_NAME}, {CHAT_SETTING_CHAT_NAME}, {CHAT_SETTING_CHAT_IMAGE}, {CHAT_SETTING_READERS_VIEW}, {CHAT_SETTING_MESSAGE_PERIOD}) VALUES('{name}', '{chatName}', '{chatImage}', '{chatReadersView}', '{chatMessagePeriod}')")
    con.commit()

def addTask(name, account_id, band_id, setting_id):
    cursor.execute(f"INSERT INTO {TABLE_TASK} ({TASK_NAME}, {TASK_ACCOUNT_ID}, {TASK_BAND_ID}, {TASK_CHAT_SETTING_ID}) VALUES('{name}', '{account_id}', '{band_id}', '{setting_id}')")
    con.commit()

def addMember(member_id, band_id, chat_id):
    cursor.execute(f"INSERT INTO {TABLE_MEMBERS} ({MEMBERS_ID}, {MEMBERS_BAND_ID}, {MEMBERS_CHAT_ID}) VALUES('{member_id}', '{band_id}', '{chat_id}')")
    con.commit()

def getAccounts():
    cursor.execute(f"SELECT * FROM {TABLE_ACCOUNT}")

connect()
addAccount('chad0706', 'asdf0706')
addBand('세상을 바꾸는 시간 15분', 'https://band.us/band/60518206')
addChatSetting('테스트 세팅', '테스트', r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg', 1 if True else 0, 'min')
addTask('테스트 작업', 0, 0, 0)
close()
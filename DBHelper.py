import sqlite3
import os

DB_NAME = "create_chat_macro.db"

TABLE_ACCOUNT = "account"
ACCOUNT_ID = "_id"
ACCOUNT_PW = "pw"

TABLE_BAND = "band"
BAND_ID = "_id"
BAND_ACCOUNT_ID = "account_id"
BAND_NAME = "name"
BAND_URL = "url"
BAND_COMPLETED = "completed"

TABLE_CHAT_SETTING = "chat_setting"
CHAT_SETTING_ID = "_id"
CHAT_SETTING_NAME = "name"
CHAT_SETTING_CHAT_NAME = "chat_name"
CHAT_SETTING_CHAT_IMAGE = "chat_image"
CHAT_SETTING_READERS_VIEW = "readers_view"
CHAT_SETTING_MESSAGE_PERIOD = "message_period"

TABLE_MEMBER = "member"
MEMBER_ID = "_id"
MEMBER_ACCOUNT_ID = "account_id"
MEMBER_BAND_ID = "band_id"
MEMBER_CHAT_ID = "chat_id"
MEMBER_DATE = "date"

def connect():
    global con
    global cursor
    con = sqlite3.connect(f"./{DB_NAME}")
    cursor = con.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_ACCOUNT}({ACCOUNT_ID} text primary key, {ACCOUNT_PW} text)")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS  {TABLE_BAND}({BAND_ID} integer primary key, {BAND_ACCOUNT_ID} text, {BAND_NAME} text, {BAND_URL} text, {BAND_COMPLETED} integer default 0, foreign key({BAND_ACCOUNT_ID}) references {TABLE_ACCOUNT}({ACCOUNT_ID}))")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_CHAT_SETTING}({CHAT_SETTING_ID} integer primary key autoincrement, {CHAT_SETTING_NAME} text, {CHAT_SETTING_CHAT_NAME} text, {CHAT_SETTING_CHAT_IMAGE} text, {CHAT_SETTING_READERS_VIEW} integer default 1, {CHAT_SETTING_MESSAGE_PERIOD} text)")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_MEMBER}({MEMBER_ID} integer primary key, {MEMBER_ACCOUNT_ID} text, {MEMBER_BAND_ID} integer, {MEMBER_CHAT_ID} text, {MEMBER_DATE} text, foreign key({MEMBER_ACCOUNT_ID}) references {TABLE_ACCOUNT}({ACCOUNT_ID}), foreign key({MEMBER_BAND_ID}) references {TABLE_BAND}({BAND_ID}))")
    cursor.execute("PRAGMA foreign_keys=1")

def close():
    con.close()

def addAccount(id, pw):
    cursor.execute(f"INSERT INTO {TABLE_ACCOUNT} ({ACCOUNT_ID}, {ACCOUNT_PW}) SELECT '{id}','{pw}' WHERE NOT EXISTS ( SELECT *  FROM {TABLE_ACCOUNT} WHERE  {ACCOUNT_ID} =  '{id}')")
    con.commit()

def deleteAccount(id):
    #cursor.execute(f"DELETE FROM {TABLE_CHAT} WHERE {ACCOUNT_ID}='{id}'")
    cursor.execute(f"DELETE FROM {TABLE_BAND} WHERE {ACCOUNT_ID} = '{id}'")
    cursor.execute(f"DELETE FROM {TABLE_MEMBER} WHERE {ACCOUNT_ID} = '{id}'")
    cursor.execute(f"DELETE FROM {TABLE_ACCOUNT} WHERE {ACCOUNT_ID}='{id}'")
    con.commit()

def deleteAccounts(accounts):
    for account in accounts:
        deleteAccount(account[0])

def addBand(id, account_id, name, url):
    cursor.execute(f"INSERT INTO {TABLE_BAND} ({BAND_ID}, {BAND_ACCOUNT_ID}, {BAND_NAME}, {BAND_URL}) VALUES('{id}', '{account_id}', '{name}', '{url}')")
    con.commit()

def updateBandCompleted(account_id, band_id, completed):
    cursor.execute(f"UPDATE {TABLE_BAND} SET {BAND_COMPLETED} = {completed} WHERE {BAND_ACCOUNT_ID} = '{account_id}', {BAND_ID} = {id};")
    con.commit()

def addChatSetting(name, chatName, chatImage, chatReadersView, chatMessagePeriod):
    cursor.execute(f"INSERT INTO {TABLE_CHAT_SETTING} ({CHAT_SETTING_NAME}, {CHAT_SETTING_CHAT_NAME}, {CHAT_SETTING_CHAT_IMAGE}, {CHAT_SETTING_READERS_VIEW}, {CHAT_SETTING_MESSAGE_PERIOD}) VALUES('{name}', '{chatName}', '{chatImage}', '{chatReadersView}', '{chatMessagePeriod}')")
    con.commit()
    return cursor.lastrowid

def deleteChatSetting(id):
    #cursor.execute(f"DELETE FROM {TABLE_CHAT} WHERE {ACCOUNT_ID}='{id}'")
    cursor.execute(f"DELETE FROM {TABLE_CHAT_SETTING} WHERE {CHAT_SETTING_ID}='{id}'")
    con.commit()

def deleteChatSettings(ids):
    for id in ids:
        deleteChatSetting(id)

def addMember(member_id, account_id, band_id, chat_id, date):
    cursor.execute(f"INSERT INTO {TABLE_MEMBER} ({MEMBER_ID}, {MEMBER_ACCOUNT_ID}, {MEMBER_BAND_ID}, {MEMBER_CHAT_ID}, {MEMBER_DATE}) VALUES('{member_id}', '{account_id}', '{band_id}', '{chat_id}', '{date}')")
    con.commit()

def addMembers(members):
    for (id, account_id, band_id, chat_id, date) in members: 
        addMember(id, account_id, band_id, chat_id, date)

def getMembers(account_id):
    cursor.execute(f"SELECT * FROM {TABLE_MEMBER} WHERE {MEMBER_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchall()

def hasMember(account_id, member_id):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_MEMBER} WHERE {MEMBER_ID} = {member_id} AND {MEMBER_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchone()[0] != 0

def getRemainings(account_id, date):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_MEMBER} WHERE {MEMBER_ACCOUNT_ID} = '{account_id}' AND {MEMBER_DATE} = '{date}'")
    return 1000 - cursor.fetchone()[0]

def hasBand(account_id, band_id):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_BAND} WHERE {BAND_ID} = {band_id} AND {BAND_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchone()[0] != 0

def isCompleted(account_id, band_id):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_BAND} WHERE {BAND_ID} = {band_id} AND {BAND_ACCOUNT_ID} = '{account_id}' AND {BAND_COMPLETED} = 1")
    return cursor.fetchone()[0] != 0

def getAccounts():
    cursor.execute(f"SELECT * FROM {TABLE_ACCOUNT}")
    return cursor.fetchall()

def getChatSettings():
    cursor.execute(f"SELECT * FROM {TABLE_CHAT_SETTING}")
    return cursor.fetchall()

def getChatSetting(setting_id):
    cursor.execute(f"SELECT * FROM {TABLE_CHAT_SETTING} WHERE {CHAT_SETTING_ID} = {setting_id}")
    return cursor.fetchall()[0]

connect()
#addAccount('chad0706@naver.com', 'asdf0706')
#addBand('세상을 바꾸는 시간 15분', 'https://band.us/band/60518206')
#addChatSetting('테스트 세팅', '테스트', r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg', 1 if True else 0, 'min')
close()
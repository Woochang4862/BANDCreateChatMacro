import sqlite3
import os

DB_NAME = "send_message_macro.db"

TABLE_ACCOUNT = "account"
ACCOUNT_ID = "_id"
ACCOUNT_PW = "pw"

TABLE_CHAT = "chat"
CHAT_ID = "_id"
CHAT_BAND_NAME = "chat_band_name"
CHAT_NAME = "chat_name"
CHAT_URL = "chat_url"

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
        cursor.execute(f"CREATE TABLE {TABLE_CHAT}({CHAT_ID} integer primary key autoincrement, {CHAT_BAND_NAME} text, {CHAT_NAME} text, {CHAT_URL} text)")

def close():
    con.close()

def clearAccounts():
    cursor.execute(f'DELETE FROM {TABLE_ACCOUNT}')
    con.commit

def addAccount(id, pw):
    cursor.execute(f"INSERT INTO {TABLE_ACCOUNT} ({ACCOUNT_ID}, {ACCOUNT_PW}) SELECT '{id}','{pw}' WHERE NOT EXISTS ( SELECT *  FROM {TABLE_ACCOUNT} WHERE  {ACCOUNT_ID} =  '{id}')")
    con.commit()

def addChat(bandName, chatName, url):
    cursor.execute(f"INSERT INTO {TABLE_CHAT} ({CHAT_BAND_NAME}, {CHAT_NAME}, {CHAT_URL}) VALUES('{bandName}', '{chatName}', '{url}')")
    con.commit()

def getAccounts():
    cursor.execute(f"SELECT * FROM {TABLE_ACCOUNT}")
    rows = cursor.fetchall()
    return rows

def getChats():
    cursor.execute(f"SELECT * FROM {TABLE_CHAT}")
    rows = cursor.fetchall()
    return rows

def getChatsWithoutId():
    cursor.execute(f"SELECT {CHAT_BAND_NAME}, {CHAT_NAME}, {CHAT_URL} FROM {TABLE_CHAT}")
    rows = cursor.fetchall()
    return rows

def addChats(chats):
    for chat in chats:
        addChat(chat[0], chat[1], chat[2])

def addAccounts(accounts):
    for account in accounts:
        addAccount(account[0], account[1])

connect()
clearAccounts()
#addAccount('b', 'b')
# addBand('테스트', '테스트', 'https://band.us/band/123456/chat/xyz')
#print(getAccounts())
# print(getChats())
close()
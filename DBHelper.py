import sqlite3
import logging

logger = logging.getLogger()
FORMAT = "[%(asctime)s][%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logger.setLevel(logging.DEBUG)

DB_NAME = "create_chat_macro.db"

CURRENT_VERSION = "0.2"
"""
#0.2
계정 테이블에 아이피 추가
"""

TABLE_ACCOUNT = "account"
ACCOUNT_ID = "_id"
ACCOUNT_PW = "pw"
ACCOUNT_IP = "ip"
ACCOUNT_COLUMNS = [ACCOUNT_ID, ACCOUNT_PW, ACCOUNT_IP]

TABLE_BAND = "band"
BAND_ID = "_id"
BAND_ACCOUNT_ID = "account_id"
BAND_NAME = "name"
BAND_URL = "url"
BAND_COMPLETED = "completed"
BAND_LATEST_KEYWORD = "latest_keyword"
BAND_COLUMNS = [BAND_ID, BAND_ACCOUNT_ID, BAND_NAME, BAND_URL, BAND_COMPLETED, BAND_LATEST_KEYWORD]

TABLE_CHAT_SETTING = "chat_setting"
CHAT_SETTING_ID = "_id"
CHAT_SETTING_NAME = "name"
CHAT_SETTING_CHAT_NAME = "chat_name"
CHAT_SETTING_CHAT_IMAGE = "chat_image"
CHAT_SETTING_READERS_VIEW = "readers_view"
CHAT_SETTING_MESSAGE_PERIOD = "message_period"
CHAT_SETTING_COLUMNS = [CHAT_SETTING_ID, CHAT_SETTING_NAME, CHAT_SETTING_CHAT_NAME, CHAT_SETTING_CHAT_IMAGE, CHAT_SETTING_READERS_VIEW, CHAT_SETTING_MESSAGE_PERIOD]

TABLE_MEMBER = "member"
MEMBER_ID = "_id"
MEMBER_ACCOUNT_ID = "account_id"
MEMBER_BAND_ID = "band_id"
MEMBER_CHAT_ID = "chat_id"
MEMBER_DATE = "date"
MEMBER_COLUMNS = [MEMBER_ID, MEMBER_ACCOUNT_ID, MEMBER_BAND_ID, MEMBER_CHAT_ID, MEMBER_DATE]

TABLE_PREFERENCE = "preference"
PREFERENCE_KEY = "preference_key"
PREFERENCE_STRING = "preference_string"
PREFERENCE_INTEGER = "preference_integer"
PREFERENCE_REAL = "preference_real"

"""
PREFERENCE KEY
"""
KEY_CHROME_ROUTE = "key_chrome_route"

def connect():
    global con
    global cursor
    con = sqlite3.connect(f"./{DB_NAME}")
    cursor = con.cursor()
    
    SCHEMA_ACCOUNT = f"({ACCOUNT_ID} text primary key, {ACCOUNT_PW} text, {ACCOUNT_IP} text)"
    SCHEMA_BAND = f"({BAND_ID} integer, {BAND_ACCOUNT_ID} text, {BAND_NAME} text, {BAND_URL} text, {BAND_COMPLETED} integer default 0, {BAND_LATEST_KEYWORD} text, foreign key({BAND_ACCOUNT_ID}) references {TABLE_ACCOUNT}({ACCOUNT_ID}), primary key({BAND_ID}, {BAND_ACCOUNT_ID}))"
    SCHEMA_CHAT_SETTING = f"({CHAT_SETTING_ID} integer primary key autoincrement, {CHAT_SETTING_NAME} text, {CHAT_SETTING_CHAT_NAME} text, {CHAT_SETTING_CHAT_IMAGE} text, {CHAT_SETTING_READERS_VIEW} integer default 1, {CHAT_SETTING_MESSAGE_PERIOD} text)"
    SCHEMA_MEMBER = f"({MEMBER_ID} integer, {MEMBER_ACCOUNT_ID} text, {MEMBER_BAND_ID} integer, {MEMBER_CHAT_ID} text, {MEMBER_DATE} text, foreign key({MEMBER_ACCOUNT_ID}) references {TABLE_ACCOUNT}({ACCOUNT_ID}), foreign key({MEMBER_BAND_ID}, {MEMBER_ACCOUNT_ID}) references {TABLE_BAND}({BAND_ID}, {BAND_ACCOUNT_ID}), primary key({MEMBER_ID}, {MEMBER_ACCOUNT_ID}, {MEMBER_CHAT_ID}, {MEMBER_BAND_ID}))"
    SCHEMA_PREFERENCE = f"({PREFERENCE_KEY} text primary key, {PREFERENCE_STRING} text, {PREFERENCE_INTEGER} integer, {PREFERENCE_REAL} real)"

    CREATE_ACCOUNT = f"CREATE TABLE IF NOT EXISTS \"{TABLE_ACCOUNT}\""+SCHEMA_ACCOUNT
    CREATE_BAND = f"CREATE TABLE IF NOT EXISTS \"{TABLE_BAND}\""+SCHEMA_BAND
    CREATE_CHAT_SETTING = f"CREATE TABLE IF NOT EXISTS \"{TABLE_CHAT_SETTING}\""+SCHEMA_CHAT_SETTING
    CREATE_MEMBER = f"CREATE TABLE IF NOT EXISTS \"{TABLE_MEMBER}\""+SCHEMA_MEMBER
    CREATE_PREFERENCE = f"CREATE TABLE IF NOT EXISTS \"{TABLE_PREFERENCE}\""+SCHEMA_PREFERENCE

    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='schema_versions'")
    if cursor.fetchone()[0] == 0: # 버전 기능이 들어가기 전 (완전히 처음이거나 7/13일 전쯤...)
        cursor.execute(f'CREATE TABLE schema_versions(version text)')
        cursor.execute(f'INSERT INTO schema_versions(version) VALUES({CURRENT_VERSION})')
        con.commit()

        cursor.execute("begin")
        try:
            cursor.execute(f"ALTER TABLE {TABLE_BAND} ADD COLUMN {BAND_LATEST_KEYWORD} text")
            cursor.execute(f"UPDATE schema_versions SET version = '0.1'")
            con.commit()
        except:
            logging.exception("")
            con.rollback()

        checkSchema(TABLE_ACCOUNT, SCHEMA_ACCOUNT, ACCOUNT_COLUMNS)
        checkSchema(TABLE_BAND, SCHEMA_BAND, BAND_COLUMNS)
        checkSchema(TABLE_CHAT_SETTING, SCHEMA_CHAT_SETTING, CHAT_SETTING_COLUMNS)
        checkSchema(TABLE_MEMBER, SCHEMA_MEMBER, MEMBER_COLUMNS)

    cursor.execute(CREATE_ACCOUNT)
    cursor.execute(CREATE_BAND)
    cursor.execute(CREATE_CHAT_SETTING)
    cursor.execute(CREATE_MEMBER)
    cursor.execute(CREATE_PREFERENCE)
    cursor.execute("PRAGMA foreign_keys=1")

    # 버전별 변경 사항 적용해줌 컬럼 -> 속성
    if getDatabaseVersion() == "0.1":
        cursor.execute("begin")
        try:
            cursor.execute(f"ALTER TABLE {TABLE_ACCOUNT} ADD COLUMN {ACCOUNT_IP} text")
            cursor.execute(f"UPDATE schema_versions SET version = '0.2'")
            con.commit()
        except:
            logging.exception("")
            con.rollback()
        
        checkSchema(TABLE_ACCOUNT, SCHEMA_ACCOUNT, ACCOUNT_COLUMNS)

def getDatabaseVersion():
    cursor.execute(f"select max(version) from schema_versions")
    return cursor.fetchone()[0]

def checkSchema(table_name, table_schema, table_columns):
    cursor.execute(f"select * from sqlite_master where type='table' and name='{table_name}';")
    result = cursor.fetchall()[0][4]
    if result[result.index('('):].lower() != table_schema.lower():
        print(table_name)
        cursor.execute("PRAGMA foreign_keys=0")
        cursor.execute("begin")
        try:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS new_{table_name}"+table_schema)
            cursor.execute(f"INSERT INTO new_{table_name}({','.join(table_columns)}) SELECT * FROM {table_name}")
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"ALTER TABLE new_{table_name} RENAME TO {table_name}")
            con.commit()
        except:
            logging.exception("")
            con.rollback()
        finally:
            cursor.execute("PRAGMA foreign_keys=1")

def close():
    cursor.close()
    con.close()

def putStringExtra(key, extra):
    cursor.execute(f"INSERT OR REPLACE INTO {TABLE_PREFERENCE}({PREFERENCE_KEY}, {PREFERENCE_STRING}) VALUES ('{key}', '{extra}')")
    con.commit()

def getStringExtra(key, empty):
    cursor.execute(f"SELECT {PREFERENCE_STRING} FROM {TABLE_PREFERENCE} WHERE {PREFERENCE_KEY} = '{key}'")
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return empty

def addAccount(id, pw, ip):
    cursor.execute(f"INSERT INTO {TABLE_ACCOUNT} ({ACCOUNT_ID}, {ACCOUNT_PW}, {ACCOUNT_IP}) VALUES('{id}','{pw}','{ip}')")
    con.commit()

def deleteAccount(id):
    #cursor.execute(f"DELETE FROM {TABLE_CHAT} WHERE {ACCOUNT_ID}='{id}'")
    cursor.execute(f"DELETE FROM {TABLE_MEMBER} WHERE {MEMBER_ACCOUNT_ID} = '{id}'")
    con.commit()
    cursor.execute(f"DELETE FROM {TABLE_BAND} WHERE {BAND_ACCOUNT_ID} = '{id}'")
    con.commit()
    cursor.execute(f"DELETE FROM {TABLE_ACCOUNT} WHERE {ACCOUNT_ID}='{id}'")
    con.commit()

def deleteAccounts(accounts):
    for account in accounts:
        deleteAccount(account[0])

def addBand(id, account_id, name, url, completed=0):
    cursor.execute(f"INSERT INTO {TABLE_BAND} ({BAND_ID}, {BAND_ACCOUNT_ID}, {BAND_NAME}, {BAND_URL}, {BAND_COMPLETED}) VALUES('{id}', '{account_id}', ?, '{url}', '{completed}')", (name,))
    con.commit()

def getBands(account_id):
    cursor.execute(f"SELECT * FROM {TABLE_BAND} WHERE {BAND_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchall()

def getBand(band_id, account_id):
    cursor.execute(f"SELECT * FROM {TABLE_BAND} WHERE {BAND_ID} = '{band_id}' AND {BAND_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchall()[0]

def updateBandCompleted(account_id, band_id, completed):
    cursor.execute(f"UPDATE {TABLE_BAND} SET {BAND_COMPLETED} = {completed} WHERE {BAND_ACCOUNT_ID} = '{account_id}' AND {BAND_ID} = {band_id};")
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
    print(member_id, account_id, band_id, chat_id, date)
    cursor.execute(f"INSERT INTO {TABLE_MEMBER} ({MEMBER_ID}, {MEMBER_ACCOUNT_ID}, {MEMBER_BAND_ID}, {MEMBER_CHAT_ID}, {MEMBER_DATE}) VALUES('{member_id}', '{account_id}', '{band_id}', '{chat_id}', '{date}')")
    con.commit()

def addMembers(members):
    for (id, account_id, band_id, chat_id, date) in members: 
        addMember(id, account_id, band_id, chat_id, date)

def getMembers(account_id, band_id):
    cursor.execute(f"SELECT * FROM {TABLE_MEMBER} WHERE {MEMBER_ACCOUNT_ID} = '{account_id}' AND {MEMBER_BAND_ID} = '{band_id}'")
    return cursor.fetchall()

def hasMember(account_id, member_id):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_MEMBER} WHERE {MEMBER_ID} = {member_id} AND {MEMBER_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchone()[0] != 0

def getRemainings(account_id, date):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_MEMBER} WHERE {MEMBER_ACCOUNT_ID} = '{account_id}' AND {MEMBER_DATE} = '{date}' AND {MEMBER_CHAT_ID} != 'None'")
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

def getNumberOfMembers(account_id, band_id):
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_MEMBER} WHERE {MEMBER_BAND_ID} = {band_id} AND {MEMBER_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchone()[0]

def getLatestKeyword(account_id, band_id):
    cursor.execute(f"SELECT {BAND_LATEST_KEYWORD} FROM {TABLE_BAND} WHERE {BAND_ID} = {band_id} AND {BAND_ACCOUNT_ID} = '{account_id}'")
    return cursor.fetchone()[0]

def updateLatestKeyword(account_id, band_id, keyword):
    cursor.execute(f"UPDATE {TABLE_BAND} SET {BAND_LATEST_KEYWORD} = '{keyword}' WHERE {BAND_ACCOUNT_ID} = '{account_id}' AND {BAND_ID} = {band_id};")
    con.commit()

connect()
#updateBandCompleted('hungsung0231@gmail.com',71757012,0)
#addAccount('chad0706@naver.com', 'asdf0706')
#addBand(48511215, 'hungsung0232@gmail.com', "윤보영시인의 팬밴드 '커피도 가끔은 사랑이 된다'", 'https://band.us/band/48511215')
#addChatSetting('테스트 세팅', '테스트', r'C:\Users\wooch\OneDrive\바탕 화면\sample.jpg', 1 if True else 0, 'min')
#print(getRemainings('chad0706@naver.com', '2021-06-29'))
#addMember(74767098, 'hungsung0232@gmail.com', 72837984, 'CZmZ77', '2021-06-30')
updateLatestKeyword('hungsung0231@gmail.com', 72038937, '강')
close()
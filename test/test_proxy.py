from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import chromedriver_autoinstaller
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from LoginMacro import loginWithEmail

IP = "3.14.89.188"
PORT = "3128"
PROXY = f"{IP}:{PORT}"

# webdriver.DesiredCapabilities.CHROME['proxy'] = {
#     "httpProxy": PROXY,
#     "ftpProxy": PROXY,
#     "sslProxy": PROXY,
#     "proxyType": "MANUAL"
# }

#subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/ChromeTEMP --daemon')
co = Options()
#co.debugger_address = '127.0.0.1:9222'
co.add_argument('--user-data-dir=C:/ChromeTEMP')
co.add_argument(f'--proxy-server=http://{PROXY}')
co.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")
co.add_argument("app-version=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")

chromedriver_autoinstaller.install(cwd=True)
output = subprocess.check_output(
    r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
    shell=True
)
version = output.decode('utf-8').strip().strip("Version=")

driver = webdriver.Chrome(f"./{version[0:2]}/chromedriver.exe",chrome_options=co)
# URL 열기
# loginWithEmail(driver, 'chad0706@naver.com', 'asdf0706')
driver.get('https://api.ipify.org/')
time.sleep(3)
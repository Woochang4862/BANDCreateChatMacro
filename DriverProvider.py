import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import platform
import logging
import zipfile

logger = logging.getLogger()
FORMAT = "[%(asctime)s][%(filename)s:%(lineno)3s - %(funcName)20s()] %(message)s"
logger.setLevel(logging.DEBUG)

class ChromeDriverException(Exception):
    def __str__(self) -> str:
        return "크롬 드라이버를 얻어오는 중 에러 발생"

def open_chrome_with_debug_mode(path):
    logging.info(f"path : {path}")
    if path == '':
        if platform.architecture()[0] == '32bit':
            return subprocess.Popen(rf'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/ChromeTEMP --daemon')
        else :
            return subprocess.Popen(rf'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/ChromeTEMP --daemon')

    else:
        return subprocess.Popen(f'{path} --remote-debugging-port=9222 --user-data-dir=C:/ChromeTEMP --daemon')

def getChromeVersion(path=None):
    if path is None:
        if platform.architecture()[0] == '32bit':
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
                shell=True
            )

            return output.decode('utf-8').strip().strip("Version=")
        else:
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
                shell=True
            )
            
            return output.decode('utf-8').strip().strip("Version=")

# def download_chrome_driver(chrome_version):
    
#     # get the latest chrome driver version number
#     url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_'+chrome_version[0:2]
#     response = requests.get(url)
#     version_number = response.text

#     # build the donwload url
#     download_url = "https://chromedriver.storage.googleapis.com/" + version_number +"/chromedriver_win32.zip"

#     print(download_url)

#     os.makedirs(f'./{chrome_version[0:2]}/')

#     # download the zip file using the url built above
#     latest_driver_zip = wget.download(download_url,f'./{chrome_version[0:2]}/chromedriver.zip')

#     # extract the zip file
#     with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
#         zip_ref.extractall() # you can specify the destination folder path here
#     # delete the zip file downloaded above
#     os.remove(latest_driver_zip)

def setup_driver(ip):
    try:
        if os.path.exists("demofile.txt"):
            os.remove("demofile.txt")
        PROXY_HOST = ip  # rotating proxy or host
        PROXY_PORT = 3128 # port
        PROXY_USER = 'band-macro-proxy' # username
        PROXY_PASS = 'band-macro-proxy' # password


        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
        co = Options()
        if ip:
            pluginfile = 'proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            co.add_extension(pluginfile)
        co.add_argument('--user-data-dir=C:/ChromeTEMP')
        co.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")
        co.add_argument("app-version=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")
        chromedriver_path = "C:/chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_path, options=co)
        return driver
    except Exception as e:
        logging.exception("DriverProvider.py")
        raise ChromeDriverException(e)
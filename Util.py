class ValidateAccountThread(QThread):
        state_logged_in = pyqtSignal()
        state_login_success = pyqtSignal()
        state_login_fail = pyqtSignal()
        def __init__(self, id, pw, parent=None):
            super().__init__()
            self.id = id
            self.pw = pw
 
        def run(self):
            result = False
            driver.get('https://band.us/home')
            
            time.sleep(3)

            if driver.current_url != 'https://band.us/home': # 로그인이 된 상태
                self.state_logged_in.emit()
            else:
                login_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="header"]/div/div/a[2]'))
                )
                login_btn.click()
                naver_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'uBtn.-icoType.-naver.externalLogin'))
                )
                naver_btn.click()

                """
                네이버 로그인
                """
                user_id = driver.find_element_by_id("id")
                password = driver.find_element_by_id("pw")
                time.sleep(1)

                user_id.click()
                pyperclip.copy(self.id)
                user_id.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)

                password.click()
                pyperclip.copy(self.pw)
                password.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)

                password.submit()
                
                time.sleep(3)

                if driver.current_url == 'https://band.us/':
                    result = True
            
                if result: # 올바른 아이디
                    self.state_login_success.emit()
                else: # 올바르지 못한 아이디
                    self.state_login_fail.emit()
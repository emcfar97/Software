import time
from pathlib import Path
import mysql.connector as sql
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as exceptions
from selenium.webdriver.common.action_chains import ActionChains

CREDENTIALS = ConfigParser(delimiters='=') 
CREDENTIALS.read('credentials.ini')
ROOT = Path(Path().cwd().drive)
SELECT = [
    'SELECT href FROM imageData WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM imageData WHERE site=%s AND ISNULL(path)',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    f'SELECT REPLACE(path, "C:", "{ROOT}"), href, src, site FROM favorites WHERE NOT (checked OR ISNULL(path))',
    f'''
        SELECT REPLACE(save_name, "{ROOT}", "C:"), '/artworks/'||image_id,'pixiv' FROM pixiv_master_image UNION
        SELECT REPLACE(save_name, "{ROOT}", "C:"), '/artworks/'||image_id, 'pixiv' FROM pixiv_manga_image
        ''',
    f'SELECT * FROM imagedata WHERE path=%s'
    ]
INSERT = [
    'INSERT INTO imageData(href, site) VALUES(%s, %s)',
    'INSERT INTO favorites(href, site) VALUES(%s, %s)',
    f'INSERT INTO favorites(path, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s)',
    'INSERT INTO imageData(path, artist, tags, rating, type, hash, src, site) VALUES(%s, CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s)',
    'INSERT INTO comic(path_, parent, page) VALUES(%s, %s, %s)',
    'INSERT INTO imageData(path, artist, tags, rating, type, hash, src, site, href) VALUES(%s, CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s. %s)',
    ]
UPDATE = [
    f'UPDATE imageData SET path=%s, artist=CONCAT(" ", %s, " "), tags=CONCAT(" ", %s, " "), rating=%s, type=%s, src=%s, hash=%s WHERE href=%s',
    f'UPDATE imageData SET path=%s, src=%s, hash=%s, type=%s WHERE href=%s',
    f'UPDATE favorites SET path=REPLACE(%s, "{ROOT}", "C:"), src=%s WHERE href=%s',
    f'INSERT INTO imageData(path, hash, href, site) VALUES(%s, %s, %s, %s)',
    f'UPDATE favorites SET checked=%s, saved=%s WHERE path=%s',
    f'INSERT INTO favorites(path, hash, src, href, site) VALUES(%s, %s, %s, %s, %s)'
    ]
DELETE = [
    'DELETE FROM imageData WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE href=%s AND ISNULL(path)'
    ]

class CONNECT:

    def __init__(self):

        self.DATAB = sql.connect(
            user=CREDENTIALS.get('mysql', 'username'), 
            password=CREDENTIALS.get('mysql', 'password'), 
            database=CREDENTIALS.get('mysql', 'database'), 
            host=CREDENTIALS.get('mysql', 'hostname')
            )
        self.CURSOR = self.DATAB.cursor(buffered=True)

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):

        for _ in range(10):
            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)

                if commit: return self.DATAB.commit()
                if fetch: return self.CURSOR.fetchall()
                return 1

            except sql.errors.ProgrammingError:
            
                break

            except sql.errors.IntegrityError:
                
                if statement.startswith('UPDATE'):
                    index = 0 if 'imageD' in statement else 1
                    self.execute(DELETE[index], (arguments[-1],), commit=1)
                    return 1
                elif statement.startswith('INSERT'): break

            except (sql.errors.OperationalError, sql.errors.DatabaseError):
                
                self.reconnect()

        return 0
            
    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=5, time=15):

        try: self.DATAB.reconnect(attempts, time)
        except sql.errors.InterfaceError: return 0

class WEBDRIVER:
    
    def __init__(self, headless=True, wait=15):

        binary = webdriver.firefox.firefox_binary.FirefoxBinary(
            r'C:\Program Files\Mozilla Firefox\firefox.exe'
            )
        options = webdriver.firefox.options.Options()
        options.headless = headless
        self.driver = webdriver.Firefox(firefox_binary=binary, options=options)
        self.driver.implicitly_wait(wait)
        self.options = {
            1: self.driver.find_element_by_xpath,
            2: self.driver.find_element_by_id,
            3: self.driver.find_element_by_name,
            4: self.driver.find_element_by_link_text,
            5: self.driver.find_element_by_partial_link_text,
            6: self.driver.find_element_by_tag_name,
            7: self.driver.find_element_by_class_name,
            8: self.driver.find_element_by_css_selector,
            }

    def get(self, url, retry=3):
        
        for _ in range(retry):
            try: self.driver.get(url)
            except exceptions.TimeoutException: continue
    
    def find(self, address, keys=None, click=None, move=None, type_=1, enter=0, fetch=0):
        
        try:
            element = self.options[type_](address)
            
            if click: element.click()
            if keys: element.send_keys(keys)
            if move:ActionChains(self.driver).move_to_element(element).perform()
            if enter: element.send_keys(Keys.RETURN)

            return element

        except exceptions.NoSuchElementException as error:
            if fetch: raise error
        
        except exceptions.StaleElementReferenceException as error:
            if fetch: raise error

        except exceptions.ElementClickInterceptedException as error:
            if fetch: raise error

        except Exception as error: 
            if fetch: raise error
            print(error)
    
    def page_source(self):
        
        for _ in range(10):
            try: return self.driver.page_source
            except exceptions.WebDriverException: pass
        raise exceptions.WebDriverException
    
    def current_url(self): return self.driver.current_url

    def refresh(self): self.driver.refresh()

    def login(self, site, type_=0):

        if site == 'flickr':

            self.get('https://identity.flickr.com/login')
            while self.current_url() == 'https://identity.flickr.com/login':
                self.find('login-email', CREDENTIALS.get(site, 'user'), type_=2)
                self.find('login-email', Keys.RETURN, type_=2)
                self.find('login-password', CREDENTIALS.get(site,'pass', enter=1), type_=2)
                time.sleep(2.5)

        elif site in ('metarthunter', 'femjoyhunter', 'elitebabes'):

            self.get(f'https://www.{site}.com/members/')
            self.find('//*[@id="user_login"]', CREDENTIALS.get(site, 'user'))
            self.find('//*[@id="user_pass"]', CREDENTIALS.get(site, 'pass'), enter=1)
            while self.current_url() ==f'https://www.{site}.com/members/': 
                time.sleep(2)

        elif site == 'instagram':
        
            self.get('https://www.instagram.com/')
            time.sleep(1)
            self.find('//body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[1]/div/label/input', CREDENTIALS.get(site, 'email'))
            self.find('//body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[2]/div/label/input', CREDENTIALS.get(site, 'pass'), enter=1)
            time.sleep(3)

        elif site== 'gelbooru':

            self.get(
                'https://gelbooru.com/index.php?page=account&s=login&code=00'
                )
            self.find('//body/div[4]/div[4]/div/div/form/input[1]', CREDENTIALS.get(site, 'user'))
            self.find('//body/div[4]/div[4]/div/div/form/input[2]', CREDENTIALS.get(site, 'pass'), enter=1)
            time.sleep(1)

        elif site == 'sankaku':
        
            self.get(f'https://{type_}.sankakucomplex.com/user/login')
            
            while self.current_url().endswith('/user/login'):
                self.find(
                    '//*[@id="user_name"]',CREDENTIALS.get(site, 'user').lower()
                    )
                self.find(
                    '//*[@id="user_password"]', CREDENTIALS.get(site, 'pass', enter=1)
                    )
                time.sleep(1)
        
        elif site == 'furaffinity':

            self.get('https://www.furaffinity.net/login/')
            self.find('//*[@id="login"]', CREDENTIALS.get(site, 'user'))
            self.find('//body/div[2]/div[2]/form/div/section[1]/div/input[2]', CREDENTIALS.get(site, 'pass'), enter=1)
            while self.current_url() == 'https://www.furaffinity.net/login/': 
                time.sleep(2)
        
        elif site == 'twitter':

            email = CREDENTIALS.get(site, 'email')
            passw = CREDENTIALS.get(site, 'pass')

            self.get('https://twitter.com/login')
            element = '//body/div[1]/div[2]/div/div/div[1]/form/fieldset/div[{}]/input'  
            while self.current_url() == 'https://twitter.com/login':
                try:  
                    self.find('session[username_or_email]', email, type_=3)
                    time.sleep(.75)
                    self.find('session[password]', passw, type_=3, enter=1)
                    time.sleep(5)

                except:
                    self.find(element.format(1), email)
                    time.sleep(.75)
                    self.find(element.format(2), passw, enter=1)
                    time.sleep(5)

        elif site == 'posespace':

            self.get('https://www.posespace.com/')
            self.find("//body/form[1]/div[3]/div[1]/nav/div/div[2]/ul[2]/li[6]/a", click=True)
            self.find("popModal", click=True, type_=7)
            self.find("loginUsername", CREDENTIALS.get(site, 'email'), type_=2)
            self.find("loginPassword", CREDENTIALS.get(site, 'pass'), type_=2, enter=1)

        elif site == 'pinterest':
            
            self.get('https://www.pinterest.com/login/')
            self.find('//*[@id="email"]', CREDENTIALS.get(site, 'email'))
            self.find('//*[@id="password"]', CREDENTIALS.get(site, 'pass'), enter=1)
            time.sleep(5)
            
        elif site == 'deviantArt':

            self.get('https://www.deviantart.com/users/login')
            self.find('//*[@id="username"]', CREDENTIALS.get(site, 'email'))
            self.find('//*[@id="password"]', CREDENTIALS.get(site, 'pass'), enter=1)
            time.sleep(5)
    
    def close(self):
        
        try: self.driver.close()
        except: pass

def start():
    
    import threading
    from Webscraping import Photos, Illus, comics
    
    threads = [
        threading.Thread(target=Photos.start),
        threading.Thread(target=Illus.start),
        threading.Thread(target=comics.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    print('Complete')

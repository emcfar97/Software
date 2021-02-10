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
    f'INSERT IGNORE INTO favorites(path, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s)',
    'INSERT INTO imageData(path, artist, tags, rating, type, hash, src, site) VALUES(%s, CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s)',
    'INSERT INTO comic(path_, parent, page) VALUES(%s, %s, %s)',
    'INSERT INTO imageData(path, artist, tags, rating, type, hash, src, site, href) VALUES(%s, CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s. %s)',
    f'INSERT IGNORE INTO favorites(path, src, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s)',
    ]
UPDATE = [
    f'UPDATE imageData SET path=%s, artist=CONCAT(" ", %s, " "), tags=CONCAT(" ", %s, " "), rating=%s, type=%s, src=%s, hash=%s WHERE href=%s',
    f'UPDATE imageData SET path=%s, src=%s, hash=%s, type=%s WHERE href=%s',
    f'UPDATE favorites SET path=REPLACE(%s, "{ROOT}", "C:"), src=%s WHERE href=%s',
    f'INSERT INTO imageData(path, hash, href, site) VALUES(%s, %s, %s, %s)',
    f'UPDATE favorites SET checked=%s, saved=%s WHERE path=%s',
    ]
DELETE = [
    'DELETE FROM imageData WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE NOT (path LIKE "%jpg" OR path LIKE "%jpeg" OR path LIKE "%png" OR path LIKE "%gif" OR path LIKE "%webm" OR path LIKE "%mp4")'
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
    
    def __init__(self, headless=True, profile=True, wait=15):

        if profile: profile = webdriver.FirefoxProfile(self.get_profile())
        binary = webdriver.firefox.firefox_binary.FirefoxBinary(
            r'C:\Program Files\Mozilla Firefox\firefox.exe'
            )
        options = webdriver.firefox.options.Options()
        options.headless = headless
        self.driver = webdriver.Firefox(
            firefox_profile=profile, firefox_binary=binary, options=options
            )
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

    def get_profile(self):

        path = Path(r'~\AppData\Roaming\Mozilla\Firefox\Profiles')
        
        return list(path.expanduser().glob('*.default*'))[0]

    def get(self, url, retry=3):
        
        for _ in range(retry):
            try: self.driver.get(url)
            except exceptions.TimeoutException: continue
            except exceptions.UnexpectedAlertPresentException:
                continue
    
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
            except exceptions.WebDriverException: 
                self.refresh()
                
        raise exceptions.WebDriverException
    
    def current_url(self): return self.driver.current_url

    def refresh(self): self.driver.refresh()

    def active_element(self): return self.driver.switch_to.active_element

    def login(self, site, login=0):

        if site == 'flickr': return CREDENTIALS.get(site, 'url')

        elif site == 'elitebabes': return CREDENTIALS.get(site, 'url')

        elif site == 'instagram': return CREDENTIALS.get(site, 'url')

        elif site == 'gelbooru': return CREDENTIALS.get(site, 'url')

        elif site == 'sankaku':
            
            if login:
                self.get(f'https://{login}.sankakucomplex.com/user/login')
                
                while self.current_url().endswith('/user/login'):
                    self.find(
                        '//*[@id="user_name"]',CREDENTIALS.get(site, 'user').lower()
                        )
                    self.find(
                        '//*[@id="user_password"]', CREDENTIALS.get(site, 'pass'), enter=1
                        )
                    time.sleep(2)
                
            return CREDENTIALS.get(site, 'url')
        
        elif site == 'foundry': return CREDENTIALS.get(site, 'url')

        elif site == 'furaffinity': return CREDENTIALS.get(site, 'url')
        
        elif site == 'twitter': return CREDENTIALS.get(site, 'url')

        elif site == 'posespace':

            self.get('https://www.posespace.com/')
            self.find("//body/form[1]/div[3]/div[1]/nav/div/div[2]/ul[2]/li[6]/a", click=True)
            self.find("popModal", click=True, type_=7)
            self.find("loginUsername", CREDENTIALS.get(site, 'email'), type_=2)
            self.find("loginPassword", CREDENTIALS.get(site, 'pass'), type_=2, enter=1)
            
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

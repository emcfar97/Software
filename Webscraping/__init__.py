import time, json
from os import path
from pathlib import Path
import mysql.connector as sql
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

CREDENTIALS = ConfigParser(delimiters='=') 
CREDENTIALS.read(r'Webscraping\credentials.ini')
ROOT = Path(Path().cwd().drive)
USER = ROOT / path.expandvars(r'\Users\$USERNAME')
TOKEN = CREDENTIALS.get('redgifs', 'token')

SELECT = [
    'SELECT href FROM imagedata WHERE site=%s',
    'SELECT href FROM temporary WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    f'SELECT rowid, REPLACE(path, "C:", "{ROOT}"), src, href, site FROM favorites WHERE {{}} AND NOT ISNULL(path)',
    f'''
        SELECT save_name, '/artworks/'||image_id, 'pixiv' FROM pixiv_master_image WHERE SUBSTR(save_name, -3) IN ("gif", "jpg", "png")
        UNION
        SELECT save_name, '/artworks/'||image_id, 'pixiv' FROM pixiv_manga_image
        WHERE SUBSTR(save_name, -3) IN ("gif", "jpg", "png")
        ''',
    f'SELECT * FROM imagedata WHERE path=%s',
    f'SELECT REPLACE(path, "C:", "{ROOT}"), src, href, site FROM favorites WHERE site=%s',
    ]
INSERT = [
    'INSERT IGNORE INTO temporary(href, site, type) VALUES(%s, %s, %s)',
    'INSERT IGNORE INTO favorites(href, site) VALUES(%s, %s)',
    f'INSERT IGNORE INTO favorites(path, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s)',
    'REPLACE INTO imagedata(path, artist, tags, rating, type, hash, src, site, href) VALUES(%s, CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s, %s)',
    'REPLACE INTO comic(path, parent) VALUES(%s, %s)',
    f'INSERT IGNORE INTO favorites(path, src, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s)',
    ]
UPDATE = [
    f'UPDATE imagedata SET path=%s, artist=CONCAT(" ", %s, " "), tags=CONCAT(" ", %s, " "), rating=%s, type=%s, src=%s, hash=%s WHERE href=%s',
    f'UPDATE imagedata SET path=%s, src=%s, hash=%s, type=%s WHERE href=%s',
    f'UPDATE favorites SET path=REPLACE(%s, "{ROOT}", "C:"), src=%s WHERE href=%s',
    f'INSERT INTO imagedata(path, hash, href, site) VALUES(%s, %s, %s, %s)',
    f'UPDATE favorites SET checked=%s, saved=%s WHERE rowid=%s',
    'UPDATE temporary SET href=%s WHERE href=%s',
    'UPDATE temporary SET href=%s, site=%s WHERE href=%s',
    ]
DELETE = [
    'DELETE FROM imagedata WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE href LIKE "%s%" AND ISNULL(path)',
    'DELETE FROM favorites WHERE SUBSTRING_INDEX(path, ".", -1) IN ("zip", "pixiv", "ini", "lnk", "ugoira")',
    'DELETE FROM temporary WHERE href=%s AND type=%s',
    'DELETE FROM temporary WHERE href=%s'
    ]

class CONNECT:

    def __init__(self, target='mysql'):

        self.DATAB = sql.connect(
            user=CREDENTIALS.get(target, 'username'), 
            password=CREDENTIALS.get(target, 'password'), 
            database=CREDENTIALS.get(target, 'database'), 
            host=CREDENTIALS.get(target, 'hostname')
            )
        self.CURSOR = self.DATAB.cursor(buffered=True)
        self.rowcount = -1

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):

        for _ in range(3):
            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)
                self.rowcount = self.CURSOR.rowcount

                if commit: return self.DATAB.commit()
                if fetch: return self.CURSOR.fetchall()
                return 1

            except sql.errors.ProgrammingError:
                print('\nProgrammingError')                        
                break

            except sql.errors.IntegrityError:
                print('\nIntegrityError')                            
                if statement.startswith('UPDATE'):
                    index = 0 if 'imaged' in statement else 1
                    self.execute(DELETE[index], (arguments[-1],), commit=1)
                    return 1
                elif statement.startswith('INSERT'): return 1

            except sql.errors.DatabaseError:
                print('\nDatabaseError')
                self.reconnect()
                
            except Exception as error:
                print('\n', error)
                self.reconnect()

        return 0
    
    def call(self, function, arguments=None, fetch=1):

        self.CURSOR.callproc(function, arguments)
        results = self.CURSOR.stored_results()
        
        if fetch: return list(results)[0]
    
    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=4, time=15):

        try: self.DATAB.reconnect(attempts, time)
        except sql.errors.InterfaceError: return 0
    
class WEBDRIVER:
    
    PATH = Path(r'C:\Program Files\Mozilla Firefox')
    options = {
        1: By.XPATH,
        2: By.ID,
        3: By.NAME,
        4: By.LINK_TEXT,
        5: By.PARTIAL_LINK_TEXT,
        6: By.TAG_NAME,
        7: By.CLASS_NAME,
        8: By.CSS_SELECTOR,
        }
            
    def __init__(self, headless=True, profile=True, wait=15):
        
        # self.headless = headless
        # self.profile = profile
        # self.wait = wait
        
        if profile: firefox_profile = self.get_profile()
        options = webdriver.firefox.options.Options()
        options.headless = headless
        
        self.driver = webdriver.Firefox(
            firefox_profile, self.get_binary(),  
            executable_path=str(WEBDRIVER.PATH / 'geckodriver.exe'),
            options=options, service_log_path='nul'
            )
        self.driver.implicitly_wait(wait)
     
    def get_profile(self):
        
        path = Path(r'~\AppData\Roaming\Mozilla\Firefox\Profiles')
        profile_list = list(path.expanduser().glob('*.default*'))[0]
        
        return webdriver.FirefoxProfile(profile_list)

    def get_binary(self):
        
        path = str(WEBDRIVER.PATH / 'firefox.exe')

        return webdriver.firefox.firefox_binary.FirefoxBinary(path)

    def get(self, url, wait=0, retry=3):
        
        for _ in range(retry):
            
            try: 
                self.driver.get(url)
                time.sleep(wait)
                break
                
            # except (
            #     exceptions.InvalidSessionIdException,
            #     exceptions.NoSuchWindowException
            #     ):
            #     self.__init__(self.headless, self.profile, self.wait)
                
            except (
                exceptions.TimeoutException,
                exceptions.WebDriverException,
                exceptions.UnexpectedAlertPresentException
                ):
                continue
            
        return self.driver.page_source
    
    def current_url(self):
        
        return self.driver.current_url
    
    def find(self, address, keys=None, click=None, move=None, type_=1, enter=0, fetch=0):
        
        for _ in range(5):
        
            try:
                element = self.driver.find_element(WEBDRIVER.options[type_], address)
                
                if click: element.click()
                if keys: element.send_keys(keys)
                if move: ActionChains(self.driver).move_to_element(element).perform()
                if enter: element.send_keys(Keys.RETURN)

                return element
                
            # except (
            #     exceptions.InvalidSessionIdException,
            #     exceptions.NoSuchWindowException
            #     ):
            #     self.__init__(self.headless, self.profile, self.wait)

            except Exception as error_:
                if fetch: 
                    
                    self.lock.release()
                    raise error_
                error = error_

        if fetch: raise error
    
    def execute_script(self, script):
        
        self.driver.execute_script(script)
        
    def active_element(self):
        
        return self.driver.switch_to.active_element
    
    def close(self=None):

        try: self.driver.close()
        except: pass

def get_credentials(section, *fields):
    
    if len(fields) == 1:

        return CREDENTIALS.get(section, fields[0])
    
    return [
        CREDENTIALS.get(section, option) for option in fields
        ]
    
def get_starred(headless=True):

    import bs4
    
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless=headless)
    UPDATE = 'UPDATE imagedata SET stars=3 WHERE path=%s AND stars=0'
    ADDRESS = '//button[@aria-label="Remove from Starred"]'

    content = DRIVER.get('https://www.dropbox.com/starred', wait=10)
    html = bs4.BeautifulSoup(content, 'lxml')
    starred = html.findAll('a', {'data-testid': 'filename-link'})
    
    for star in starred:

        DRIVER.find(ADDRESS, click=True)
        MYSQL.execute(UPDATE, (star.text,), commit=1)
        html = bs4.BeautifulSoup(content, 'lxml')
        starred = html.findAll('span', {"data-testid": "filename-link"})

    DRIVER.close()

def get_token():
    
    import requests
    
    response = requests.get('https://api.redgifs.com/v2/auth/temporary')
    TOKEN = response.json()['token']
    CREDENTIALS.set('redgifs', 'token', TOKEN)
    
    with open(r'Webscraping\credentials.ini', 'w') as configfile:
        CREDENTIALS.write(configfile)
    
    return TOKEN
      
def json_generator(path):
    
    try: 
        generator = json.load(open(path, encoding='utf-8'))
        if len(generator) > 1: raise IndexError
    except:
        print(path)
        return []

    for object in generator[0]['windows'].values():

        for value in object.values():
    
            yield value
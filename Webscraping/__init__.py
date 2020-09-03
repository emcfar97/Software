from pathlib import Path
import mysql.connector as sql
from selenium import webdriver
from configparser import ConfigParser
import selenium.common.exceptions as exceptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

ROOT = Path(Path().cwd().drive)
SELECT = [
    'SELECT href FROM imageData WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM imageData WHERE site=%s AND ISNULL(path)',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    f'SELECT REPLACE(path, "C:", "{ROOT}"), href, src, site FROM favorites WHERE NOT (checked OR ISNULL(path))',
    f'''
        SELECT REPLACE(save_name, "{ROOT}", "C:"),'/artworks/'||image_id,'pixiv' FROM pixiv_master_image UNION
        SELECT REPLACE(save_name, "{ROOT}", "C:"), '/artworks/'||image_id, 'pixiv' FROM pixiv_manga_image
        ''',
    f'SELECT * FROM imagedata WHERE path=%s'
    ]
INSERT = [
    'INSERT INTO imageData(href, type, site) VALUES(%s, %s, %s)',
    'INSERT INTO favorites(href, site) VALUES(%s, %s)',
    f'INSERT IGNORE INTO favorites(path, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s)',
    'INSERT INTO imageData(artist, type, src, site) VALUES(%s, %s, %s, %s)',
    f'INSERT INTO imageData(path, artist, tags, rating, type, hash, src, page) VALUES(REPLACE(%s, "{ROOT}", "C:"), CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s)',
    f'replace INTO imageData(path, artist, tags, rating, hash, site, type) VALUES(REPLACE(%s, "{ROOT}", "C:"), CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s)'
    ]
UPDATE = [
    f'UPDATE imageData SET path=REPLACE(%s, "{ROOT}", "C:"), src=%s, hash=%s, type=%s WHERE href=%s',
    f'UPDATE favorites SET path=REPLACE(%s, "{ROOT}", "C:"), hash=%s, src=%s WHERE href=%s',
    f'REPLACE INTO imageData(path, hash, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"),%s,%s,%s)',
    f'UPDATE imageData SET path=REPLACE(%s, "{ROOT}", "C:"), artist=CONCAT(" ", %s, " "), tags=CONCAT(" ", %s, " "), rating=%s, src=%s, hash=%s WHERE href=%s',
    f'UPDATE favorites SET checked=%s, saved=%s WHERE path=REPLACE(%s, "{ROOT}", "C:")',
    f'INSERT INTO favorites(path, hash, src, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s, %s)'
    ]
DELETE = [
    'DELETE FROM imageData WHERE href=%s AND ISNULL(path)'
    ]

class CONNECT:

    def __init__(self):

        credentials = ConfigParser(delimiters='=') 
        credentials.read('credentials.ini')

        self.DATAB = sql.connect(
            user=credentials.get('mysql', 'username'), 
            password=credentials.get('mysql', 'password'), 
            database=credentials.get('mysql', 'database'), 
            host=credentials.get('mysql', 'hostname')
            )
        self.CURSOR = self.DATAB.cursor(buffered=True)

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        for _ in range(10):

            try:
                try: self.CURSOR.execute(statement, arguments)
                except: self.CURSOR.executemany(statement, arguments)

                if commit: return self.DATAB.commit()
                elif fetch: return self.CURSOR.fetchall()

            except sql.errors.IntegrityError: 
                self.CURSOR.execute(DELETE[0], (arguments[-1],))
                self.DATAB.commit()

            except sql.errors.OperationalError: continue
            
            except sql.errors.DatabaseError: self.__init__()
            
            except sql.errors.ProgrammingError: raise sql.ProgrammingError

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

class WEBDRIVER:
    
    def __init__(self, headless=False):

        options = Options()
        options.headless = headless
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        self.driver = webdriver.Firefox(firefox_binary=binary, options=options)
        self.driver.implicitly_wait(15)

    def get(self, url): self.driver.get(url)
    
    def find(self, adress, keys=None, click=False, type_=1):
        
        try:
            
            if   type_ == 1:
                element = self.driver.find_element_by_xpath(adress)
            elif type_ == 2:
                element = self.driver.find_element_by_id(adress)
            elif type_ == 3:
                element = self.driver.find_element_by_name(adress)
            # elif type_ == 4:
            #     element = self.driver.find_element_by_link_text(adress)
            # elif type_ == 5:
            #     element =self.driver.find_element_by_partial_link_text(adress)
            elif type_ == 6:
                element = self.driver.find_element_by_tag_name(adress)
            elif type_ == 7:
                element = self.driver.find_element_by_class_name(adress)
            # elif type_ == 8:
            #     element = self.driver.find_element_by_css_selector(adress)
            
            if keys: element.send_keys(keys)

            if click: element.click()

            return element

        except exceptions.StaleElementReferenceException:
            print('stale element')

        except exceptions.NoSuchElementException:
            print('no such element')
        
        except Exception as error: print(error)
    
    def page_source(self):
        
        for _ in range(10):
            try: return self.driver.page_source
            except exceptions.WebDriverException: pass
        raise exceptions.WebDriverException
    
    def current_url(self): return self.driver.current_url

    def refresh(self): self.driver.refresh()

    def close(self):
        
        try: self.driver.close()
        except: pass

def start():
    
    import threading
    from Webscraping import Photos, Illus, comics
    
    threads = [
        # threading.Thread(target=Photos.start),
        threading.Thread(target=Illus.start),
        threading.Thread(target=comics.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    print('Complete')

CONNECTION = CONNECT()
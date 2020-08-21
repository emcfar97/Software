import pathlib, threading
import mysql.connector as sql
from selenium import webdriver
import selenium.common.exceptions as exceptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
    
ROOT = pathlib.Path().cwd().parent
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
    ]
INSERT = [
    'INSERT INTO imageData(href, type, site) VALUES(%s, %s, %s)',
    'INSERT INTO favorites(href, site) VALUES(%s, %s)',
    f'INSERT IGNORE INTO favorites(path, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s)',
    'INSERT INTO imageData(artist, type, src, site) VALUES(%s, %s, %s, %s)',
    'INSERT INTO imageData(path, artist, tags, rating, type, hash, src, page) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s, %s, %s, %s, %s)',
    'INSERT IGNORE INTO imageData(path, tags, rating, hash, type) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s, 0)'
    ]
UPDATE = [
    f'UPDATE imageData SET path=REPLACE(%s, "{ROOT}", "C:"), src=%s, hash=%s, type=%s WHERE href=%s',
    f'UPDATE favorites SET path=REPLACE(%s, "{ROOT}", "C:"), hash=%s, src=%s WHERE href=%s',
    f'REPLACE INTO imageData(path,hash,href,site) VALUES(REPLACE(%s, "{ROOT}", "C:"),%s,%s,%s)',
    f'UPDATE imageData SET path=REPLACE(%s, "{ROOT}", "C:"), artist=%s, tags=%s, rating=%s, src=%s, hash=%s WHERE href=%s',
    f'UPDATE favorites SET checked=%s, saved=%s WHERE path=REPLACE(%s, "{ROOT}", "C:")',
    f'INSERT INTO favorites(path, hash, src, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s, %s)'
    ]

class CONNECT:

    def __init__(self):

        self.DATAB = sql.connect(
            user='root', password='SchooL1@', database='userData', 
            host='127.0.0.1' if ROOT.drive == 'C:' else '192.168.1.43'
            )
        self.CURSOR = self.DATAB.cursor(buffered=True)

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        for _ in range(20):

            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)

                if commit: return self.DATAB.commit()
                elif fetch: return self.CURSOR.fetchall()

            except sql.errors.OperationalError: continue
            
            except sql.errors.DatabaseError: self.__init__()

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

class WEBDRIVER:
    
    def __init__(self, headless=False):

        options = Options()
        options.headless = headless
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        self.driver = webdriver.Firefox(firefox_binary=binary, options=options)
        self.driver.implicitly_wait(10)

    def get(self, url): self.driver.get(url)

    def page_source(self): return self.driver.page_source
    
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
            #     element = self.driver.find_element_by_partial_link_text(adress)
            # elif type_ == 6:
            #     element = self.driver.find_element_by_tag_name(adress)
            # elif type_ == 7:
            #     element = self.driver.find_element_by_class_name(adress)
            # elif type_ == 8:
            #     element = self.driver.find_element_by_css_selector(adress)

            if keys: element.send_keys(keys)

            if click: element.click()

        # except exceptions.WebDriverException: self.__init__()
        except Exception as error: print(error) 
        # self.find(adress, keys, click, type_)
    
    def refresh(self): self.driver.refresh()

    def close(self): 
        
        try: self.driver.close()
        except: pass

def start():
    
    from Webscraping import Photos, Illus
    
    threads = [
        threading.Thread(target=Photos.start),
        threading.Thread(target=Illus.start) 
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    print('Complete')

CONNECTION = CONNECT()
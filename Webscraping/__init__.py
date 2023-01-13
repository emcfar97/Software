import os, time, json
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
USER = ROOT / os.path.expandvars(r'\Users\$USERNAME')
EXT = 'jpe?g|png|webp|gif|webm|mp4'

SELECT = [
    'SELECT href FROM imagedata WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM imagedata WHERE site=%s AND ISNULL(path)',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    f'SELECT REPLACE(path, "C:", "{ROOT}"), href, src, site FROM favorites WHERE {{}} AND NOT ISNULL(path)',
    f'''
        SELECT REPLACE(save_name, "{ROOT}", "C:"), '/artworks/'||image_id,'pixiv' FROM pixiv_master_image UNION
        SELECT REPLACE(save_name, "{ROOT}", "C:"), '/artworks/'||image_id, 'pixiv' FROM pixiv_manga_image
        WHERE SUBSTR(save_name, -3) IN ("gif", "jpg", "png")
        ''',
    f'SELECT * FROM imagedata WHERE path=%s'
    ]
INSERT = [
    'INSERT INTO imagedata(href, site) VALUES(%s, %s)',
    'INSERT INTO favorites(href, site) VALUES(%s, %s)',
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
    f'UPDATE favorites SET checked=%s, saved=%s WHERE path=REPLACE(%s, "{ROOT}", "C:")',
    ]
DELETE = [
    'DELETE FROM imagedata WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE href=%s AND ISNULL(path)',
    'DELETE FROM favorites WHERE href LIKE "%s%" AND ISNULL(path)',
    'DELETE FROM favorites WHERE SUBSTRING_INDEX(path, ".", -1) IN ("zip", "pixiv", "ini", "lnk")',
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

        for _ in range(10):
            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)
                self.rowcount = self.CURSOR.rowcount

                if commit: return self.DATAB.commit()
                if fetch: return self.CURSOR.fetchall()
                return 1

            except sql.errors.ProgrammingError:
            
                break

            except sql.errors.IntegrityError:
                
                if statement.startswith('UPDATE'):
                    index = 0 if 'imaged' in statement else 1
                    self.execute(DELETE[index], (arguments[-1],), commit=1)
                    return 1
                elif statement.startswith('INSERT'): return 1

            except (
                sql.errors.OperationalError, 
                sql.errors.DatabaseError, 
                sql.errors.InterfaceError
                ):
                
                self.reconnect()

        return 0
    
    def call(self, function, arguments=None, fetch=1):

        self.CURSOR.callproc(function, arguments)
        results = self.CURSOR.stored_results()
        
        if fetch: return list(results)[0]
    
    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=5, time=15):

        try: self.DATAB.reconnect(attempts, time)
        except sql.errors.InterfaceError: return 0
    
class WEBDRIVER:
    
    PATH = Path(r'C:\Program Files\Mozilla Firefox')

    def __init__(self, headless=True, profile=True, wait=15):
        
        self.headless = headless
        self.profile = profile
        self.wait = wait
        
        if profile: profile = webdriver.FirefoxProfile(self.get_profile())
        binary = webdriver.firefox.firefox_binary.FirefoxBinary(
            str(WEBDRIVER.PATH / 'firefox.exe')
            )
        options = webdriver.firefox.options.Options()
        options.headless = headless
        
        self.driver = webdriver.Firefox(
            firefox_profile=profile, firefox_binary=binary, 
            options=options, service_log_path=None, 
            executable_path=str(WEBDRIVER.PATH / 'geckodriver.exe')
            )
        self.driver.implicitly_wait(wait)
        self.options = {
            1: By.XPATH,
            2: By.ID,
            3: By.NAME,
            4: By.LINK_TEXT,
            5: By.PARTIAL_LINK_TEXT,
            6: By.TAG_NAME,
            7: By.CLASS_NAME,
            8: By.CSS_SELECTOR,
            }

    def get_profile(self):

        path = Path(r'~\AppData\Roaming\Mozilla\Firefox\Profiles')
        
        return list(path.expanduser().glob('*.default*'))[0]

    def get(self, url, wait=0, retry=3):
        
        for _ in range(retry):
            try: 
                self.driver.get(url)
                time.sleep(wait)
                
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
    
    def find(self, address, keys=None, click=None, move=None, type_=1, enter=0, fetch=0):
        
        for _ in range(5):
        
            try:
                element = self.driver.find_element(self.options[type_], address)
                
                if click: element.click()
                if keys: element.send_keys(keys)
                if move:ActionChains(self.driver).move_to_element(element).perform()
                if enter: element.send_keys(Keys.RETURN)

                return element
                
            # except (
            #     exceptions.InvalidSessionIdException,
            #     exceptions.NoSuchWindowException
            #     ):
            #     self.__init__(self.headless, self.profile, self.wait)

            except Exception as error_:
                if fetch: raise error_
                error = error_

        if fetch: raise error
    
    def page_source(self, wait=0, error=None):
        
        time.sleep(wait)
        
        for _ in range(5):
            try: return self.driver.page_source
            
            except exceptions.InvalidArgumentException as error_:
                error = error_
                return self.driver.page_source.encode('ascii', 'ignore').decode('unicode_escape')
                
            # except (
            #     exceptions.InvalidSessionIdException,
            #     exceptions.NoSuchWindowException
            #     ) as error_:
            #     error = error_
            #     self.__init__(self.headless, self.profile, self.wait)
            
            except exceptions.WebDriverException as error_:
                error = error_
                self.refresh()
                
        raise error
    
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
                        '//*[@id="user_name"]', CREDENTIALS.get(site, 'user').lower()
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
            
        elif site == 'deviantart': return CREDENTIALS.get(site, 'url')
        
    def close(self):
        
        try: self.driver.close()
        except: pass
        
def get_starred(headless=True):

    import bs4
    
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless=headless)
    UPDATE = 'UPDATE imagedata SET stars=4 WHERE path=%s AND stars=0'
    ADDRESS = '//button[@aria-label="Remove from Starred"]'

    DRIVER.get('https://www.dropbox.com/starred', wait=4)
    time.sleep(5)
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    starred = html.findAll('a', {"data-testid": "filename-link"})
    
    for star in starred:

        DRIVER.find(ADDRESS, click=True)
        MYSQL.execute(UPDATE, (star.text,), commit=1)
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        starred = html.findAll('span', {"data-testid": "filename-link"})

    DRIVER.close()

def extract_files(source, dest=None, headless=True):
    
    import re, bs4, pathlib, send2trash, subprocess
    from urllib.parse import urlparse
    from Webscraping.utils import USER, save_image
        
    def extract_errors(path, dest):
        
        if path.exists():
            
            images = path.read_text().split()
            
            for image in images:
            
                name = dest / image.split('/')[-1].split('?')[0]
                
                if name.suffix == '': name = name.with_suffix('.webm')
                elif name.suffix == '.m3u8':
                    name = dest / image.split('/')[3]
                    name = name.with_suffix('.mp4')
                    subprocess.run(['ffmpeg', '-y', '-i', image, str(name)])
                    
                if save_image(name, image): images.remove(image)
                
                path.write_text('\n'.join(images))
            
        else: path.touch()
    
    if isinstance(source, str):
        source = pathlib.Path(source)
        if source.is_file(): iterator = [source]
        else: iterator = source.glob('*json')
        errors_txt = source.parent / 'Errors.txt'
        
    elif isinstance(source, list):
        iterator = source
        errors_txt = source / 'Errors.txt'
        
    elif isinstance(source, Path):
        iterator = source.glob('*json')
        errors_txt = source / 'Errors.txt'
    
    if dest is None: dest = source
    else: dest = USER / dest
    
    extract_errors(errors_txt, dest)
    errors = []
        
    driver = WEBDRIVER(headless=headless)
    
    for file in iterator:

        for url in json_generator(file):
            
            path = urlparse(url['url']).path[1:]
                
            if re.match('https://www.reddit.com/r/.+', url['url']):
                
                driver.get(url['url'], wait=10)
                html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
                try: image = html.find('source', src=True).get('src')
                except AttributeError:
                    errors.append(image)
                    continue
                
            else:
                try: image = (
                        f'https://{url["title"]}'
                        if url['url'] == 'about:blank' else 
                        url['url']
                        )
                except KeyError: continue
                
            name = dest / path.split('/')[-1]
            
            if not name.suffix and 'imgur' in image:
                
                driver.get(image, wait=5)
                html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
                
                try: 
                    image = html.find('source', src=True).get('src')
                    name = dest / image.split('/')[-1]
                except: errors.append(image); continue
                
            elif not name.suffix and re.search('redgifs|gfycat', image):
                
                name = dest / image.split('/')[-1].split('?')[0]
                name = name.with_suffix('.webm')
               
            if name.suffix == '.gifv':
                        
                name = name.with_suffix('.webm')
                image = f'https://i.imgur.com/{name.stem}.mp4'
                
            if name.exists(): continue

            elif not save_image(name, image): errors.append(image)
            
            elif name.suffix == '.gif' and b'MPEG' in name.read_bytes():
                try: name.rename(name.with_suffix('.webm'))
                except: name.unlink(missing_ok=1)
        
        errors_txt.write_text('\n'.join(errors))
        send2trash.send2trash(str(file))
        
def json_generator(path):
    
    generator = json.load(open(path, encoding='utf-8'))

    for object in generator[0]['windows'].values():

        for value in object.values():
    
            yield value
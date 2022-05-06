import os, time, json, send2trash
from pathlib import Path
import mysql.connector as sql
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as exceptions
from selenium.webdriver.common.action_chains import ActionChains

CREDENTIALS = ConfigParser(delimiters='=') 
CREDENTIALS.read(r'Webscraping\credentials.ini')
ROOT = Path(Path().cwd().drive)
USER = ROOT / os.path.expandvars(r'\Users\$USERNAME')
EXT = 'jpe?g|png|gif|webm|mp4'

SELECT = [
    'SELECT href FROM imagedata WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM imagedata WHERE site=%s AND ISNULL(path)',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    f'SELECT REPLACE(path, "C:", "{ROOT}"), href, src, site FROM favorites WHERE NOT (checked={{}} OR ISNULL(path))',
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
    'DELETE FROM favorites WHERE SUBSTRING_INDEX(path, ".", -1) IN ("zip", "pixiv", "ini", "lnk")',
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

    def get(self, url, wait=0, retry=3):
        
        for _ in range(retry):
            try: 
                self.driver.get(url)
                time.sleep(wait)
            except (
                exceptions.TimeoutException,
                exceptions.WebDriverException,
                exceptions.UnexpectedAlertPresentException
                ):
                continue
    
    def find(self, address, keys=None, click=None, move=None, type_=1, enter=0, fetch=0):
        
        for _ in range(5):
        
            try:
                element = self.options[type_](address)
                
                if click: element.click()
                if keys: element.send_keys(keys)
                if move:ActionChains(self.driver).move_to_element(element).perform()
                if enter: element.send_keys(Keys.RETURN)

                return element

            except Exception as error_:
                if fetch: raise error_
                error = error_

        if fetch: raise error
    
    def page_source(self, error=None):
        
        for _ in range(5):
            try: return self.driver.page_source
            except exceptions.InvalidArgumentException as error_:
                error = error_
                return self.driver.page_source.encode('ascii', 'ignore').decode('unicode_escape')
            except exceptions.WebDriverException as error_:
                error = error_
                self.refresh()
            except exceptions.InvalidSessionIdException as error_:
                error = error_
                print()
                
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
    starred = html.findAll('a', {"data-testid": "files-filename"})
    
    for star in starred:

        DRIVER.find(ADDRESS, click=True)
        MYSQL.execute(UPDATE, (star.text,), commit=1)
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        starred = html.findAll('span', {"data-testid": "files-filename"})

    DRIVER.close()

def extract_files(source, dest=None, headless=True):
    
    import re, bs4
    from urllib.parse import urlparse
    from Webscraping.utils import USER, save_image
        
    def get_url(driver, src):

        driver.get(src)
        time.sleep(4)
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        url = html.find(content=re.compile('.+mp4'))

        return url.get('content')

    def extract_errors(path, dest):
        
        if path.exists():
            
            for image in path.read_text().split('\n'):
            
                image = image.strip()
                name = dest / image.split('/')[-1].split('?')[0]
                if not name.exists(): save_image(name, image)
            
        else: path.touch()
    
    if isinstance(source, str): 
        source = USER / source
        iterator = source.glob('*json')
    elif isinstance(source, list): iterator = source
    elif isinstance(source, Path): iterator = source.glob('*json')
    
    if dest is None: dest = source
    else: dest = USER / dest
        
    driver = WEBDRIVER(headless=headless, profile=None)
    errors_txt = source / 'Errors.txt'
    extract_errors(errors_txt, dest)
    errors = []
        
    for file in iterator:

        for url in json_generator(file):
            
            path = urlparse(url['url']).path[1:]
            if re.match('https://i.imgur.com/.+gif', url['url']):
                path.replace('gif', 'mp4')
            elif re.search('.+/watch.+', url['url']):
                try: 
                    path = get_url(driver, url['url'])
                    url['url'] = path
                except:
                    errors.append(url['url'])
                    continue

            name = dest / path.split('/')[-1]
            if name.exists(): continue
            try: image = (
                    f'https://{url["title"]}'
                    if url['url'] == 'about:blank' else 
                    url['url']
                    )
            except KeyError: continue
                        
            if not save_image(name, image): errors.append(image)
            elif name.suffix == '.gif' and b'MPEG' in name.read_bytes():
                try: name.rename(name.with_suffix('.mp4'))
                except: name.unlink(missing_ok=1)
        
        send2trash.send2trash(str(file))
    
    if errors: errors_txt.write_text('\n'.join(errors))

    for file in dest.glob('*webp'):

        name = file.with_suffix('.jpg')
        name.write_bytes(file.read_bytes())
        file.unlink()
        
    for file in dest.glob('*gifv'):

        name = file.with_suffix('.mp4')
        image = f'https://i.imgur.com/{name.name}'
        save_image(name, image)
        file.unlink()

def json_generator(path):

    generator = json.load(open(path, encoding='utf-8'))

    for object in generator[0]['windows'].values():

        for value in object.values():
    
            yield value
import os, sqlite3, tempfile
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, InvalidArgumentException, WebDriverException, ElementClickInterceptedException, NoSuchElementException    
import mysql.connector as sql
if __name__ == '__main__': from utils import *
else: from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor()

def main(driver, paths, sankaku=0, gelbooru=0):
    
    if not paths: return
    size = len(paths)
    limit = get_limit(driver)

    for num, (path, src,) in enumerate(paths):
        progress(size, num, 'favorites')
        
        try:
            driver.get('http://iqdb.org/')
            if src is None: 
                driver.find_element_by_xpath('//*[@id="file"]').send_keys(path)
            else:
                driver.find_element_by_xpath('//*[@id="url"]').send_keys(src)
            driver.find_element_by_xpath('//body/form/table[2]/tbody/tr[4]/td[1]/input').click()

            if path.endswith(('gif', 'mp4')): time.sleep(20)
            try:
                html = bs4.BeautifulSoup(driver.page_source, 'lxml')
                too_large = html.findAll(text=re.compile('too large'))
                cant_read = html.findAll(text=re.compile('read query'))
                cant_find = html.findAll(text=re.compile('file was uploaded'))
                
                if too_large or cant_read or cant_find:
                    CURSOR.execute(UPDATE[4], (1, 0, path))
                    DATAB.commit()
                    continue
                
                targets = [
                    target.findAll(href=re.compile('/gelbooru|/chan.san'))[0] 
                    for target in 
                    html.findAll(id='pages', class_='pages')[0].contents 
                    if type(target) != bs4.element.NavigableString and 
                    target.findAll(href=re.compile('/gelbooru|/chan.san')) and 
                    target.findAll(text=re.compile('(Best)|(Additional) match'))
                    ]
            except IndexError: pass
            
            saved = False
            if not targets:
                # site = path.split('\\')[7]
                # if ((sankaku < limit and site != 'pixiv') or (gelbooru < 50 and site == 'pixiv')) and not path.endswith(('.gif', '.webm', '.mp4')):
                #     saved, type_ = upload(driver, path, site)  
                #     if type_: sankaku += 1
                #     else: gelbooru += 1
                pass
                    
            for match in targets:
                driver.get(f'https:{match.get("href")}')
                if 'gelbooru' in match.get("href"):
                    if 'list&' in driver.current_url:
                        saved = True
                        continue
                    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
                    status = html.find(class_='status-notice')
                    if status and 'This post was deleted' in status.text:
                        saved = True
                        continue
                    driver.find_element_by_partial_link_text('Add to favorites').click()
                else:
                    driver.find_element_by_xpath('//*[@title="Add to favorites"]').click()
                saved = True
                            
            if saved:
                os.remove(path)
                CURSOR.execute(UPDATE[4], (1, 1, path))

            DATAB.commit()

        except ElementNotInteractableException:
            
            if 'sankaku' in match.get('href'):
                os.remove(path)
                CURSOR.execute(UPDATE[4], (1, 0, path))

        except FileNotFoundError:
            
            CURSOR.execute(UPDATE[4], (1, 1, path,))
            DATAB.commit()

        except InvalidArgumentException:
            
            CURSOR.execute(UPDATE[4], (1, 0, path,))
            DATAB.commit()
        
        except NoSuchElementException: continue 
            
    progress(size, size, 'favorites')
     
def upload(driver, path, site):

    CURSOR.execute(SELECT[6], (path,))
    href, src = CURSOR.fetchone()
    if site == 'foundry':
        artist = href.split('/')[3]
        href = f'http://www.hentai-foundry.com{href}'
    elif site == 'twitter':
        artist = href.split('/')[0]
        href = f'https://twitter.com{href}'
    elif site == 'furaffinity':
        artist = href.split('/')[2]
        href = f'https://www.furaffinity.net{href}'
    elif site == 'pixiv':
        artist = path.split('\\')[-1].split('-')[0].strip()
        if href is None:
            href = f"/artworks/{path.split('-')[-1].strip().split('_')[0]}"
        href = f'https://www.pixiv.net{href}'
    if artist in artists_dict:
        if artists_dict[artist]: artist = artists_dict[artist]
        else: return False, 0

    driver.get('http://kanotype.iptime.org:8003/deepdanbooru/')
    driver.find_element_by_xpath('//*[@id="exampleFormControlFile1"]').send_keys(path)
    driver.find_element_by_xpath('//body/div/div/div/form/button').click()    
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    tags = [
        tag.text for group in html.findAll('tbody') 
        for tag in group.findAll(href=True)
        ]
    if not tags: return False, None
    if 'comic' in tags: return False, None
    general, rating = generate_tags(exif=False, general=tags, rating=True)
    if len(tags) < 10: tags.append('tagme')
    tags = ' '.join(set(tags + general + [artist]))
    image = tempfile.TemporaryFile(BytesIO(requests.get(src)))
    
    if site in ('pixiv'):
        driver.get('https://gelbooru.com/index.php?page=post&s=add')
        driver.find_element_by_xpath('//body/div[4]/div[4]/form/input[1]').send_keys(path)
        driver.find_element_by_xpath('//body/div[4]/div[4]/form/input[2]').send_keys(href)
        driver.find_element_by_xpath('//*[@id="tags"]').send_keys(tags)
        
        if rating == 'erotic':
            driver.find_element_by_xpath('//body/div[4]/div[4]/form/input[4]').click()
        elif rating == 'questionable':
            driver.find_element_by_xpath('//body/div[4]/div[4]/form/input[5]').click()
        else:
            driver.find_element_by_xpath('//body/div[4]/div[4]/form/input[6]').click()

        driver.find_element_by_xpath('//body/div[4]/div[4]/form/input[7]').click()
        driver.find_element_by_partial_link_text('Add to favorites').click()
        
        return True, 0

    else: 
        driver.get('https://chan.sankakucomplex.com/post/upload')
        driver.find_element_by_xpath('//*[@id="post_file"]').send_keys(path)
        driver.find_element_by_xpath('//*[@id="post_source"]').send_keys(href)
        driver.find_element_by_xpath('//*[@id="post_tags"]').send_keys(tags)
        
        if rating == 'erotic':
            driver.find_element_by_xpath('//*[@id="post_rating_explicit"]').click()
        elif rating == 'questionable':
            driver.find_element_by_xpath('//*[@id="post_rating_questionable"]').click()
        else:
            driver.find_element_by_xpath('//*[@id="post_rating_safe"]').click()
        
        try:
            driver.find_element_by_xpath('//body/div[4]/div[1]/form/div/table/tfoot/tr/td[2]/input').click()
        except ElementClickInterceptedException:
            driver.find_element_by_xpath('//*[@id="post_tags"]').click()
            driver.find_element_by_tag_name('html').send_keys(Keys.ESCAPE)
            driver.find_element_by_xpath('//body/div[4]/div[1]/form/div/table/tfoot/tr/td[2]/input').click()
        driver.find_element_by_xpath('//*[@title="Add to favorites"]').click()
    
        return True, 1

def get_limit(driver):
    
    driver.get('https://chan.sankakucomplex.com/user/upload_limit')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    return int(html.find('strong').text)

def search(driver, path):

    driver.get('https://gelbooru.com/index.php?page=post&s=list&tags=all')
    
    for file in os.listdir(path):

        hash = file.split('.')[-2]
        try: int(hash, 16)
        except: continue
        if int(hash, 16) < 10000: continue

        driver.find_element_by_xpath('//*[@id="tags-search"]').clear()
        driver.find_element_by_xpath('//*[@id="tags-search"]').send_keys(f'md5:{hash}')
        driver.find_element_by_xpath('//*[@id="tags-search"]').send_keys(Keys.RETURN)
        time.sleep(3)
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        null = html.findAll(text=re.compile('Nobody here but us chickens!'))
        if null: continue
        response = input('Delete? ')
        
        if response.lower() in 'yes': 
            file = join(path, file)
            os.remove(file)
            state = 'DELETE FROM imageDatabase WHERE path=?'
            CURSOR.execute(state, (path,))
            driver.get('https://gelbooru.com/index.php?page=post&s=list&tags=all')            
   
def fix(driver, url='?page=favorites&s=view&id=173770&pid=50'):
    
    def next_page(pages):
        
        try: return pages[pages.index(' ') + 3].get('href')
        except IndexError: return False
    
    driver.get(f'https://gelbooru.com/index.php{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    hrefs = [
        target.get('href') for target in 
        html.findAll('a', id=re.compile(r'p\d+'), href=True)
        ]
    for href in hrefs:
        
        driver.get(f'https://gelbooru.com/{href}')
        page = bs4.BeautifulSoup(driver.page_source, 'lxml')
        source = page.find('a', href=True, rel="nofollow", style=False)
        
        if 'artworks' not in source.text:
            source = source.text.replace('net', 'net/artworks/')
            try:
                driver.find_element_by_xpath('/html/body/div[4]/div[5]/div[4]/div/div/h4/a[1]').click()
            except NoSuchElementException: 
                input('Error')
            driver.find_element_by_xpath('//*[@id="source"]').clear()
            driver.find_element_by_xpath('//*[@id="source"]').send_keys(source)
            try:
                driver.find_element_by_xpath('//body/div[4]/div[5]/div[4]/div/div/form[1]/table/tbody/tr[13]/td/input').click()
                
            except NoSuchElementException: pass
            
    next = next_page(html.find(id='paginator').contents) 
    fix(driver, next)
    
def setup():

    data = sqlite3.connect(r'Webscraping\PixivUtil\Data.sqlite')
    CURSOR.executemany(INSERT[2], data.execute(SELECT[5]).fetchall())
    data.close()
    DATAB.commit()
    try:
        driver = get_driver(headless=True)
        login(driver, 'gelbooru')
        login(driver, 'sankaku')
        CURSOR.execute(SELECT[4])
        main(driver, CURSOR.fetchall())
        driver.close()
    except WebDriverException:
        if input(f'Favorites: Browser closed\nContinue? ').lower() in 'yes':
            setup()
    DATAB.close()

if __name__ == '__main__': setup()
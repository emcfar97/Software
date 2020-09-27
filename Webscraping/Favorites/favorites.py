import sqlite3
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re

def main(paths, sankaku=0, gelbooru=0):
    
    if not paths: return
    size = len(paths)
    limit = get_limit(DRIVER)

    for num, (path, href, src, site,) in enumerate(paths):
        progress(size, num, 'favorites')
        
        try:
            DRIVER.get('http://iqdb.org/')
            if src is None:
                DRIVER.find_element_by_xpath('//*[@id="file"]').send_keys(path)
            else:
                DRIVER.find_element_by_xpath('//*[@id="url"]').send_keys(src)
            DRIVER.find_element_by_xpath('//body/form/table[2]/tbody/tr[4]/td[1]/input').click()

            if path.endswith(('gif', 'mp4', 'webm')): time.sleep(20)
            try:
                html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
                too_large = html.findAll(text=re.compile('too large'))
                cant_read = html.findAll(text=re.compile('read query'))
                cant_find = html.findAll(text=re.compile('file was uploaded'))
                
                if too_large or cant_read or cant_find:
                    CONNECTION.execute(UPDATE[4], (1, 0, path))
                    CONNECTION.commit()
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
                # if (sankaku < limit or gelbooru < 50) and not path.endswith(('.gif', '.webm', '.mp4')):
                #     saved, type_ = upload(DRIVER, path, href, src, site)  
                #     if type_: sankaku += 1
                #     else: gelbooru += 1
                pass
                    
            for match in targets:
                DRIVER.get(f'https:{match.get("href")}')
                if 'gelbooru' in match.get("href"):
                    if 'list&' in DRIVER.current_url:
                        saved = True
                        continue
                    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
                    status = html.find(class_='status-notice')
                    if status and 'This post was deleted' in status.text:
                        saved = True
                        continue
                    DRIVER.find_element_by_partial_link_text('Add to favorites').click()
                else:
                    DRIVER.find_element_by_xpath('//*[@title="Add to favorites"]').click()
                saved = True
                            
            if saved:
                if src is None: os.remove(path)
                CONNECTION.execute(UPDATE[4], (1, 1, path))

            CONNECTION.commit()

        except ElementNotInteractableException:
            
            if 'sankaku' in match.get('href'):
                os.remove(path)
                CONNECTION.execute(UPDATE[4], (1, 0, path))

        except FileNotFoundError:
            
            CONNECTION.execute(UPDATE[4], (1, 1, path,))
            CONNECTION.commit()

        except InvalidArgumentException:
            
            CONNECTION.execute(UPDATE[4], (1, 0, path,))
            CONNECTION.commit()
        
        except NoSuchElementException: continue 
            
    progress(size, size, 'favorites')
     
def upload(path, href, src, site):

    if site == 'foundry':
        artist = href.split('/')[3]
        href = f'http://www.hentai-foundry.com{href}'
    elif site == 'furaffinity':
        artist = src.split('/')[4]
        href = f'https://www.furaffinity.net{href}'
    elif site == 'twitter':
        artist = href.split('/')[0]
        href = f'https://twitter.com{href}'
    elif site == 'pixiv':
        artist = path.split('\\')[-1].split('-')[0].strip()
        if href is None:
            href = f"/artworks/{path.split('-')[-1].strip().split('_')[0]}"
        href = f'https://www.pixiv.net{href}'
    try: artist, site = artists_dict[artist]
    except KeyError: return False, 0

    with tempfile.NamedTemporaryFile(suffix='.jpg') as temp:
        
        temp.write(bytes(requests.get(src).content)) 
        tags = get_tags(DRIVER, temp.name)
        if not tags or 'comic' in tags: return False, 0
        general, rating = generate_tags(general=tags, rating=True, exif=False)
        if len(tags) < 10: tags.append('tagme')
        tags = ' '.join(set(tags + general + [artist]))
        
        if site:
            DRIVER.get('https://chan.sankakucomplex.com/post/upload')
            DRIVER.find_element_by_xpath('//*[@id="post_file"]').send_keys(temp.name)
            DRIVER.find_element_by_xpath('//*[@id="post_source"]').send_keys(href)
            DRIVER.find_element_by_xpath('//*[@id="post_tags"]').send_keys(tags)
            DRIVER.find_element_by_tag_name('html').send_keys(Keys.ESCAPE)
            DRIVER.find_element_by_xpath(f'//*[@id="post_rating_{rating}"]').click()
            
            # try:
            DRIVER.find_element_by_xpath('//body/div[4]/div[1]/form/div/table/tfoot/tr/td[2]/input').click()
            # except ElementClickInterceptedException:
            #     DRIVER.find_element_by_xpath('//*[@id="post_tags"]').click()
            #     DRIVER.find_element_by_tag_name('html').send_keys(Keys.ESCAPE)
            #     DRIVER.find_element_by_xpath('//body/div[4]/div[1]/form/div/table/tfoot/tr/td[2]/input').click()
            DRIVER.find_element_by_xpath('//*[@title="Add to favorites"]').click()
        
        else: 
            DRIVER.get('https://gelbooru.com/index.php?page=post&s=add')
            DRIVER.find_element_by_xpath('//body/div[4]/div[4]/form/input[1]').send_keys(temp.name)
            DRIVER.find_element_by_xpath('//body/div[4]/div[4]/form/input[2]').send_keys(href)
            DRIVER.find_element_by_xpath('//*[@id="tags"]').send_keys(tags)
            
            if rating == 'erotic':
                DRIVER.find_element_by_xpath('//body/div[4]/div[4]/form/input[4]').click()
            elif rating == 'questionable':
                DRIVER.find_element_by_xpath('//body/div[4]/div[4]/form/input[5]').click()
            else:
                DRIVER.find_element_by_xpath('//body/div[4]/div[4]/form/input[6]').click()

            DRIVER.find_element_by_xpath('//body/div[4]/div[4]/form/input[7]').click()
            DRIVER.find_element_by_partial_link_text('Add to favorites').click()
        
        return True, site

def get_limit():
    
    DRIVER.get('https://chan.sankakucomplex.com/user/upload_limit')
    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
    return int(html.find('strong').text)

def search(path):

    DRIVER.get('https://gelbooru.com/index.php?page=post&s=list&tags=all')
    
    for file in os.listdir(path):

        hash = file.split('.')[-2]
        try: int(hash, 16)
        except: continue
        if int(hash, 16) < 10000: continue

        DRIVER.find_element_by_xpath('//*[@id="tags-search"]').clear()
        DRIVER.find_element_by_xpath('//*[@id="tags-search"]').send_keys(f'md5:{hash}')
        DRIVER.find_element_by_xpath('//*[@id="tags-search"]').send_keys(Keys.RETURN)
        time.sleep(3)
        html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
        null = html.findAll(text=re.compile('Nobody here but us chickens!'))
        if null: continue
        response = input('Delete? ')
        
        if response.lower() in 'yes': 
            file = join(path, file)
            os.remove(file)
            state = 'DELETE FROM imageDatabase WHERE path=?'
            CONNECTION.execute(state, (path,))
            DRIVER.get('https://gelbooru.com/index.php?page=post&s=list&tags=all')            
   
def fix(url='?page=favorites&s=view&id=173770&pid=50'):
    
    def next_page(pages):
        
        try: return pages[pages.index(' ') + 3].get('href')
        except IndexError: return False
    
    DRIVER.get(f'https://gelbooru.com/index.php{url}')
    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
    hrefs = [
        target.get('href') for target in 
        html.findAll('a', id=re.compile(r'p\d+'), href=True)
        ]
    for href in hrefs:
        
        DRIVER.get(f'https://gelbooru.com/{href}')
        page = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
        source = page.find('a', href=True, rel="nofollow", style=False)
        
        if 'artworks' not in source.text:
            source = source.text.replace('net', 'net/artworks/')
            try:
                DRIVER.find_element_by_xpath('/html/body/div[4]/div[5]/div[4]/div/div/h4/a[1]').click()
            except NoSuchElementException: 
                input('Error')
            DRIVER.find_element_by_xpath('//*[@id="source"]').clear()
            DRIVER.find_element_by_xpath('//*[@id="source"]').send_keys(source)
            try:
                DRIVER.find_element_by_xpath('//body/div[4]/div[5]/div[4]/div/div/form[1]/table/tbody/tr[13]/td/input').click()
                
            except NoSuchElementException: pass
            
    next = next_page(html.find(id='paginator').contents) 
    fix(next)
    
def start():

    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(0)
    
    data = sqlite3.connect(r'Webscraping\PixivUtil\Data.sqlite')
    CONNECTION.execute(INSERT[2], data.execute(SELECT[5]).fetchall(), many=1, commit=1)
    data.close()

    DRIVER.login('gelbooru')
    DRIVER.login('sankaku')
    main(CONNECTION.execute(SELECT[4], fetch=1))
    DRIVER.close()
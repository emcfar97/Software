import sqlite3, json, os, time, tempfile
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import Progress, get_tags, generate_tags, bs4, requests, re
import selenium.common.exceptions as exceptions
from selenium.webdriver.common.keys import Keys

EXT = '.gif', '.webm', '.mp4'
IGNORE = '(too large)|(read query)|(file was uploaded)|(request failed:)'

def main(paths, upload=False, sankaku=0, gelbooru=0):
    
    if not paths: return
    if upload:
        limit = get_limit()
        artists = json.load(open(
            r'Webscraping\artists.json', encoding='utf8'
            ))
    progress = Progress(len(paths), 'favorites')

    for (path, href, src, site,) in paths:
        
        print(progress)
        
        DRIVER.get('http://iqdb.org/')
        try:
            if src: DRIVER.find('//*[@id="url"]', src, fetch=1)
            else: DRIVER.find('//*[@id="file"]', path, fetch=1)
        except exceptions.InvalidArgumentException:
            CONNECTION.execute(UPDATE[4], (1, 0, path), commit=1)
            continue
        DRIVER.find('//body/form/table[2]/tbody/tr[4]/td[1]/input', click=True)
        if path.endswith(EXT): time.sleep(25)
        
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        if html.find(text=re.compile(IGNORE)):
            CONNECTION.execute(UPDATE[4], (1, 0, path), commit=1)
            continue
        try:
            targets = [
            target.find(href=re.compile('/gelbooru|/chan.san')) 
            for target in html.find(id='pages', class_='pages').contents 
            if type(target) != bs4.element.NavigableString and 
            target.findAll(href=re.compile('/gelbooru|/chan.san')) and 
            target.findAll(text=re.compile('(Best)|(Additional) match'))
            ]
        except: continue
        
        if targets and not upload:
            try: saved = favorite(targets)
            except: saved = False
        elif upload and (sankaku < limit or gelbooru < 50):
            saved, type_ = upload(path, href, src, site, artists)  
            if type_: sankaku += 1
            else: gelbooru += 1
        else: saved = False
                        
        if saved and src is None: os.remove(path)
        CONNECTION.execute(UPDATE[4], (1, saved, path), commit=1)

    print(progress)

def favorite(targets, saved=False):

    for match in targets:
        DRIVER.get(f'https:{match.get("href")}')
        if'gelbooru' in match.get('href') and'list&'not in DRIVER.current_url():
            DRIVER.find('Add to favorites', click=True, type_=4)
        else:
            element = DRIVER.find('//*[@title="Add to favorites"]')
            try: element.click()
            except exceptions.ElementClickInterceptedException: 
                DRIVER.active_element().click()
                element.click()
            except exceptions.ElementNotInteractableException: pass

        saved = True

    return saved
     
def upload(path, href, src, site, artists):

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
    try: artist, site = artists[artist]
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

def edit(search, replace):
    
    address = '/html/body/div[4]/div/div[2]/div[8]/form/table/tfoot/tr/td/input'
    driver = WEBDRIVER(0, None, wait=30)
    driver.login('sankaku', 'chan')
    driver.get(f'https://chan.sankakucomplex.com?tags={search}')
    html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
    hrefs = [
        target.get('href') for target in 
        html.findAll('a', {'onclick': True}, href=re.compile('/p+'))
        ]

    for href in hrefs:

        driver.get(f'https://chan.sankakucomplex.com{href}')
        time.sleep(6)
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        tags = html.find('textarea').contents[0]

        text = re.sub(search.replace('*', '.*'), replace, tags)
        driver.find('//*[@id="post_tags"]').clear()
        driver.find('//*[@id="post_tags"]', keys=text)

        try: element = driver.find(address, click=True)
        except exceptions.ElementClickInterceptedException: 
            driver.active_element().click()
            element.click()
        
def initialize():
    
    data = sqlite3.connect(r'Webscraping\PixivUtil\Data.sqlite')
    CONNECTION.execute(
        INSERT[2], data.execute(SELECT[5]).fetchall(), many=1, commit=1
        )
    data.close()
    
    # paths = list()
    # for site in ['foundry', 'furaffinity', 'misc', 'twitter']:

    #     paths += [
    #         (str(path), None, site) for path in 
    #         (PATH / 'Images' / site).iterdir()
    #         ]

    # CONNECTION.execute(INSERT[2], paths, many=1, commit=1)

def start(initial=1, headless=True):

    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(headless, wait=30)
    
    if initial: initialize()
    main(CONNECTION.execute(SELECT[4], fetch=1))
    DRIVER.close()
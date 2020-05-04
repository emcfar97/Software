import re, bs4, threading, time
from utils import DATAB, CURSOR, get_driver
from selenium.webdriver.common.keys import Keys

MODE = {
    0:['idol', 0], 1:['chan', 1]
    }
SELECT = 'SELECT COUNT(*) FROM imageData WHERE site="sankaku" AND type=%s'
INSERT = 'INSERT IGNORE INTO imageData(type, href, site) VALUES(%s, %s, "sankaku")'

def favorites(type_):
    
    driver = get_driver(True)
    mode = MODE[type_]

    url = f'https://{mode[0]}.sankakucomplex.com/?tags=fav%3Achairekakia'
    driver.get(url)
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')

    total = html.find(text=re.compile('has .+ favorites'))
    total = int(''.join(re.findall('\d', total)))
    CURSOR.execute(SELECT, (mode[1],))
    current, = CURSOR.fetchall()[0]

    while current <= total:
        
        for _ in range(60):
            driver.find_element_by_tag_name('html').send_keys(Keys.END)
            html = bs4.BeautifulSoup(driver.page_source, 'lxml')
            
            try:
                hrefs = [
                    (mode[1], href.get('href')) for href in 
                    html.findAll(href=re.compile('/post/show/\d.+'))
                    ]
                while True:
                    try:
                        CURSOR.executemany(INSERT, hrefs)
                        DATAB.commit()
                        break
                    except: continue
                CURSOR.execute(SELECT, (mode[1],))
                current, = CURSOR.fetchall()[0]
                
            except: continue
            time.sleep(3)
        
        url = f'https://{mode[0]}.sankakucomplex.com/?tags=fav%3Achairekakia+order%3Arandom' 
        driver.get(url)
        if html.find(text=re.compile('(Too many requests)|(Please slow down)')):
            time.sleep(80)
            driver.refresh()
            html = bs4.BeautifulSoup(driver.page_source, 'lxml')

favorites(0)
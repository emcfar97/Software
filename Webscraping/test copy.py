import re, requests, bs4, threading, time
import mysql.connector as sql
from utils import DATAB, CURSOR

MODE = {
    0:['idol', 0], 1:['chan', 1]
    }
SELECT = 'SELECT COUNT(*) FROM imageData WHERE site="sankaku" AND type=%s'
INSERT = 'INSERT INTO imageData(type, href, site) VALUES(%s, %s, "sankaku")'

def favorites(type_):
    
    mode = MODE[type_]

    url = f'https://{mode[0]}.sankakucomplex.com/?tags=fav%3Achairekakia+order%3Arandom'
    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')

    total = html.find(text=re.compile('has .+ favorites'))
    total = int(''.join(re.findall('\d', total)))
    CURSOR.execute(SELECT, (mode[1],))
    current, = CURSOR.fetchall()[0]

    while current <= total:
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
            
            page_source = requests.get(url).content
            html = bs4.BeautifulSoup(page_source, 'lxml')
            if html.find(text=re.compile('(Too many requests)|(Please slow down)')):
                time.sleep(80)
                page_source = requests.get(url).content  
                html = bs4.BeautifulSoup(page_source, 'lxml')

        except: continue

threads = [
    threading.Thread(target=favorites, args=(0,)),
    threading.Thread(target=favorites, args=(1,))
    ]
for thread in threads: thread.start()
for thread in threads: thread.join()
import json, time
from os import path 
from . import USER
from .utils import bs4, requests, re

PATH = USER / r'Downloads\Images'

def page_handler(url, title, page=0): 
    
    path = PATH / 'Games'/ title
    try: path.mkdir()
    except: pass

    while True:

        page_source = requests.get(f'{url}?p={page}').content
        html = bs4.BeautifulSoup(page_source, 'lxml')

        for image in html.findAll(class_='gdtm'):

            href = image.find(href=True).get('href')
            page_source = requests.get(href).content
            page = bs4.BeautifulSoup(page_source, 'lxml')

            src = page.find(src=True)
            name = html.find(title=True)
            name = path / name.split(': ')[-1]
            name.write_bytes(requests.get(src).content)
            time.sleep(60)
        
        else:
            if timeout := html.find(
                text=re.compile('Your IP address has been temporarily.+')
                ):
                print(timeout)
                timeout = timeout.split('.')[-1].split()
                time.sleep((int(timeout[4]) * 60) + int(timeout[7]))

        page += 1

def start():
        
    for file in PATH.glob('*json'):

        file = json.load(open(file))[0]['windows']
        for val in file.values():
            for url in val.values():
                page_handler(url['url'], url['title'])
        file.remove()

if __name__ == '__main__':
    
    start()
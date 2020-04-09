import os, json, bs4, re, time, requests
from os.path import join

ROOT = os.getcwd()[:2].upper()
PATH = rf'{ROOT}\Users\Emc11\Downloads'

def page_handler(url, title, page=0): 
    
    path = join(PATH, title)
    os.mkdir(path)

    while True:

        page_source = requests.get(f'{url}?p={page}').content
        html = bs4.BeautifulSoup(page_source, 'lxml')

        for image in html.findAll(class_='gdtl'):

            href = image.find(href=True).get('href')
            page_source = requests.get(href).content
            html = bs4.BeautifulSoup(page_source, 'lxml')
            src = html.find(src=True)
            name = None

            with open(join(path, name), 'wb') as image:
                image.write(requests.get(src).content)
            time.sleep(1)
        
        else:
            if timeout := html.find(
                text=re.compile('Your IP address has been temporarily.+')
                ):
                timeout = timeout.split('.')[-1].split()
                time.sleep((int(timeout[4]) * 60) + int(timeout[7]))

        time.sleep(2)
        page += 1

files = [
    join(PATH, file) for file in os.listdir(PATH) 
    if file.endswith('json')
    ]

for file in files:

    file = json.load(open(file))[0]['windows']
    for val in file.values():
        for url in val.values():
            page_handler(url['url'], url['title'])
    os.remove(file)
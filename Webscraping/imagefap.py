import os, json, bs4, re, requests
from os.path import join

ROOT = os.getcwd()[:2].upper()
PATH = rf'{ROOT}\Users\Emc11\Downloads'

def page_handler(url, title): 
    
    try: url = f'{url}?gid={url.split("/")[4]}&view=2'
    except IndexError: url = f'https://{title}&view=2'
    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    images = html.findAll(href=re.compile('/photo/.+'))

    for image in images:

        href = f'https://www.imagefap.com/{image.get("href")}'
        page_source = requests.get(href).content
        target = bs4.BeautifulSoup(page_source, 'lxml')
        src = target.find(src=re.compile('https://cdn.imagefap.com/images/full/.+')).get('src')

        name = src.split('?')[0].split('/')[-1]
        with open(join(PATH, name), 'wb') as image:
            image.write(requests.get(src).content)
    
files = [
    join(PATH, file) for file in os.listdir(PATH) 
    if file.endswith('json')
    ]

for file in files:

    window = json.load(open(file))[0]['windows']
    for val in window.values():
        for url in val.values():
            page_handler(url['url'], url['title'])
    os.remove(file)
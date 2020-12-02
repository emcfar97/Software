import os
from . import WEBDRIVER, ROOT
from .utils import bs4, requests, re, time, Image, BytesIO
from selenium.webdriver.common.keys import Keys

path =  ROOT / r'E:\Users\Emc11\Training\New folder'

def unsplash(images, folder, type_):

    driver = WEBDRIVER()
    driver.get(f'https://unsplash.com/images/{type_}')
    total = set()

    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        targets = html.findAll('img', src=re.compile(
            'https://images.unsplash.com/pho+')
            )
        targets = set(targets) - total

        for target in targets:
            src = target.get('src')
            image = Image.open(BytesIO(requests.get(src).content))
            name = f"{hash(src)}.{image.format}"
            if exists(name): continue
            image.thumbnail([512, 512])
            image.save(join(path, folder, name))

        total = total | targets
        for _ in range(2):
            driver.find('html', Keys.PAGE_DOWN)
            time.sleep(2)

    driver.close()

def shutterstock(images, folder, cate, type_):

    driver = WEBDRIVER()
    driver.get(f'https://www.shutterstock.com/search/{cate}?image_type={type_}&safe=off')
    total = set()

    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        targets = html.findAll('img', src=re.compile(
            f'https://image.shutterstock.com/image-{type_}+')
            )
        targets = set(targets) - total

        for target in targets:
            src = target.get('src')
            image = Image.open(BytesIO(requests.get(src).content))
            name = f"{hash(src)}.{image.format}"
            if exists(name): continue
            image.thumbnail([500, 500])
            image = image.crop([0, 0, image.width, image.height - 25])
            image.save(join(path, folder, name))

        total = total | targets
        driver.find('//body/div[2]/div[2]/div/div[2]/div[2]/main/div/div[2]/div[2]/div/div/a[2]', click=True)

    driver.close()

def pinterest(images, folder, boards, user='chairekakia'):

    driver = WEBDRIVER()
    driver.login('pinterest')
    for board in boards[0]:
        for section in boards[1]:

            driver.get(f'https://pinterest.com/{user}/{board}/{section}')
            time.sleep(2)
            total = set()

            while len(total) < images:
                html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
                targets = html.find(class_="gridCentered").findAll(
                    'img', src=re.compile(f'https://i.pinimg.com/+')
                    )
                targets = set(targets) - total
                if not targets: break

                for target in targets:
                    src = target.get('src')
                    image = Image.open(BytesIO(requests.get(src).content))
                    name = f"{hash(src)}.{image.format}"
                    if exists(name): continue
                    image.thumbnail([500, 500])
                    image.save(join(path, folder, name))

                total = total | targets
                for _ in range(2):
                    driver.find('html', Keys.PAGE_DOWN)
                    time.sleep(2)

    driver.close()

def fineartamerica(images, folder, type_):

    driver = WEBDRIVER()
    driver.get(f'https://fineartamerica.com/art/{type_}')
    total = set()

    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        targets = html.findAll('img', src=re.compile(
            'https://render.fineartamerica.com/imag+')
            )
        targets = set(targets) - total

        for target in targets:
            src = target.get('src')
            image = Image.open(BytesIO(requests.get(src).content))
            name = f"{hash(src)}.{image.format}"
            if exists(name): targets.remove(target); continue
            image.thumbnail([500, 500])
            image.save(join(path, folder, name))

        total = total | targets
        driver.find_element_by_xpath('//*[@id="topPaginationDiv"]/div/a[5]').click()

    driver.close()

def turbosquid(images, folder, type_):

    driver = WEBDRIVER()
    driver.get(f'https://www.turbosquid.com/Search/3D-Models/{type_}')
    total = set()

    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        targets = html.findAll('img', src=re.compile(
            'https://static.turbosquid.com/Preview+')
            )
        targets = set(targets) - total

        for target in targets:
            
            src = target.get('src')
            image = Image.open(BytesIO(requests.get(src).content))
            name = path / f"{hash(src)}.{image.format.lower()}"
            if name.exists(): continue
            image.thumbnail([500, 500])
            image.save(name)

        total = total | targets
        driver.find('//*[@id="ts-paging-next-btn"]/div/span', click=True)

    driver.close()

def localfiles(images, srce, dest):

    total = set()

    while len(total) < images:
        targets = os.listdir(join(path, srce))
        targets = set(targets) - total

        for target in targets:
            src = join(path, srce, target)
            try: image = Image.open(src)
            except: continue
            name = f"{hash(src)}.{image.format}"
            if exists(name): targets.remove(target); continue
            image.thumbnail([500, 500])
            image.save(join(path, dest, name))
            os.remove(src)

        total = total | targets

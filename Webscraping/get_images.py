import re, time, os, pywinauto, pyautogui
from os.path import exists, join
from utils import get_driver, bs4, requests, Image, BytesIO, login
from selenium.webdriver.common.keys import Keys
from pywinauto.application import Application

LOCATION = {
    'subtool': []
}

path = r'C:\Users\Emc11\Dropbox\Pictures\4.Reference\5.Machine Learning'

if __file__.startswith(('e:\\', 'e:/')):
    
    path = path.replace("C:", "E:")

def unsplash(images, folder, type_): 
    
    driver = get_driver(False)
    driver.get(f'https://unsplash.com/images/{type_}')
    total = set()
    
    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        targets = html.findAll('img', src=re.compile(
            'https://images.unsplash.com/pho+')
            )
        targets = set(targets) - total
        
        for target in targets:
            src = target.get('src')
            image = Image.open(BytesIO(requests.get(src).content))
            name = f"{hash(src)}.{image.format}"
            if exists(name): continue
            image.thumbnail([500, 500])
            image.save(join(path, folder, name))
        
        total = total | targets
        for _ in range(2):
            driver.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)
            
    driver.close()
            
def shutterstock(images, folder, cate, type_): 
    
    driver = get_driver(False)
    driver.get(f'https://www.shutterstock.com/search/{cate}?image_type={type_}&safe=off')
    total = set()
    
    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
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
        driver.find_element_by_xpath('//body/div[2]/div[2]/div/div[2]/div[2]/main/div/div[2]/div[2]/div/div/a[2]').click()
        
    driver.close()

def pinterest(images, folder, boards, user='chairekakia'): 
    
    driver = get_driver(False)
    login(driver, 'pinterest')
    for board in boards[0]:
        for section in boards[1]:
            
            driver.get(f'https://pinterest.com/{user}/{board}/{section}')
            time.sleep(2)
            total = set()
            
            while len(total) < images:
                html = bs4.BeautifulSoup(driver.page_source, 'lxml')
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
                    driver.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(2)
                
    driver.close()

def fineartamerica(images, folder, type_):

    driver = get_driver(False)
    driver.get(f'https://fineartamerica.com/art/{type_}')
    total = set()
    
    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
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

def clipstudio(images, folder): pass

def turbosquid(images, folder, type_):
    
    driver = get_driver(False)
    driver.get(f'https://www.turbosquid.com/Search/3D-Models/{type_}')
    total = set()
    
    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        targets = html.findAll('img', src=re.compile(
            'https://static.turbosquid.com/Preview+')
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
        driver.find_element_by_xpath('//*[@id="ts-paging-next-btn"]/div/span').click()
            
    driver.close()

def gelbooru(images, folder, tags):
    
    driver = get_driver(False)
    driver.get(f'https://gelbooru.com/&s=list&tags={"+".join(tags)}')
    total = set()

    while len(total) < images:
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        targets = html.findAll('a', id=re.compile(r'p\d+'), href=True)
        targets = set(targets) - total
        
        # for target in targets:
        #     src = target.get('src')
        #     image = Image.open(BytesIO(requests.get(src).content))
        #     name = f"{hash(src)}.{image.format}"
        #     if exists(name): targets.remove(target); continue
        #     image.thumbnail([500, 500])
        #     image.save(join(path, folder, name))
        
        total = total | targets
        pages = html.find(id='paginator').contents[pages.index(' ') + 3]
        driver.get(f"https://gelbooru.com/{pages.get('href')}")

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

# unsplash(1000, r'')
# shutterstock(2000, r'Medium\Illustration', 'landscape', 'illustration')
# boards = ['your-pinterest-likes'], ['']
# pinterest(125, r'Medium\Photograph', boards, 0)
# pinterest(220, r'Medium\Illustration', boards, 1)
# fineartamerica(500, r'Medium\Illustration', 'paintings')
# localfiles(1000, r'Medium', r'Medium\Illustration')
# turbosquid(1000, r'Medium\3-Dimensional', 'low-poly')
# clipstudio(1000, r'Medium\3-Dimensional')
gelbooru(2200, r'Medium\3-Dimensional', ['3d', 'rating%3asafe', '-animated', '-custom_maid_3d_2', '-3d_custom_girl'])
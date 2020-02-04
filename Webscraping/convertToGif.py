import requests, threading
from math import log
from bs4 import BeautifulSoup
from os import listdir, remove, getcwd
from os.path import join, splitext
from utils import get_driver, progress
from selenium.webdriver.support.ui import Select

SUM = 0
EXT = 'webm', 'webp', 'mp4'
root = getcwd()[:2].upper()
PATH = rf'{root}\Users\Emc11\Downloads'
DEST = rf'{root}\Users\Emc11\Dropbox\Pictures\4.Reference\3.Gifs'

if __file__.startswith(('e:\\', 'e:/')):

    PATH = PATH.replace('C:', 'E:')
    DEST = DEST.replace('C:', 'E:')

def main(paths, lock=False):

    global SUM
    driver = get_driver(True)
    upload = '//body/div/div[4]/div[2]/form/fieldset/p[4]/input'
    
    for path, dest in paths:
        
        progress(size, SUM, 'Files')
        driver.get('https://ezgif.com/video-to-gif')
        driver.find_element_by_xpath('//*[@id="new-image"]').send_keys(path)
        driver.find_element_by_xpath(upload).click()

        if path.endswith('.webp'):
            driver.find_element_by_name('make-a-gif').click()
        else:
            while True:
                try:
                    stats = driver.find_element_by_class_name('filestats')
                    break
                except: pass
            stats = stats.text.split(', ')[3].split(':')[2:]
            seconds = int(stats[0]) * 60 + int(stats[1])
            driver.find_element_by_name('end').clear()
            driver.find_element_by_name('end').send_keys(f'{seconds}')

            if 61 <= seconds: continue
            else:
                fps = Select(driver.find_element_by_name('fps'))
                fps.select_by_value(switch(seconds))
            driver.find_element_by_name('video-to-gif').click()
            
        while True:
            try:
                driver.find_element_by_class_name('m-btn-optimize').click()
                break
            except: pass
        driver.find_element_by_name('optimize').click()
        image = '//body/div/div[3]/div[2]/div[2]/p[1]/img'
        while True:
            try:
                image = driver.find_element_by_xpath(image)
                break
            except: pass
        
        html = BeautifulSoup(driver.page_source, 'lxml')
        image = html.find('img', src=True, alt='[optimize output image]')
        with open(splitext(dest)[0] + '.gif', 'wb') as file:
            file.write(requests.get(f'https:{image.get("src")}').content)
        
        remove(path)
        if lock:
            lock.acquire()
            SUM += 1
            lock.release()
        
    progress(size, SUM, 'Files')
    driver.close()

def switch(seconds):

    if 40 < seconds:         return '5'
    elif 30 < seconds <= 40: return '7'
    elif 15 < seconds <= 30: return '10'
    elif 10 < seconds <= 15: return '20'
    elif seconds <= 10:      return '25'

paths = [
    (join(PATH, path), join(DEST, path)) 
    for path in listdir(PATH) if path.endswith(EXT)
    ]

lock = threading.Lock()
size = len(paths)
thr = int(2 * log(len(paths), 10) + 1)
num, div = divmod(size, thr)

threads = [
    threading.Thread(
        target=main, 
        args=(
            paths[i * num + min(i, div):(i+1) * num + min(i+1, div)], lock
            ))
    for i in range(thr)
    ]
for thread in threads: thread.start()
for thread in threads: thread.join()
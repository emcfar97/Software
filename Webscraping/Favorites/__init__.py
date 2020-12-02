import threading, subprocess
from . import favorites, foundry, furaffinity, twitter

def start():

    process = subprocess.Popen([
        r'Webscraping\PixivUtil\PixivUtil2.exe',
        '-s', '6', 'y', '', '0', '400', '', '-x'
        #              start end  stop
        ])
    
    threads = [
        threading.Thread(target=process.wait),
        # threading.Thread(target=furaffinity.start),
        # threading.Thread(target=foundry.start),
        # threading.Thread(target=twitter.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    favorites.start()
import subprocess, threading
from Webscraping import flickr, foundry, furaffinity, gelbooru, sankaku, posespace, twitter, favorites

def erotica3():

    # process = subprocess.Popen([
    #     r'Webscraping\PixivUtil\PixivUtil2.exe',
    #     '-s', '6', 'y', '0', '7', '-x'
    #     #              start end  stop
    #     ])
    threads = [
        threading.Thread(target=webscrapers),
        # threading.Thread(target=process.wait)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    
    favorites.setup()
    
    threads = [
        threading.Thread(target=gelbooru.setup),
        threading.Thread(target=sankaku.setup)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

def webscrapers():

    # furaffinity.setup()
    # foundry.setup()
    twitter.setup()

threads = [
    # threading.Thread(target=flickr.setup),
    threading.Thread(target=erotica3),
    # threading.Thread(target=posespace.setup)
    ]
for thread in threads: thread.start()
for thread in threads: thread.join()

print('Complete')

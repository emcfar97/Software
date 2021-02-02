from . import favorites, foundry, furaffinity, twitter

def start():

    import threading, subprocess

    # process = subprocess.Popen([
    #     r'Webscraping\PixivUtil\PixivUtil2.exe',
    #     '-i', '6', ''#, '', '0', '7', '', '-x'
    #     #              start end  stop
    #     ])
    
    threads = [
        # threading.Thread(target=process.wait),
        threading.Thread(target=foundry.start),
        threading.Thread(target=furaffinity.start),
        threading.Thread(target=twitter.start),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    favorites.start()
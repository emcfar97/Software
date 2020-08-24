import threading
from .. import WEBDRIVER
from . import foundry, furaffinity, twitter

def start():

    threads = [
        threading.Thread(target=furaffinity.setup, args=(WEBDRIVER(),)),
        threading.Thread(target=foundry.setup, args=(WEBDRIVER(),)),
        threading.Thread(target=twitter.setup, args=(WEBDRIVER(),))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

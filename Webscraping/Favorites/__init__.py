import threading
from . import favorites, foundry, furaffinity, twitter

def start():

    threads = [
        threading.Thread(target=furaffinity.start),
        threading.Thread(target=foundry.start),
        # threading.Thread(target=twitter.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    favorites.start()
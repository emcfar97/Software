import threading
from . import foundry, furaffinity, twitter

def start():

    threads = [
        threading.Thread(target=furaffinity.setup),
        threading.Thread(target=foundry.setup),
        threading.Thread(target=twitter.setup)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

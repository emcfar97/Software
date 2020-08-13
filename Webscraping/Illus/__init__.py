import threading
from ..utils import *
from . import gelbooru, sankaku

def start():

    threads = [
        threading.Thread(target=gelbooru.setup),
        threading.Thread(target=sankaku.setup, args=(1,))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
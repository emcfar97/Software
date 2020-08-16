import threading
from . import gelbooru
from ..utils import *
from .. import Favorites, sankaku

def start():

    Favorites.start()

    threads = [
        threading.Thread(target=gelbooru.setup),
        threading.Thread(target=sankaku.setup, args=(1,))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
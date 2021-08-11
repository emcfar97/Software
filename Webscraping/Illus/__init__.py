import threading
from . import gelbooru
from .. import Favorites, sankaku

def start(initialize=True, favorites=True):

    if favorites: Favorites.start()

    threads = [
        threading.Thread(target=gelbooru.start, args=(initialize,)),
        threading.Thread(target=sankaku.start, args=(initialize, 1))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
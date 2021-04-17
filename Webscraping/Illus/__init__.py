import threading
from . import gelbooru
from .. import Favorites, sankaku

def start(initialize=True):

    Favorites.start()

    threads = [
        threading.Thread(target=gelbooru.start, args=(initialize,)),
        threading.Thread(target=sankaku.start, args=(1, initialize))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
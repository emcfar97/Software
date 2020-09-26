import threading
from . import gelbooru
from .. import Favorites, sankaku

def start():

    # Favorites.start()

    threads = [
        threading.Thread(target=gelbooru.start),
        # threading.Thread(target=sankaku.start, args=(1,))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
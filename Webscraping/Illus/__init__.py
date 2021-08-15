def start(initialize=1, favorites=True):
    
    import threading
    from . import gelbooru
    from .. import Favorites, sankaku

    if favorites: Favorites.start()

    threads = [
        threading.Thread(target=gelbooru.start, args=(initialize,)),
        threading.Thread(target=sankaku.start, args=(initialize, True, 1))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
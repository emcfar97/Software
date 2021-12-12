def main(initialize=1, favorites=True, depth=1000):
    
    import threading
    from . import gelbooru
    from .. import Favorites, sankaku

    if favorites: Favorites.main(initialize, depth)

    threads = [
        threading.Thread(target=gelbooru.start, args=(initialize,)),
        threading.Thread(target=sankaku.start, args=(initialize, True, 1))
        ]
    for thread in threads: thread.main()
    for thread in threads: thread.join()
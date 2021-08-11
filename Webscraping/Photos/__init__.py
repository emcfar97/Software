from .. import sankaku
from . import flickr, posespace, elitebabes, instagram, blogspot

def start(initialize=True):

    import threading 

    threads = [
        threading.Thread(target=flickr.start, args=(initialize,)),
        threading.Thread(target=elitebabes.start, args=(initialize,)),
        # threading.Thread(target=instagram.start, args=(initiailze,)),
        # threading.Thread(target=posespace.start, args=(initiailze,))
        threading.Thread(target=sankaku.start, args=(initialize, 0)),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
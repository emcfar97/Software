from .. import sankaku
from . import flickr, imagefap, posespace, elitebabes, instagram, pinterest, blogspot

def start():

    import threading 

    threads = [
        threading.Thread(target=flickr.start),
        threading.Thread(target=elitebabes.start),
        # threading.Thread(target=instagram.start),
        # threading.Thread(target=posespace.start)
        threading.Thread(target=sankaku.start, args=(0,)),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
import threading
from .. import sankaku
from . import flickr, posespace, metart, elitebabes, femjoy, imagefap, instagram, pinterest, blogspot, toplesspulp

def start():

    threads = [
        # threading.Thread(target=metart.start),
        # threading.Thread(target=elitebabes.start),
        # threading.Thread(target=femjoy.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    threads = [
        threading.Thread(target=flickr.start),
        threading.Thread(target=sankaku.start, args=(0,)),
        # threading.Thread(target=posespace.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
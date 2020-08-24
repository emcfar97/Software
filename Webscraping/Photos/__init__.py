import threading
from .. import WEBDRIVER, sankaku
from . import flickr, posespace, metart, elitebabes, femjoy

def start():

    threads = [
        threading.Thread(target=metart.setup, args=(WEBDRIVER(),)),
        threading.Thread(target=elitebabes.setup, args=(WEBDRIVER(),)),
        threading.Thread(target=femjoy.setup, args=(WEBDRIVER(),)),
        ]
    # for thread in threads: thread.start()
    # for thread in threads: thread.join()

    threads = [
        threading.Thread(target=flickr.setup, args=(WEBDRIVER(),)),
        threading.Thread(target=sankaku.setup, args=(WEBDRIVER(), 0))
        # threading.Thread(target=posespace.setup, args=(WEBDRIVER(),))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
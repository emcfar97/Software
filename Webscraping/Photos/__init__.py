import threading
from ..utils import *
from .. import sankaku
from . import flickr, posespace, metart, elitebabes, femjoy

def start():

    threads = [
        threading.Thread(target=flickr.setup),
        threading.Thread(target=sankaku.setup, args=(0,))
        # threading.Thread(target=posespace.setup)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
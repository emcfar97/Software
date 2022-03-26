def main(initialize=1):

    import threading 

    from .. import sankaku
    from . import posespace, elitebabes, instagram, blogspot
    
    threads = [
        threading.Thread(target=elitebabes.main, args=(initialize,)),
        # threading.Thread(target=instagram.main, args=(initiailze,)),
        # threading.Thread(target=posespace.main, args=(initiailze,))
        threading.Thread(target=sankaku.main, args=(initialize, True, 0)),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
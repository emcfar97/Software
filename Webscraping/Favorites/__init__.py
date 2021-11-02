def start(initialize=1, depth=1000):

    import threading, subprocess
    from . import favorites, foundry, furaffinity, twitter

    # process = subprocess.Popen([
    #     r'python Webscraping\Pixivutil\PixivUtil2.py --start_action 6 --ep 7',
    #     ])
    
    threads = [
        # threading.Thread(target=process.wait),
        threading.Thread(target=twitter.start, args=(initialize,)),
        threading.Thread(target=foundry.start, args=(initialize,)),
        threading.Thread(target=furaffinity.start, args=(initialize,)),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    favorites.start(initialize, depth=depth)
def main(initialize=1, depth=-1):

    import threading, subprocess
    from . import favorites, foundry, furaffinity, twitter

    if initialize:
        
        process = subprocess.Popen(
            r'Webscraping\PixivUtil2\PixivUtil2.exe -s 6 --ep 25 -x'
            )
        
        threads = [
            threading.Thread(target=process.wait),
            threading.Thread(target=twitter.main, args=(initialize,)),
            threading.Thread(target=foundry.main, args=(initialize,)),
            threading.Thread(target=furaffinity.main, args=(initialize,)),
            ]
        for thread in threads: thread.start()
        for thread in threads: thread.join()

    favorites.main(initialize, depth=depth)
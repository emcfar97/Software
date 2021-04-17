import threading, time, argparse, re
from Webscraping import WEBDRIVER
import selenium.common.exceptions as exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PLAY = '//*[@class="LiveTapToPlay"]'
CHAT = '//*[@id="UserLiveSidebarToggle"]'
CONTROL = '//*[@class="StreamBodyCtrlBody"]'
ACCEPT = '//body/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]'
HIGH = '//body/div[2]/div[2]/div[2]/div[1]/div[2]/div/div[2]/button'
FINISHED = '//*[@id="UserLiveFinishedBody"]'

class Browser(WEBDRIVER):

    def __init__(self, profile=True):

        super().__init__(headless=False, profile=profile, wait=15)
        self.get('https://sketch.pixiv.net/followings')
        self.driver.fullscreen_window()
        self.run()

    def run(self):

        while True:
            
            try:
                if '@' in self.current_url(): self.live_stream()
                
            except exceptions.WebDriverException: self.close(); break

            except Exception as error: print(f'\n{error}\n')

            threading.Timer(5, function=None)

    def live_stream(self, wait=60, retry=0):

        while re.match('.+/@.+/lives/\d+', self.current_url()):

            try:

                self.find(PLAY, click=True, fetch=1)
                time.sleep(5)
                self.find(CHAT, click=True)

                if retry < 5:
                    
                    target = self.find(CONTROL, fetch=1) \
                        .find_elements_by_class_name('StreamBodyCtrlButton')
                    self.driver.execute_script(
                        "arguments[0].style.visibility='visible'",
                        self.find(CONTROL, fetch=1)
                        )

                    target[0].click()
                    target[-1].click()
                    self.find(HIGH, click=True)
                    self.find(ACCEPT, click=True)
                    
                    retry += 1

            except exceptions.WebDriverException: break
            except exceptions.ElementClickInterceptedException: self.refresh()

            now = time.gmtime()[4]
            threading.Timer(wait * (now // 2), function=None)
            if (now % 30) == 0: retry = 0

def start(): Browser()

parser = argparse.ArgumentParser(
    prog='manage_streams', 
    description='Automate recording of streams via OBS'
    )
parser.add_argument(
    '-n', '--num', type=int,
    help='Number of streams', default=2
    )
args = parser.parse_args()

threads = [
    threading.Thread(target=start)
    for _ in range(args.num)
    ]
for thread in threads: thread.start()
for thread in threads: thread.join()
import argparse
from time import sleep, gmtime
from Webscraping import WEBDRIVER
from pywinauto import Application
from threading import Thread, Timer
import selenium.common.exceptions as exceptions

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
        self.obs = Application(backend='uia').start(
            work_dir=r'C:\Program Files\obs-studio\bin\64bit',
            cmd_line=r'C:\Program Files\obs-studio\bin\64bit\obs64.exe'
            )
        self.run()

    def run(self):

        while True:
            
            try:
                if 'lives' in self.current_url():

                    self.obs.top_window().child_window(
                        title='Start Recording', 
                        control_type='CheckBox',
                        ).click()

                    self.live_stream()

                    self.obs.top_window().child_window(
                        title='Stop Recording', 
                        control_type='CheckBox',
                        ).click()
                
            except exceptions.WebDriverException: break

            except Exception as error: print(f'\n{error}\n')

            Timer(5, function=None)

        self.close()

    def live_stream(self, wait=60, retry=0):

        self.set_window()
        
        while 'lives' in self.current_url():

            try:

                self.find(PLAY, click=True, fetch=1)
                sleep(5)
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

            except exceptions.ElementClickInterceptedException: self.refresh()
                
            except: pass

            if self.find(FINISHED): self.driver.back()
                            
            now = gmtime()[4]
            Timer(wait * (now // 2), function=None)
            if (now % 30) == 0: retry = 0

    def set_window(self,):

        title = f'[firefox.exe]: {self.driver.title} — Mozilla Firefox'
        pass

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
    Thread(target=start) for _ in range(args.num)
    ]
for thread in threads: thread.start()
for thread in threads: thread.join()
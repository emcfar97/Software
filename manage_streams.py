import argparse, re
from Webscraping import WEBDRIVER
from pywinauto import Application
from threading import Thread, Timer
import selenium.common.exceptions as exceptions

CHAT = '//*[@class="visible"]/*[@id="UserLiveSidebarToggle"]'
PLAY = '//*[@class="LiveTapToPlay"]'
CONTROL = '//*[@class="StreamBodyCtrlBody"]'
HIGH = '//*[@class="RadioButton 1"]/button'
ACCEPT = '//button[text()="Select"]'
FINISHED = '//*[@id="UserLiveFinishedBody"]'

class Browser(WEBDRIVER):
    
    def __init__(self, profile=True):

        super().__init__(headless=False, profile=profile, wait=15)
        self.obs = Application(backend='uia').start(
            work_dir=r'C:\Program Files\obs-studio\bin\64bit',
            cmd_line=r'C:\Program Files\obs-studio\bin\64bit\obs64.exe'
            )
        self.auto_find('Launch Anyway', click=True, type_='Button')
        self.get('https://sketch.pixiv.net/followings')
        self.driver.set_window_position(-1000, 0)
        self.driver.fullscreen_window()
        self.run()

    def run(self, start=1):

        while True:
            
            try:
                if re.match('.+lives/\d+$', self.current_url()):

                    if start: self.set_source(); start=0

                    self.auto_find(
                        'Start Recording', click=True
                        )

                    self.live_stream()

                self.auto_find(
                    'Stop.* Recording', click=True
                    )
                
            except exceptions.WebDriverException: break

            except Exception as error: print(f'{error}\n')

            Timer(5, function=None)

        self.obs.kill()
        self.close()

    def live_stream(self):

        while 'lives' in self.current_url():

            try:

                self.find(CHAT, click=True)
                self.find(PLAY, click=True, fetch=1)

                target = self.find(CONTROL).find_elements_by_class_name(
                    'StreamBodyCtrlButton'
                    )
                self.driver.execute_script(
                    'arguments[0].style.visibility="visible"',
                    self.find(CONTROL, fetch=1)
                    )

                target[0].click()
                target[-1].click()
                self.find(HIGH, click=True)
                self.find(ACCEPT, click=True)

            except exceptions.ElementClickInterceptedException: self.refresh()
                
            except: pass

            if self.find(FINISHED):

                self.driver.back()
                self.refresh()
               
    def set_source(self):

        title = f'[firefox.exe]: {self.driver.title} — Mozilla Firefox'

        self.auto_find('Livestreams', select=True, type_='ListItem')
        self.auto_find('Window Capture.+', select=True, type_='ListItem')
        self.auto_find('Window', select=title, type_='ComboBox')

    def auto_find(self, title, keys=None, click=0, select=None, type_='CheckBox', fetch=0):
        
        try:
            element = self.obs.top_window().child_window(
                title_re=title, control_type=type_
                )

            if keys: element.type_keys(keys)
            if click: element.click()
            if select:
                if isinstance(bool, select): element.select()
                else: element.select(select)
            
            return element

        except Exception as error:
            if fetch: raise error

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
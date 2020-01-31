import pywinauto, pyautogui, time
from pywinauto.application import Application

LOCATION = {
    'subtool': []
}

def open_file(app, file=None):
    
    pyautogui.click(119, 61, duration=0.10)
    pyautogui.click(296, 472)
    pyautogui.typewrite(file)
    pyautogui.typewrite(['enter'])

def click_subtool(): pass

def get_images():

    for x in range(0, 181, 30):
        for y in range(0, 181, 30):
            for z in range(0, 181, 30): pass

path = r"C:\Program Files\CELSYS\CLIP STUDIO 1.5\CLIP STUDIO\CLIPStudio.exe"

# if input('Is CLIPStudioPaint open?\n').lower() in 'yes':
# app = Application(backend="win32").connect(path=path)
# else: 
app = Application(backend="win32").start(path)
#     open_file(clipstudio, 'Pose Dataset.clip')
# time.sleep(1)

# clipstudio = app['CLIP STUDIO PAINT']

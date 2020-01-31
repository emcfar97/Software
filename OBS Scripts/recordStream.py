import pywinauto
from pywinauto.application import Application

def record(app): pass
def pause(app): pass

path = r'C:\Program Files\obs-studio\bin\64bit\obs64.exe'

# if input('Is CLIPStudioPaint open?\n').lower() in 'yes':
app = Application(backend="win32").connect(path=path)
# else: 
#     app = Application(backend="win32").start(path)

obs = app['Qt5QWindowIcon']
for h in obs.descendants():
    print(h.element_info._handle, h.element_info.rectangle)
    for i in h.descendants():
        print('\t', i.element_info._handle, i.element_info.rectangle)
    print()
# pass
# obs['Start Recording'].click()
# obs['Start Recording'].click()
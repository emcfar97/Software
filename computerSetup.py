import os, subprocess, threading
from os.path import join

ignore = [
    'Anaconda3-2019.03-Windows-x86_64.exe',
    'dban-2.3.0_i586.iso',
    'Driver Wiper.exe',
    'GPlates 2.1.0-win32.msi',
    'MediaCreationTool1903.exe',
    'opencodecs_0.85.17777.exe',
    'ReflectDLHF.exe ',
    'rufus.ini',
    'Wilbur.exe'
    ]

# for setup in setup_files:
#     print(setup)
#     setup = join(path, setup)
#     setup = subprocess.Popen([setup])
#     thread = threading.Thread(target=setup.wait)
#     thread.start()
#     thread.join()

input(__file__)
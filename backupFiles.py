import os, re
from datetime import date
from win32api import GetLogicalDriveStrings
from shutil import copy, copytree, ignore_patterns
from os.path import join, getmtime, exists, isfile, splitext

SPECIAL = [
    'Aesdh',
    'Aphorisms on Love',
    'Gnosis',
    'Hybrids',
    'Zanzonshobu', 
    'The Ice Cream Man',
    'Eavesdropper Diary', 
    'Manuke Shounen',
    'Monster Behaviorist', 
    'Monster Prankster',
    'Nevermore',
    'Novel Ideas'
    ]

def backup(drive, source=r'C:\Users\Emc11\Dropbox'):
    
    print(drive)

    for root, dirs, files in os.walk(drive):
        if 'System Volume Information' not in root:
            targets = [
                *[
                    join(root, dir) for dir in dirs
                    if re.search(r'\D - \d', dir)
                    ]
                +[
                    join(root, file) for file in files 
                    if re.search(r'\D - \d', file)
                    ]
                ]
            if not targets: continue
            targets = {
                re.sub(r'[A-Z]:',source,re.sub(r' - \d+','',target)):
                re.sub(r' - \d+', '', target) for target in targets
                }
            
            for key, val in targets.items():
                key = sanitize(key)
                if exists(key) and time_frame(key):
                    val = get_version(val)
                    if isfile(key): copy(key, val)
                    else: copytree(
                        key, val, ignore=ignore_patterns('*Reference')
                        )
                    print(f'\t{key}')     

def sanitize(path):

    if path.endswith('.doc'): path += 'x'
    
    for string in SPECIAL:
        if string in path:
            if path.endswith('.scriv'):
                path = path.replace('{}\\'.format(string), '')
            else: path = path.replace(f'{string}\\', '')
            break
    
    return path
    
def time_frame(path):
    modified = date.fromtimestamp(getmtime(path))
    difference = date.today() - modified

    return difference.days <= 15

def get_version(path, num=1):

    # name changes
    if 'Aesdh' in path: num = 35
    elif 'Gnosis' in path: num = 30
    elif 'Hybrids' in path: num = 32
    elif 'Manuke' in path: num = 14
    elif 'Cream' in path: num = 11
    elif 'Novel' in path: num = 7
    elif 'Manip' in path: num = 3

    comp = splitext(path)
    path = f'{comp[0]} - {num}{comp[1]}'

    while exists(path):
        num += 1
        path = f'{comp[0]} - {num}{comp[1]}'

    return path

drives = GetLogicalDriveStrings().split('\000')[:-1]
drives.remove('E:\\' if 'E:' in __file__ else 'C:\\')
for drive in drives: backup(drive)

print('Done')

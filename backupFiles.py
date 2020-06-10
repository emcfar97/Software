import os, re
from datetime import date
from shutil import copy, copytree
from win32api import GetLogicalDriveStrings
from os.path import join, getmtime, isfile, dirname, splitext

def last_modified(path):

    try: modified = date.fromtimestamp(getmtime(path))
    except: return
    difference = date.today() - modified

    return difference.days <= 15

def get_version(paths):

    latest = max(
        paths, key=lambda path: 
        int(re.search(' [0-9]+', path).group()[1:])
        )
    version = int(re.search(' [0-9]+', latest).group()[1:])

    return re.sub(' [0-9]+', f' {version + 1}', latest)

root = os.getcwd()[:3].upper()
source = rf'{root}Users\Emc11\Dropbox'
drives = GetLogicalDriveStrings().split('\000')[:-1]
drives.remove(root)

for drive in drives:
    
    print(drive)

    for root, dirs, files in os.walk(drive):

        targets = {}
        
        for path in dirs + files:
            
            dropbox = re.sub(
                r' - \d+', '', join(root.replace(drive[:-1], source), path)
                )
            if dropbox.endswith('scriv'):
                
                head, ext = splitext(dropbox)
                dropbox = dirname(head) + ext

            if re.search(r'\D - \d', path) and last_modified(dropbox):
                
                targets[dropbox] = targets.get(dropbox, []) + [join(root, path)]

        for key, val in targets.items():

            val = get_version(val)

            if isfile(key): copy(key, val)
            else: copytree(key, val)

            print(f'\t{val}') 

while True:
    input('\nDone')
    break
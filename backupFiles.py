import re
from os import walk
from pathlib import Path
from datetime import date
from shutil import copy, copytree
from win32con import DRIVE_REMOVABLE
from win32.win32file import GetDriveType
from win32.win32api import GetLogicalDriveStrings

SOURCE = Path.home() / 'Dropbox'

def get_drives(drive_types=(DRIVE_REMOVABLE,)):

    drives = GetLogicalDriveStrings().split("\x00")
    drives = [item for item in drives if item]
    
    return [
        item[:2] for item in drives 
        if drive_types is None or 
        GetDriveType(item) in drive_types
        ]

def last_modified(path):

    if path.exists():
        
        modified = date.fromtimestamp(path.stat().st_mtime)
        difference = date.today() - modified

        return difference.days <= 15

def get_version(paths):

    latest = str(sorted(paths)[-1])
    version = int(*re.findall(' - (\d+)', latest))

    return re.sub(' - \d+', f' - {version + 1:02}', latest)

for drive in get_drives():
    
    print(drive)

    for root, dirs, files in walk(drive):

        targets = {}
        root = Path(root)
        head = SOURCE / Path(*root.parts[1:])
        
        for path in root.iterdir():
            
            dropbox = head / re.sub(r' - \d+', '', path.name)
            if dropbox.suffix == '.scriv':
                
                dropbox = dropbox.parent.with_suffix(dropbox.suffix)

            if re.search(r' - \d', path.stem) and last_modified(dropbox):
                
                targets[dropbox] = targets.get(dropbox, []) + [path]

        for key, val in targets.items():
            
            val = get_version(val)

            if key.is_file(): copy(key, val)
            else: copytree(key, val)

            print(f'\t{val}') 

while True: input('\nDone'); break
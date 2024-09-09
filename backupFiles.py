import re
from os import path
from pathlib import Path
from datetime import date
from shutil import copy, copytree
from win32con import DRIVE_REMOVABLE
from win32.win32file import GetDriveType
from win32.win32api import GetLogicalDriveStrings

ROOT = Path(Path().cwd().drive)
SOURCE = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox')

def path_walk(top, topdown=False, followlinks=False):
    """
    See Python docs for os.walk, exact same behavior but it yields Path() instances instead
    """
    names = list(top.iterdir())

    dirs = (node for node in names if node.is_dir() is True)
    nondirs =(node for node in names if node.is_dir() is False)

    if topdown:
        yield top, dirs, nondirs

    for name in dirs:
        if followlinks or name.is_symlink() is False:
            for x in path_walk(name, topdown, followlinks):
                yield x

    if topdown is not True:
        yield top, dirs, nondirs

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

    latest = sorted(paths)[-1]
    version = int(*re.findall(' - (\d+)', latest.name))
    # modified = date.fromtimestamp(latest.stat().st_mtime)
    # difference = date.today() - modified

    stem = re.sub(' - \d+', f' - {version + 1:02}', latest.stem)

    return latest.with_stem(stem)

for drive in get_drives():
    
    drive = Path(drive)
    print(drive)

    for root, dirs, files in path_walk(drive):

        if 'Software' in root.parts: continue
        
        targets = {}
        head = SOURCE / Path(*root.parts[1:])
        
        # get all candidate files
        for path in root.glob('* - [0-9][0-9].*'):
            
            path = path.with_name(path.name.replace(' Backup', ''))
            dropbox = head / re.sub(r' - \d+', '', path.name)
      
            if dropbox.suffix == '.scriv':
                
                dropbox = dropbox.parent.with_suffix(dropbox.suffix)

            if last_modified(dropbox):
                
                targets[dropbox] = targets.get(dropbox, []) + [path]

        # save recently updated files
        for key, val in targets.items():
            
            val = get_version(val)
            
            print(f'\t{val}')         
            if key.is_file(): copy(key, val)
            else: copytree(key, val)
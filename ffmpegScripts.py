import ffmpeg
from os import path
from pathlib import Path
from ffprobe import FFProbe
from tempfile import gettempdir
from send2trash import send2trash
from re import search, sub, findall, IGNORECASE

EXT = '\.(mp4|flv|mkv|avi|wmv|mov|mpg|mpeg|divx|rm|ram|vob|3gp)'
ROOT = Path(Path().cwd().drive)
USER = ROOT / path.expandvars(r'\Users\$USERNAME')
DOWN = USER / r'Downloads\Images'
SOURCE = USER / r'Videos\Captures'
DEST = USER / r'Dropbox\Videos\Captures'
CRF = 15
PRESET = 'fast'
VSYNC = 2

def get_stream(files, text):
        
    new = DEST / files[0].with_suffix('.mp4').name

    if text and text in ('y', 'ye', 'yes'):

        stream = [
            ffmpeg.input(str(file)).drawtext(
                text=file.stem, fontsize=45, 
                x=int(FFProbe(file).streams[0].width) * .66, 
                y=int(FFProbe(file).streams[0].height) * .85,
                shadowcolor='white', shadowx=2, shadowy=2
                ) 
            for file in files
            ]
    else: stream = [ffmpeg.input(str(file)) for file in files]
    
    return new, stream

def get_folders():
    
    targets = input('Target folders: ')
    
    if '..' in targets:

        start, end = targets.split('..')
        
        return ''.join(
            str(i) for i in range(int(start), int(end) + 1)
            )
        
    return targets

def get_time(file, type):

    time = input(f'Enter {type} time (seconds or hh:mm:ss): ')
    
    if search('\d{2}:\d{2}:\d{2}.+', time): return time
    
    if time == '':
        
        if type == 'end' or time == -1:
            
            time = float(FFProbe(file).streams[0].duration)
        
        else:
        
            time == '0'

    min, sec = divmod(float(time), 60)
    hour, min = divmod(min, 60)

    return f'{hour:02.0f}:{min:02.0f}:{sec:06.3f}'

while True:
    
    user_input = input(
        'Choose from:\n1 - Convert videos\n2 - Concat videos\n3 - Change framerate\n4 - Split video\n5 - Download m3u8\n6 - Adjust directories\n7 - Check directories\n8 - Exit\n'
        )
    
    try:
        if   user_input == '1': # convert vidoes
                
            text = input('Overlay text? ').lower()

            files = [
                (
                    SOURCE / file, 
                    DEST / file.with_suffix('.mp4').name
                    )
                for file in SOURCE.iterdir() if search(EXT, file.suffix, IGNORECASE)
                ]
            
            for file, mp4 in files:

                try:
                
                    if text and text in 'yes':

                        metadata = FFProbe(str(file)).streams[0]

                        ffmpeg.input(str(file)).drawtext(
                            text=file.stem, fontsize=45, 
                            x=int(metadata.width) * .70, 
                            y=int(metadata.height) * .85,
                            shadowcolor='white', shadowx=2, shadowy=2
                            ).output(str(mp4), crf=CRF, preset=PRESET, vsync=VSYNC, vcodec='copy').run()

                    else:
                        ffmpeg.input(str(file)) \
                        .output(str(mp4), crf=CRF, preset=PRESET, vsync=VSYNC, vcodec='copy') \
                        .run()

                except Exception as error: print(error); continue

                send2trash(str(file))

        elif user_input == '2': # concat videos
            
            text = input('Overlay text? ').lower()

            folders = get_folders()
            
            for folder in SOURCE.glob(f'*Batch[{folders}]'):
                
                files = [
                    file for file in folder.iterdir()
                    if search(EXT, file.suffix, IGNORECASE)
                    ]
                new, stream = get_stream(files, text)
                
                try: ffmpeg.concat(*stream).output(str(new), crf=CRF, preset=PRESET, vsync=VSYNC).run()
                except Exception as error: print(error); continue
                
                for file in files: send2trash(str(file))

        elif user_input == '3': # change framerate
            
            text = input('Overlay text? ').lower()
            desired = (float(
                input('Enter desired length in minutes: ')
                ) * 60)

            for folder in SOURCE.glob(f'*Batch[{get_folders()}]'):

                try:
                    files = [
                        file for file in folder.iterdir()
                        if search(EXT, file.suffix, IGNORECASE)
                        ]
                    new, stream = get_stream(files, text)
                    temp = Path(gettempdir(), files[0].name)
                    
                    duration = sum(
                        float(FFProbe(file).streams[0].duration)
                        for file in files
                        )
                    
                    ffmpeg.concat(*stream) \
                        .filter('fps', fps=30, round='up') \
                        .setpts(f'{desired / duration:.4f}*PTS') \
                        .output(str(temp), crf=CRF, preset=PRESET, vsync=VSYNC, bitrate='100k') \
                        .run()
                    ffmpeg.input(str(temp)) \
                        .output(str(new), crf=CRF, preset=PRESET, vsync=VSYNC, vf='mpdecimate', bitrate='1k') \
                        .run()
                        
                except Exception as error: print(error); continue
                
                finally: temp.unlink()

                for file in files: send2trash(str(file))

        elif user_input == '4': # split video

            file = Path(input('Enter filepath: ').strip((' \'"')))
            
            latest = sorted(file.parent.glob(f'{file.stem} — Part [0-9][0-9]*'))
            
            if latest:
                
                num = int(*findall(' (\d+)', latest[-1].stem))
                stem = sub(f' {num}+', f' {num+1:02}', latest[-1].stem)

            else: stem = f'{file.stem} — Part 00'

            new = file.with_stem(stem)

            start = get_time(file, 'start')
            end = get_time(file, 'end')
                       
            ffmpeg.input(str(file), ss=(start), to=(end)) \
                .output(str(new), crf=CRF, preset=PRESET, acodec='copy',vcodec='copy') \
                .run()

        elif user_input == '5': # download m3u8
            
            url = input('Enter url: ')
            name = DOWN / f'{url.split("/")[3]}.mp4'
            ffmpeg.input(url).output(str(name), crf=CRF).run()

        elif user_input == '6': # adjust directories

            user_input = input(
                f'\nChoose from:\n1 - Change root: {ROOT}\n2 - Change source: {SOURCE}\n3 - Change destination: {DEST}\n4 - Change CRF: {CRF}\n5 - Change preset: {PRESET}\n6 - Change vsync: {VSYNC}\n'
                )

            if   user_input == '1': # change root

                path = Path(input('Enter path: '))

                if path.exists(): 
                    
                    ROOT = path if '\\' in path.drive else Path(f'{path}\\')
                    USER = Path(ROOT, *USER.parts[1:])
                    DOWN = Path(ROOT, *DOWN.parts[1:])
                    SOURCE = Path(ROOT, *SOURCE.parts[1:])
                    DEST = Path(ROOT, *DEST.parts[1:])

                    print('Success\n')

                else: raise FileNotFoundError
                        
            elif user_input == '2': # change source

                path = Path(input('Enter path: '))

                if path.exists(): 

                    SOURCE = path
                    print('Success\n')

                else: raise FileNotFoundError
                        
            elif user_input == '3': # change destination

                path = Path(input('Enter path: '))

                if path.exists(): 

                    DEST = path
                    print('Success\n')

                else: raise FileNotFoundError
            
            elif user_input == '4': # change CRF
                
                CRF = int(input('Enter value (integer): '))
            
            elif user_input == '5': # change preset
                
                PRESET = input('Enter value (veryfast, fast, slow, veryslow): ')
            
            elif user_input == '6': # change vsync
                
                VSYNC = int(input('Enter value (integer): '))

        elif user_input == '7': # check directories
            
            print(f'''
                Root: {ROOT}
                User: {USER}
                Down: {DOWN}
                Source: {SOURCE}
                Dest: {DEST}
                ''')

            for file in SOURCE.iterdir():

                if file.is_dir():
                    print(f'{file}: {[str(i) for i in file.iterdir()]}')
                elif search(EXT, file.suffix, IGNORECASE):
                    print(str(file))

            print() 
        
        elif user_input == '8': break
        
    except Exception as error: print(error, '\n')

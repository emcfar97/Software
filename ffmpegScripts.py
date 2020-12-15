import ffmpeg
from pathlib import Path
from ffprobe import FFProbe

EXT = '.mp4', '.flv', '.mkv'
DRIVE = Path(Path(__file__).drive)
SOURCE = DRIVE / r'\Users\Emc11\Videos\Captures'
DEST = DRIVE / r'\Users\Emc11\Dropbox\Videos\Captures'

def get_stream(files, text):
        
    new = DEST / files[0].with_suffix('.mp4').name

    if text:
        stream = [
            ffmpeg.input(str(file)).drawtext(
                text=file.stem, fontsize=45, 
                x=int(FFProbe(file).streams[0].width) * .70, 
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
        return ''.join(str(i) for i in range(int(start), int(end) + 1))
        
    return targets

while True:
    user_input = input(
        'Choose from:\n1 - Convert videos\n2 - Concat videos\n3 - Change framerate\n4 - Split video\n5 - Download m3u8\n6 - Check directories\n7 - Exit\n'
        )
    try:
        if   user_input == '1': # convert vidoes
                
            text = input('Overlay text? ').lower() in 'yes'

            files = [
                (
                    SOURCE / file, DEST / file.with_suffix('.mp4').name
                    )
                for file in SOURCE.iterdir() if file.suffix in EXT
                ]
            
            for file, mp4 in files:
                try: 
                    if text:
                        metadata = FFProbe(str(file)).streams[0]
                        ffmpeg.input(str(file)).drawtext(
                            text=file.stem, fontsize=45, 
                            x=int(metadata.width) * .70, 
                            y=int(metadata.height) * .85,
                            shadowcolor='white', shadowx=2, shadowy=2
                        ).output(str(mp4), crf=20, preset='fast').run()
                    else: 
                        ffmpeg.input(str(file)).output(str(mp4), crf=20, preset='fast').run()
                except Exception as error: print(error); continue
                file.unlink()

        elif user_input == '2': # concat videos
            
            text = input('Overlay text? ').lower() in 'yes'
            
            for folder in SOURCE.glob(f'*Batch[{get_folders()}]'):
                
                files = [
                    file for file in folder.iterdir()
                    if file.suffix in EXT
                    ]
                new, stream = get_stream(files, text)
                
                try: ffmpeg.concat(*stream).output(str(new), crf=20, preset='fast').run()
                except Exception as error: print(error); continue
                for file in files: file.unlink()

        elif user_input == '3': # change framerate
            
            text = input('Overlay text? ').lower() in 'yes'

            for folder in SOURCE.glob(f'*Batch[{get_folders()}]'):

                files = [
                    file for file in folder.iterdir()
                    if file.suffix in EXT
                    ]
                new, stream = get_stream(files, text)
                
                desired = float(input('Enter desired length (minutes): ')) * 60
                duration = sum(
                    float(FFProbe(file).streams[0].duration)
                    for file in files
                    )
                try:
                    ffmpeg.concat(*stream).setpts(
                        f'{desired / duration:.4f}*PTS') \
                        .output(str(new), crf=20, preset='fast'
                        ).run()
                except Exception as error: print(error); continue
                for file in files: file.unlink()

        elif user_input == '4': # split video

            file = Path(input('Enter filepath: ').strip())

            if file.exists():
                
                new = file.parent.parent / file.name
                start = input('Enter start time (seconds or hh:mm:ss): ')
                end = input('Enter end time (seconds or hh:mm:ss): ')
                
                if end == '':
                    
                    ffmpeg.input(str(file)).trim(
                        start=start).output(str(new), preset='fast').run()

                else:
                    
                    ffmpeg.input(str(file)).trim(
                        start=start, end=end
                        ).output(str(new), preset='fast').run()

            else: print(f'File {file} does not exist')

        elif user_input == '5': # download m3u8
            
            url = input('Enter url: ')
            name = f'{url.split("/")[3]}.mp4'
            ffmpeg.input(url).output(
                str(DRIVE / rf'\Users\Emc11\Downloads\Images\{name}')
                ).run()

        elif user_input == '6': # check directories
            
            print(DRIVE)
            for file in SOURCE.iterdir():
                if file.is_dir():
                    print(f'{file}: {[str(i) for i in file.iterdir()]}')
                elif file.suffix in EXT: print(str(file))
            print() 
        
        elif user_input == '7': break
            
    except Exception as error: print(error, '\n')

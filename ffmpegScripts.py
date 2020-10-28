import ffmpeg
from pathlib import Path
from ffprobe import FFProbe

EXT = '.mp4', '.flv', '.mkv'
SOURCE = Path().home() / r'Videos\Captures'
DEST = Path().home() / r'Dropbox\Videos\Captures'

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
        'Choose from:\n1 - Convert videos\n2 - Concat videos\n3 - Change framerate\n4 - Download m3u8\n5 - Check directories\n6 - Exit\n'
        )
    try:
        if   user_input == '1': # convert vidoes
                
            text = 1 if input('Overlay text? ').lower() in 'yes' else 0

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
            
            text = 1 if input('Overlay text? ').lower() in 'yes' else 0
            
            for folder in SOURCE.glob(f'*[{get_folders()}]'):
                
                files = [folder / file for file in folder.iterdir()]
                new, stream = get_stream(files, text)
                
                try: ffmpeg.concat(*stream).output(str(new), crf=20, preset='fast').run()
                except Exception as error: print(error); continue
                for file in files: file.unlink()

        elif user_input == '3': # change framerate
            
            text = 1 if input('Overlay text? ').lower() in 'yes' else 0

            for folder in SOURCE.glob(f'*[{get_folders()}]'):

                files = [folder / file for file in folder.iterdir()]
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
                
        elif user_input == '4': # download m3u8
            
            url = input('Enter url: ')
            name = f'{url.split("/")[3]}.mp4'
            ffmpeg.input(url).output(
                str(Path().home() / rf'Downloads\Images\{name}')
                ).run()

        elif user_input == '5': # check directories
        
            for file in SOURCE.iterdir():
                if file.is_dir():
                    print(f'{file}: {[str(i) for i in file.iterdir()]}')
                elif file.suffix in EXT: print(str(file))
            print() 
        
        elif user_input == '6': break
            
    except Exception as error: print(error, '\n')

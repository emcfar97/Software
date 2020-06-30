import ffmpeg
from ffprobe import FFProbe
from os.path import join, splitext, split, isfile
from os import remove, listdir, getcwd

def get_stream(files, text=0):

    if text:
        stream = [
            ffmpeg.input(file).drawtext(
                text=splitext(split(files[0])[-1])[0], fontsize=45, 
                x=int(FFProbe(file).streams[0].width) * .70, 
                y=int(FFProbe(file).streams[0].height) * .85,
                shadowcolor='white', shadowx=2, shadowy=2
                ) 
            for file in files
            ]
    else:
        stream = [ffmpeg.input(file) for file in files]
    new = join(dest, split(files[0])[-1]).replace(splitext(files[0])[-1], '.mp4')
    
    return new, stream

def get_folders():
    
    targets = input('Target folders: ')
    
    if '..' in targets:
        start, end = targets.split('..')
        return tuple(str(i) for i in range(int(start), int(end) + 1))
        
    return tuple(targets.split())

EXT = 'mp4', 'flv', 'mkv'
ROOT = getcwd()[:2].upper()
source = rf'{ROOT}\Users\Emc11\Videos\Captures'
dest = rf'{ROOT}\Users\Emc11\Dropbox\Videos\Captures'

while True:
    user_input = input(
        'Choose from:\n1 - Convert files\n2 - Concat files\n3 - Change framerate\n4 - Download m3u8\n5 - Check directories\n6 - Exit\n'
        )
    try:
        if  user_input ==  '1': # convert files
                
            text = 1 if input('Overlay text? ').lower() in 'yes' else 0

            files = [
                (
                    join(source, file),
                    join(dest, file.replace(splitext(file)[1], '.mp4'))
                    )
                for file in listdir(source) if file.endswith(EXT)
                ]
            print(files)
            
            for file, mp4 in files:
                try: 
                    if text:
                        metadata = FFProbe(file).streams[0]
                        ffmpeg.input(file).drawtext(
                            text=splitext(split(file)[-1])[0], fontsize=45, 
                            x=int(metadata.width) * .70, 
                            y=int(metadata.height) * .85,
                            shadowcolor='white', shadowx=2, shadowy=2
                        ).output(mp4, crf=20, preset='fast').run()
                    else: 
                        ffmpeg.input(file).output(mp4, crf=20, preset='fast').run()
                except Exception as error: print(error); continue
                remove(file)

        elif user_input == '2': # concat files
            
            text = 1 if input('Overlay text? ').lower() in 'yes' else 0
            targets = get_folders()
            
            for folder in listdir(source):
                
                if not folder.endswith((targets)): continue
                folder = join(source, folder)
                files = [join(folder, file) for file in listdir(folder)]
                new, stream = get_stream(files, text)
                
                try: ffmpeg.concat(*stream).output(new, crf=20, preset='fast').run()
                except Exception as error: print(error); continue
                for file in files: remove(file)

        elif user_input == '3': # change framerate
            
            text = 1 if input('Overlay text? ').lower() in 'yes' else 0
            targets = get_folders()

            for folder in listdir(source):

                if not folder.endswith((targets)): continue
                folder = join(source, folder)
                files = [join(folder, file) for file in listdir(folder)]
                new, stream = get_stream(files, text)
                
                desired = float(input('Enter desired length (minutes): ')) * 60
                duration = sum(
                    float(FFProbe(join(folder, file)).streams[0].duration)
                    for file in listdir(folder)
                    )
                try:
                    ffmpeg.concat(*stream).setpts(
                        f'{desired / duration:.4f}*PTS') \
                        .output(new, crf=20, preset='fast'
                        ).run()
                except Exception as error: print(error); continue
                for file in files: remove(file)
                
        elif user_input == '4': # download m3u8
            
            url = input('Enter url: ')
            name = f'{url.split("/")[3]}.mp4'
            ffmpeg.input(url).output(
                rf'{ROOT}\Users\Emc11\Downloads\Images\{name}'
                ).run()
            
        elif user_input == '5': # check directories
        
            for file in listdir(source):
                if file.startswith('Batch'):
                    print(f'{file}: {listdir(join(source, file))}')
                elif not file.endswith('.ini'): print(file)
            print() 
        
        elif user_input == '6': break
            
    except Exception as error: print(error, '\n')

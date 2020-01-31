import ffmpeg
# from ffprobe import FFProbe
from os import remove, listdir
from os.path import join, exists

source = r'C:\Users\Emc11\Videos\Captures'
dest = r'C:\Users\Emc11\Dropbox\Videos\Speedpaints'

if __file__.startswith(('e:\\', 'e:/')):
    source = source.replace('C:', 'E:')
    dest = dest.replace('C:', 'E:')

while True:
    user_input = input(
        'Choose from:\n1 - Convert files\n2 - Concat files\n3 - Change framerate\n4 - Download m3u8\n5 - Exit\n'
        )

    if  user_input ==  '1': # convert files

        files = [
            (join(source, file), join(dest, file.replace('.flv', '.mp4'))) 
            for file in listdir(source) if file.endswith('flv')
            ]
        for flv, mp4 in files:
            try: ffmpeg.input(flv).output(mp4, crf=20, preset='fast').run()
            except Exception as error: print(error); continue
            remove(flv)

    elif user_input == '2': # concat files
        
        targets = tuple(input('Target folders: ').split())
        
        for folder in listdir(source):
            
            if not folder.endswith((targets)): continue
            folder = join(source, folder)
            stream = [
                ffmpeg.input(join(folder, file)) 
                for file in listdir(folder)
                if file.endswith(('flv','mp4'))
                ]
            new = join(dest, listdir(folder)[0]).replace('flv', 'mp4')
            try: ffmpeg.concat(*stream).output(new, crf=20, preset='fast').run()
            except Exception as error: print(error); continue
            for file in stream: remove(file.node.kwargs['filename'])

    elif user_input == '3': # change framerate
        
        targets = tuple(input('Target folders: ').split())

        for folder in listdir(source):

            if not folder.endswith((targets)): continue
            folder = join(source, folder)
            files = [
                join(folder, file) for file in listdir(folder)
                if file.endswith(('flv','mp4'))
                ]
            desired = int(input('Enter desired length (minutes): '))
            
            for file in files:
                duration = float(FFProbe(file).streams[0].duration)
                frame_rate = duration / desired
                try:
                    ffmpeg.input(file).setpts(frame_rate
                        ).output(file, crf=20, preset='fast').run()
                except Exception as error: print(error)

    elif user_input == '4': # download m3u8
        
        url = input('Enter url: ')
        name = f'{url.split("/")[3]}.mp4'
        ffmpeg.input(url).output(
            rf'C:\Users\Emc11\Downloads\{name}').run()
        
    elif user_input == '5': break

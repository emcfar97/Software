import os, ffmpeg, tempfile, shutil
from os.path import join
from ffprobe import FFProbe

root = os.getcwd()[:2].upper()
path = rf'{root}\Users\Emc11\Dropbox\Videos\Captures\Streams\Illustrations'
temp_f = rf'{root}\Users\Emc11\Dropbox\Videos\Captures\Streams'
    
for file in os.listdir(path):

    temp = join(temp_f, file)
    file = join(path, file)
    ffmpeg.input(file).setpts('.5*PTS') \
        .output(temp, crf=20, preset='fast').run()
    shutil.move(temp, file)
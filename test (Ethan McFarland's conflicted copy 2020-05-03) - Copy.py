import os, ffmpeg, tempfile, shutil
from os.path import join, splitext, split
from ffprobe import FFProbe

path = r'C:\Users\Emc11\Videos\Captures\2020-0418-1857.mp4'
new = r'C:\Users\Emc11\Dropbox\Videos\Captures\2020-0418-1857.mp4'

metadata = FFProbe(path).streams[0]
height, width = int(metadata.height), int(metadata.width)
file = split(splitext(path)[0])[-1]
ffmpeg.input(path).drawtext(
    text=file, x=width*.75, y=height*.90, shadowx=(width*.75) + 10, shadowy=(height*.90) + 10, shadowcolor='gray', fontsize=42) \
    .output(new, crf=20, preset='fast').run()
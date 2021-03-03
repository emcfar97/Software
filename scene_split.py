import ffmpeg, argparse
from pathlib import Path
from ffprobe import FFProbe
from Webscraping import USER
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

SOURCE = USER / r'Downloads\Test'
DEST = USER / r'Downloads\Images\Clips'

def find_scenes(video_path, framerate):
    # Create our video & scene managers, then add the detector.

    video_manager = VideoManager([str(video_path)])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(THRESHOLD, MINIMUM))

    # Improve processing speed by downscaling before processing.
    video_manager.set_downscale_factor(DOWNSCALE)

    # Start the video manager and perform the scene detection.
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    # Each returned scene is a tuple of the (start, end) timecode.
    return scene_manager.get_scene_list(framerate)

def split_scenes(video):
    
    path = SOURCE / video.name
    name = DEST / video.name
    stream = FFProbe(str(path)).streams[0]
    start_time = convert_time(stream.start_time)
    duration = convert_time(stream.duration)
    scenes = find_scenes(path, stream.framerate)

    for num, (start, end) in enumerate(scenes):
        
        if num == 0: start = start_time
        elif isinstance(start, int): start = convert_time(start)
        else: start = start.get_timecode()

        if num == len(scenes) - 1: end = duration
        elif isinstance(end, int): end = convert_time(end)
        else: end = end.get_timecode()

        file = name.with_stem(f'{name.stem} - {num:02}')
        ffmpeg.input(str(path)).trim(
            start=start, end=end
            ).output(str(file), preset='fast').run()

def convert_time(time):

    min, sec = divmod(float(time), 60)
    hour, min = divmod(min, 60)

    return f'{hour:02.0f}:{min:02.0f}:{sec:06.3f}'

parser = argparse.ArgumentParser(
    prog='scene_split', description='Splits videos into multiple scenes'
    )
parser.add_argument(
    '-p', '--path', type=str,
    help='Path to video', default=SOURCE
    )
parser.add_argument(
    '-d', '--downscale', type=int,
    help='Downscale factor', default=2, 
    )
parser.add_argument(
    '-t', '--threshold', type=int,
    help='Threshold value', default=30, 
    )
parser.add_argument(
    '-m', '--minimum', type=int,
    help='Minimum scene length', default=15, 
    )
args = parser.parse_args()

VIDEO = Path(args.path.strip())
DOWNSCALE = args.downscale
THRESHOLD = args.threshold
MINIMUM = args.minimum

if VIDEO.is_file(): split_scenes(VIDEO)
else: [split_scenes(video) for video in VIDEO.glob('*mp4')]

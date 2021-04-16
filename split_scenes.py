import ffmpeg, argparse
from pathlib import Path
from ffprobe import FFProbe
from Webscraping import USER
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect import FrameTimecode
from scenedetect.detectors import ContentDetector

parser = argparse.ArgumentParser(
    prog='scene_splits', 
    description='Splits videos into multiple scenes'
    )
parser.add_argument(
    '-p', '--path', type=str,
    help='Path to video', default=''
    )
parser.add_argument(
    '-d', '--downscale', type=int,
    help='Downscale factor for source video', default=25, 
    )
parser.add_argument(
    '-t', '--threshold', type=int,
    help='Threshold value for scene change', default=50, 
    )
parser.add_argument(
    '-m', '--minimum', type=int,
    help='Minimum scene length', default=15, 
    )
parser.add_argument(
    '-b', '--debug', type=bool,
    help='Print timecodes', default=False, 
    )
parser.add_argument(
    '-s', '--source', type=str,
    help='File path to source folder',
    default=USER / r'Downloads\Test', 
    )
parser.add_argument(
    '-de', '--destination', type=str,
    help='File path to destination folder',
    default=USER / r'Downloads\Images\Clips', 
    )
args = parser.parse_args()

VIDEO = Path(args.path)
DOWNSCALE = args.downscale
THRESHOLD = args.threshold
MINIMUM = args.minimum
DEBUG = args.debug
SOURCE = args.source
DEST = args.destination

def split_scenes(video):
    
    if not video.exists():
        video = SOURCE / video.name
    if not DEBUG:
        folder = DEST / video.stem
        folder.mkdir(exist_ok=True)
        name = folder / video.name
    
    stream = FFProbe(str(video)).streams[0]
    start_time = get_time(stream.start_time)
    duration = get_time(stream.duration)

    scenes = find_scenes(video, stream.framerate)
    if get_time(scenes[0][0]) != start_time:
        scenes.insert(0, (start_time, scenes[0][0]))

    for num, (start, end) in enumerate(scenes, start=1):
        
        if num == 1: 
            start, end = start_time, get_time(end)

        elif num == len(scenes) + 1:
            start, end = get_time(start), duration

        else: 
            start, end = get_time(start), get_time(end)

        if start > end: start, end = end, start
        if start == end: continue
        
        if DEBUG: print(start, end); continue

        file = name.with_name(f'{name.stem} - {num:02}.mp4')
        trim(str(video), str(file), start, end)

def get_time(time):

    if isinstance(time, FrameTimecode):
        
        return time.get_timecode()

    min, sec = divmod(float(time), 60)
    hour, min = divmod(min, 60)

    return f'{hour:02.0f}:{min:02.0f}:{sec:06.3f}'

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

def trim(input_path, output_path, start, end):

    input_stream = ffmpeg.input(input_path)

    vid = (
        input_stream.video
        .trim(start=start, end=end)
        .setpts('PTS-STARTPTS')
        )
    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
        )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(
        joined[0], joined[1], output_path, preset='fast'
        )
    output.run()

if VIDEO.is_file(): split_scenes(VIDEO)
else: [split_scenes(video) for video in VIDEO.glob('*mp4')]
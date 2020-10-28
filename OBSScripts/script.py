import obspython as obs
from cv2 import matchTemplate, minMaxLoc, imread

template = imread('Target.jpg')
frame = obs.obs_

if minMaxLoc(
    matchTemplate(frame, template, 1)
    )[0] < .015: 
    
    obs.obs_frontend_recording_stop()
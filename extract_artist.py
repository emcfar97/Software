import cv2, imutils, argparse
import numpy as np

def get_frames(path, success=True, found=None):

    vidcap = cv2.VideoCapture(str(path))
    template = cv2.imread('stream_target.png', 0)
    (tH, tW) = template.shape[:2]
    
    while success:
        
        success, frame = vidcap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(gray, 50, 200)
        result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        
        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])
            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break
            
        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
        
        # draw a bounding box around the detected result and display the image
        cv2.rectangle(edged, (startX, startY), (endX, endY), (0, 0, 255), 2)
        edged = ResizeWithAspectRatio(edged, 1368, 768)
        cv2.imshow('frame', edged)
        cv2.waitKey(1)

def get_frame(path, success=True):

    vidcap = cv2.VideoCapture(str(path))

    while success:

        success, frame = vidcap.read()
        
        yield frame

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    '-t', '--template', required=True, 
    help='Path to template image',
    default='stream_target.png'
    )
ap.add_argument(
    '-p', '--path', required=True,
	help='Path to video where template will be matched'
    )
ap.add_argument(
    '-v', '--visualize',
	help='Flag indicating whether or not to visualize each iteration'
    )
args = vars(ap.parse_args())

# video = r'C:\Users\Emc11\Videos\2021-0215-1120.mp4'
# video = r'C:\Users\Emc11\Videos\2020-0414-1723.mp4'

# load the image image, convert it to grayscale, and detect edges
template = cv2.imread(args['template'], 0)
(tH, tW) = template.shape[:2]
cv2.imshow('Template', template)

# loop over the images to find the template in
for frame in get_frame(args['path']):
	# load the image, convert it to grayscale, and initialize the
	# bookkeeping variable to keep track of the matched region
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	found = None

	# loop over the scales of the image
	for scale in np.linspace(0.2, 1.0, 20)[::-1]:
		# resize the image according to the scale, and keep track
		# of the ratio of the resizing
		resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
		r = gray.shape[1] / float(resized.shape[1])

		# if the resized image is smaller than the template, then break
		# from the loop
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break

        # detect edges in the resized, grayscale image and apply template
		# matching to find the template in the image
		edged = cv2.Canny(resized, 50, 200)
		result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

		# check to see if the iteration should be visualized
		if args.get('visualize', False):
			# draw a bounding box around the detected region
			clone = np.dstack([edged, edged, edged])
			cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
				(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
			cv2.imshow('Visualize', clone)
			cv2.waitKey(0)

		# if we have found a new maximum correlation value, then update
		# the bookkeeping variable
		if found is None or maxVal > found[0]:
			found = (maxVal, maxLoc, r)

	# unpack the bookkeeping variable and compute the (x, y) coordinates
	# of the bounding box based on the resized ratio
	(_, maxLoc, r) = found
	(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
	(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

	# draw a bounding box around the detected result and display the image
	cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
	cv2.imshow('Image', frame)
	cv2.waitKey(0)
import numpy, cv2, imageio, random
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def predict(model, classes, images, verbose=False):
    
    shape = 1, *model.input_shape[1:]
    values = sum((
        model.predict(
            numpy.resize(image, shape)
            )[0]
        for image in images
        ))

    if verbose: return classes, values
    return classes[values.argmax()]

def load_video(path):
    
    frames = []
    
    vidcap = cv2.VideoCapture(str(path))
    success, frame = vidcap.read()

    while success:
        
        frames.append(frame)
        success, frame = vidcap.read()

    return frames

def show(prediction, images, frame=0, fps=50):

    if len(images) == 1:

        cv2.imshow(prediction, images[0])
        cv2.waitKey(0)
        return
    
    total = len(images)

    while True:
        cv2.imshow(prediction, images[frame])
        frame = (frame + 1) % total
        if cv2.waitKey(fps) & 0xFF == ord('q'):
            break

home = Path(__file__).parent
name = home / 'Medium-01'
model = keras.models.load_model(name)
classes = ['Illustration', 'Photograph']
path = Path(r'C:\Users\Emc11\Downloads\Images')

for image in random.choices(list(path.glob('*gif')), k=25):

    if image.suffix in ('.gif', '.mp4', '.webm'): image = load_video(image)
    else: image = [cv2.cvtColor(imageio.imread(image), cv2.COLOR_RGB2BGR)]
    
    prediction = predict(model, classes, image)
    
    show(prediction, image)
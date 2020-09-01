import numpy, imageio
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def predict(model, classes, image, verbose=False):
    
    shape = 1, *model.input_shape[1:]
    image = imageio.imread(image)
    image = numpy.resize(image, shape)    
    values = model.predict(image)[0]
    
    if verbose: return classes, values
    return classes[values.argmax()]

def make_model(input_shape, num_classes, chckpnt=False, load=False):
    
    if load: return keras.models.load_model(home / load)

    inputs = keras.Input(shape=input_shape)
    x = layers.experimental.preprocessing.Rescaling(1./255)(inputs)
    x = layers.Conv2D(32, 3, strides=2, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(64, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    previous_block_activation = x  # Set aside residual
    
    for size in [128, 256, 512, 728]:

        x = layers.Activation('relu')(x)
        x = layers.SeparableConv2D(size, 3, padding='same')(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation('relu')(x)
        x = layers.SeparableConv2D(size, 3, padding='same')(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPooling2D(3, strides=2, padding='same')(x)
        
        # Project residual
        residual = layers.Conv2D(
            size, 1, strides=2, padding='same')(previous_block_activation
            )
        x = layers.add([x, residual])  # Add back residual
        previous_block_activation = x  # Set aside next residual

    x = layers.SeparableConv2D(1024, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    
    x = layers.GlobalAveragePooling2D()(x)
    if num_classes == 2:
        activation = 'sigmoid'
        units = 1
    else:
        activation = 'softmax'
        units = num_classes
    
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(units, activation=activation)(x)
    model = keras.Model(inputs, outputs)

    if chckpnt: 
        path = home / 'Checkpoints'
        checkpoints = list(path.glob(f'{name}_*'))
        checkpoint = checkpoints[-1]
        model.load_weights(checkpoint)

    return model

classes = ['Illustration', 'Photograph']
home = Path.cwd()  / 'Machine Learning'
name = r'Medium-02'
image_size = (180, 180)
model = make_model(image_size + (3,), 2, load='Medium-01')
images = [
    r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\ce6de6a8c04b37aabea2b4d2195cd80d.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\10e02f19a038bb3812805eb2f996350b.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\433c0d5f795ef24432de471416eb35ba.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\42bc525d7a108092b13026eab161e723.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\e4d7c2b3a9f90ce815742c13d5529bd9.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\d7278f10c445ce7db4c40160168d09fc.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\ef868ce366cbd21f252f4af9dbf54fda.JPG", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\b22b0ad45a6e685ea107e97cc8fa8001.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\4a2fcce6db5c97c6ea507fc22c221bdc.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\e108727c47b37afa0b89c56cb3e24530.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\da19a8db821e83fecb581d2add99105d.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\6c74483b4fb7a8575207529d328f8e01.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\b1f54ea868019011488e4fca5dc456f7.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\ede9537b4ce16caeb6b8e7a33ce9ffbe.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\444411bcde071105eacb663707af143e.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\b2590fc5b2292cff0bc03b69a7a7c5a2.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\9ae4a9592323198fa546e2cd56dbfa80.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\83003bf692c4b772f726587134f19a74.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\af199e77f58471373fae17b8e2c44736.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\d2bc5438fb1f037f3421aae518a055a1.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\8db4027a191bd23d980d78adeb759910.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\bb2a66b55c2d2a60895f5e7004123265.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\9c23e0afee41bf3c83d846cc32f7742e.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\13d1f3ad9eddd4f955c2804276d695f3.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\03bed036e89ef9e31181edd3bb25ccd2.JPG",
    ]

for num, image in enumerate(images):

    type = 'Photograph' if 'ニ' in image else 'Illustration'
    prediction = predict(model, classes, image)
    print(f'{num:<3}: True: {type:<12} Model: {prediction}')

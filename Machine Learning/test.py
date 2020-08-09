import numpy, imageio
from tensorflow import keras
import os
from os.path import join

def predict(model, classes, image, verbose=False):
    
    shape = 1, *model.input_shape[1:]
    image = imageio.imread(image)
    image = numpy.resize(image, shape)    
    values = model.predict(image)[0]
    
    if verbose: return classes, values
    return classes[values.argmax()]

classes = ['Illustration', 'Photograph']
path = r'Machine Learning\Medium-01'
model = keras.models.load_model(path)
images = [
  r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\1dc03e690ac783335ae489eddc23d520.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\793fc1fbace7491ca23d44b7f3d6172b.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\ce40008ba01176edf395c4ee8d79902e.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\c1ae62e46f393308ddc39d207a53c5d8.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\d5af221fe91be7b2e7b361209defadbe.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\ca09e0743de63df1146dc26fc13c0b4d.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\1070a199718e00d137088a9227a2d79e.jpg", r"c:\users\emc11\dropbox\videos\ん\エラティカ ニ\69847f23421c8e8dce2de52caa964699.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\23f052fb56a77b6d035492d92150d927.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\2de4e0a4d6e1c9c37d4348e21890acda.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\22f93096a450622aae5393ff677854a0.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\5658482b11bb2207534287547f860b4e.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\182048e699c0b0e29ff7a5a95dbd7552.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\0f639efbb3cbb1157bf0822512aff703.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\e5ffbb61d829c5247c8a978c3ad8c46b.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\3d0016781c5c527786cea18d150b761c.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\db647fa8b6689c5e3cfe351d9d6e86c9.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\8f70908de6e4ba4f76e7519a0f30e5cc.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\a88ebf5b7ab8407294543e4c39c17da2.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\d6540cc80029e7c2a92a24d6e0bd9b69.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\5f397448da4c39c6d445342e46a33235.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\08f440f98cdd0f034a8cfea38cd669ed.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\b5f55bc911ba7f0506099c97dcd0676b.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ\f921e1fe3c3b245228505b0d00db43f9.jpg", r"C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三\dc66401bf60eb546657bf815db5074c2.jpg"
    ]

for num, image in enumerate(images):

    type = 'Photograph' if 'ニ' in image else 'Illustration'
    prediction = predict(model, classes, image)
    print(f'{num:<3}: True: {type:<12} Model: {prediction}')

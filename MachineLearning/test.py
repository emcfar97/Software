from hub import Dataset, schema, transform
from skimage.io import imread
from pathlib import Path

USER = Path('rayos')
dataset = './rayos/test'
custom = {
    'image': schema.Image(
        shape=(None, None), dtype='uint8', max_shape=(512, 512)
        ),
    'label': schema.ClassLabel(num_classes=2),
    }

@transform(schema=custom)
def load_transform(sample):

    image = imread(sample)
    label = int(sample.split('.')[-2])
    
    return {
        "image" : image,
        "label" : label
        }

fnames = [
    r"C:\Users\Emc11\Dropbox\ん\エラティカ ニ\f0b2dbfa779195e0769a1ebaf7d22488.jpg", 
    r"C:\Users\Emc11\Dropbox\ん\エラティカ 三\bfbf442331b996dcd3909080199df88d.jpg",
    r"C:\Users\Emc11\Dropbox\ん\エラティカ 三\90596a829d162455bd44759748b0e779.jpg", 
    r"C:\Users\Emc11\Dropbox\ん\エラティカ ニ\5956d21f8b3ffa492669001f6be4d20c.jpg", 
    r"C:\Users\Emc11\Dropbox\ん\エラティカ 三\8a360e1daa60742752da3a4ded7241fb.png", 
    r"C:\Users\Emc11\Dropbox\ん\エラティカ ニ\c5504009cd88251533ea265b4fcf2ede.jpg",
    ]

ds = Dataset(
    dataset, shape=(len(fnames),), mode='w+', schema=custom
    )
ds.flush()
dase = load_transform(fnames)
ds2 = dase.store(dataset)
data = Dataset(dataset)
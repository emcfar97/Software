'''File for collecting, organizing, and saving PyTorch datasets'''

from PIL import Image
from natsort import natsorted

from .. import DATA, HEIGHT, WIDTH, np
from . import *

from torch.utils.data import Dataset
from torchvision.datasets import ImageFolder

class Custom_Dataset(ImageFolder):

    def __init__(self, main_dir, transform):

        super(Custom_Dataset, self).__init__(main_dir, transform)
        self.main_dir = DATA / main_dir
        self.total_imgs = natsorted(
            self.main_dir.glob('*/*')
            )
        self.class_names = np.array([
            item.name for item in self.main_dir.glob('*') if item.is_dir()
            ])
        self.transform = transform

    def __len__(self): return len(self.total_imgs)

    def __getitem__(self, index):

        img_loc = str(self.total_imgs[index])
        image = Image.open(img_loc).convert('RGB')
        image.resize(HEIGHT, WIDTH)
        tensor_image = self.transform(image)

        return tensor_image

    # def __getitem__(self, index):
        
        # path = self.total_imgs[index]
        # image = Image.open((str(path))).convert('RGB')
        # image.resize(HEIGHT, WIDTH)
        # tensor_image = self.transform(image)

        # return tensor_image, path.parent.name
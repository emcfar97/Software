if __name__ == '__main__': from __init__ import *
else: from . import *
from torch.utils.data import Dataset

class Custom_Dataset(Dataset):

    def __init__(self, main_dir, transform):

        self.main_dir = main_dir
        self.transform = transform
        all_imgs = main_dir.glob('*/*')
        self.total_imgs = natsorted(all_imgs)

    def __len__(self):

        return len(self.total_imgs)

    def __getitem__(self, idx):

        img_loc = os.path.join(self.main_dir, self.total_imgs[idx])
        image = Image.open(img_loc).convert('RGB')
        tensor_image = self.transform(image)

        return tensor_image
if __name__ == '__main__': from __init__ import *
else: from . import *

# Transformation
transform = transforms.Compose([
transforms.Resize((256, 256)),
transforms.ToTensor(),
transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

train_data_tensor = Custom_Dataset(train_data_dir, transform=transform)
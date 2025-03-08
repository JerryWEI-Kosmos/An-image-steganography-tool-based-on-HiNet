# -*- coding: gbk -*-
import glob
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import config as c
from natsort import natsorted


def to_rgb(image):
    rgb_image = Image.new("RGB", image.size)
    rgb_image.paste(image)
    return rgb_image


class Hinet_Dataset(Dataset):
    def __init__(self, transforms_=None, mode="train"):

        self.transform = transforms_
        self.mode = mode
        if mode == 'train':
            # train
            self.files = natsorted(sorted(glob.glob(c.TRAIN_PATH + "/*." + c.format_train)))
        elif mode == 'data':
            # test
            self.files = sorted(glob.glob(c.VAL_PATH + "/*." + c.format_val))
        elif mode == 'cover':
            # cover
            self.files = sorted(glob.glob(c.IMAGE_PATH_cover + "/*." + c.format_val))
        elif mode == 'secret':
            # secret
            self.files = sorted(glob.glob(c.IMAGE_PATH_secret + "/*." + c.format_val))
        elif mode == 'steg':
            # steg
            self.files = sorted(glob.glob(c.IMAGE_PATH_steg + "/*." + c.format_val))
        

    def __getitem__(self, index):
        try:
            image = Image.open(self.files[index])
            image = to_rgb(image)
            item = self.transform(image)
            return item.unsqueeze(0)

        except:
            return self.__getitem__(index + 1)

    def __len__(self):
        if self.mode == 'shuffle':
            return max(len(self.files_cover), len(self.files_secret))

        else:
            return len(self.files)

transform = T.Compose([
    T.RandomHorizontalFlip(),
    T.RandomVerticalFlip(),
    T.RandomCrop(c.cropsize),
    T.ToTensor()
])

transform_val = T.Compose([
    T.CenterCrop(c.cropsize_val),
    T.ToTensor(),
])


# Training data loader
trainloader = DataLoader(
    Hinet_Dataset(transforms_=transform, mode="train"),
    batch_size=c.batch_size,
    shuffle=False,
    pin_memory=True,
    num_workers=8,
    drop_last=True
)
# Test data loader
dataloader = DataLoader(
    Hinet_Dataset(transforms_=transform_val, mode="data"),
    batch_size=c.batchsize_val,
    shuffle=False,
    pin_memory=True,
    num_workers=1,
    drop_last=True
)

# Cover data loader
coverloader = DataLoader(
    Hinet_Dataset(transforms_=transform_val, mode="cover"),
    batch_size=c.batchsize_val,
    shuffle=False,
    pin_memory=True,
    num_workers=1,
    drop_last=False
)

# Secret data loader
secretloader = DataLoader(
    Hinet_Dataset(transforms_=transform_val, mode="secret"),
    batch_size=c.batchsize_val,
    shuffle=False,
    pin_memory=True,
    num_workers=1,
    drop_last=False
)

# Steg data loader
stegloader = DataLoader(
    Hinet_Dataset(transforms_=transform_val, mode="steg"),
    batch_size=c.batchsize_val,
    shuffle=False,
    pin_memory=True,
    num_workers=1,
    drop_last=True
)
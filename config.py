# -*- coding: gbk -*-
# Super parameters
clamp = 2
channels_in = 3
log10_lr = -4.5
lr = 3.1622776601683795e-05
epochs = 1000
weight_decay = 1e-05
init_scale = 0.01

lamda_reconstruction = 5
lamda_guide = 1
lamda_low_frequency = 1
device_ids = [0]

# Train:
batch_size = 16
cropsize = 224
betas = (0.5, 0.999)
weight_step = 1000
gamma = 0.5
# Val:
cropsize_val = 1024
batchsize_val = 1
shuffle_val = False
val_freq = 50

# Dataset
TRAIN_PATH = 'Dataset/datas'
VAL_PATH = 'image/data'
COVER_PATH = 'Dataset/covers'
SECRET_PATH = 'Dataset/secrets'
STEG_PATH = 'Dataset/stegs'
format_train = 'png'
format_val = 'png'

# Display and logging:
loss_display_cutoff = 2.0
loss_names = ['L', 'lr']
silent = False
live_visualization = False
progress_bar = False

# Saving checkpoints:
MODEL_PATH = 'model/'
checkpoint_on_error = True
SAVE_freq = 50

IMAGE_PATH = 'image/'
IMAGE_PATH_cover = 'image/cover/'
IMAGE_PATH_secret = 'image/secret/'
IMAGE_PATH_steg = 'image/steg'
IMAGE_PATH_secret_rev = 'image/secret-rev/'

# Load:
suffix = 'model.pt'
tain_next = False
trained_epoch = 0

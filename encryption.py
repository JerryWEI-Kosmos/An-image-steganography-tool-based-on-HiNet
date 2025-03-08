# -*- coding: gbk -*-
import os
import re
import time
import math
import torch
import torch.nn
import datasets
import threading
import torch.optim
import torchvision
import numpy as np
import config as c
from model import *
import tkinter as tk
from itertools import cycle
from tkinter import  messagebox
import modules.Unet_common as common
from skimage.metrics import structural_similarity as ssim

def get_next_image_number(folder_path):
    files = os.listdir(folder_path)
    pattern = re.compile(r'\d+')
    max_num = 0
    for file in files:
        numbers = pattern.findall(file)
        if numbers:
            max_num = max(max_num, int(numbers[-1]))
    return max_num + 1

def load(name):
    state_dicts = torch.load(name)
    network_state_dict = {k:v for k,v in state_dicts['net'].items() if 'tmp_var' not in k}
    net.load_state_dict(network_state_dict)
    try:
        optim.load_state_dict(state_dicts['opt'])
    except:
        print('Cannot load optimizer for some reason or other')

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
net = Model()
net.cuda()
init_model(net)
net = torch.nn.DataParallel(net, device_ids=c.device_ids)
params_trainable = (list(filter(lambda p: p.requires_grad, net.parameters())))
optim = torch.optim.Adam(params_trainable, lr=c.lr, betas=c.betas, eps=1e-6, weight_decay=c.weight_decay)
weight_scheduler = torch.optim.lr_scheduler.StepLR(optim, c.weight_step, gamma=c.gamma)

load(c.MODEL_PATH + c.suffix)
net.eval()

dwt = common.DWT()
iwt = common.IWT()

def gauss_noise(shape):

    noise = torch.zeros(shape).cuda()
    for i in range(noise.shape[0]):
        noise[i] = torch.randn(noise[i].shape).cuda()

    return noise

def computePSNR(origin,pred):
    origin = np.array(origin)
    origin = origin.astype(np.float32)
    pred = np.array(pred)
    pred = pred.astype(np.float32)
    mse = np.mean((origin/1.0 - pred/1.0) ** 2 )
    if mse < 1.0e-10:
      return 100
    return 10 * math.log10(255.0**2/mse)

def forward_encryption(cover, secret, net, dwt, iwt):
    """
    加密函数，将秘密图像隐写进封面图像中。
    cover: 封面图像的tensor
    secret: 秘密图像的tensor
    net: 训练好的模型
    dwt: DWT函数实例
    iwt: IWT函数实例
    """
    with torch.no_grad():
        cover_input = dwt(cover)
        secret_input = dwt(secret)
        input_img = torch.cat((cover_input, secret_input), 1)

        # 执行前向传播
        output = net(input_img)
        output_steg = output.narrow(1, 0, 4 * c.channels_in)
        steg_img = iwt(output_steg)

        return steg_img

def backward_decryption(output_steg, net, dwt, iwt):
    """
    解密函数，从隐写图像中提取出秘密图像。
    output_steg: 隐写加密的输出，即隐写图像
    net: 训练好的模型
    dwt: DWT函数实例
    iwt: IWT函数实例
    gauss_noise: 生成高斯噪声的函数
    """
    with torch.no_grad():
        output_steg = dwt(output_steg)
        backward_z = gauss_noise(output_steg.shape)
        output_rev = torch.cat((output_steg, backward_z), 1)
        backward_img = net(output_rev, rev=True)
        secret_rev = backward_img.narrow(1, 4 * c.channels_in, backward_img.shape[1] - 4 * c.channels_in)
        secret_rev = iwt(secret_rev)

        return secret_rev

# cmd
def encryption_main(option):
    cover_loader = datasets.coverloader
    secret_loader = datasets.secretloader
    steg_loader = datasets.stegloader
    
    if option == '1':
        total_images = len(cover_loader.dataset) 
        processed_images = 0
        secret_loader_iter = cycle(secret_loader)
        with torch.no_grad():
            for cover_batch, secret_batch in zip(cover_loader, secret_loader_iter):
                cover_imgs = cover_batch  
                secret_imgs = secret_batch
                
                for i in range(cover_imgs.size(0)):
                    cover_img = cover_imgs[i].to(device)  # 确保图像是四维的
                    secret_img = secret_imgs[i].to(device)
                    
                    steg_img = forward_encryption(cover_img, secret_img, net, dwt, iwt)
                    next_num = get_next_image_number(c.IMAGE_PATH_steg)
                    
                    torchvision.utils.save_image(steg_img, f"{c.IMAGE_PATH_steg}{next_num:05d}.png")

                    processed_images += 1
                    print(f"Processed {processed_images} of {total_images} images.")

    elif option == '2':
        with torch.no_grad():
            total_images = len(steg_loader.dataset)
            processed_images = 0

            for steg_batch in steg_loader:
                steg_imgs = steg_batch
                
                for i in range(steg_imgs.size(0)):
                    steg_img = steg_imgs[i].to(device)
                    
                    secret_rev = backward_decryption(steg_img, net, dwt, iwt)
                    next_num = get_next_image_number(c.IMAGE_PATH_secret_rev)
                    torchvision.utils.save_image(secret_rev, f"{c.IMAGE_PATH_secret_rev}{next_num:05d}.png")

                    processed_images += 1
                    print(f"Processed {processed_images} of {total_images} images.")


# GUI
def update_progress_label(label, current, total):
    progress_percentage = (current / total) * 100
    label.config(text=f"Processing: {current}/{total} images ({progress_percentage:.2f}%)")
    label.update_idletasks()  # 强制更新GUI

def encryption_process(option, progress_label):
    net = Model().to(device)
    init_model(net)
    net = torch.nn.DataParallel(net, device_ids=c.device_ids)
    
    if option == '1':
        # 加密过程
        cover_loader = datasets.coverloader
        secret_loader = datasets.secretloader
        total_images = len(cover_loader.dataset) 
        processed_images = 0
        secret_loader_iter = cycle(secret_loader)
        
        with torch.no_grad():
            for cover_batch, secret_batch in zip(cover_loader, secret_loader_iter):
                cover_imgs = cover_batch 
                secret_imgs = secret_batch
                
                for i in range(cover_imgs.size(0)):
                    cover_img = cover_imgs[i].to(device)
                    secret_img = secret_imgs[i].to(device)
                    
                    steg_img = forward_encryption(cover_img, secret_img, net, dwt, iwt)
                    next_num = get_next_image_number(c.IMAGE_PATH_steg)
                    
                    torchvision.utils.save_image(steg_img, f"{c.IMAGE_PATH_steg}{next_num:05d}.png")

                    processed_images += 1
                    update_progress_label(progress_label, processed_images, total_images)

                
        messagebox.showinfo("Encryption Complete", "All images have been encrypted.")
    
    elif option == '2':
        # 解密过程
        steg_loader = datasets.stegloader
        total_images = len(steg_loader.dataset)
        processed_images = 0
        
        with torch.no_grad():
            for steg_batch in steg_loader:
                steg_imgs = steg_batch.to(device)
                
                for i in range(steg_imgs.size(0)):
                    steg_img = steg_imgs[i].unsqueeze(0)
                    
                    secret_rev = backward_decryption(steg_img, net, common.DWT(), common.IWT())
                    next_num = get_next_image_number(c.IMAGE_PATH_secret_rev)
                    torchvision.utils.save_image(secret_rev, f"{c.IMAGE_PATH_secret_rev}/{next_num:05d}.png")

                    processed_images += 1
                    # 更新进度提示
                    update_progress_label(progress_label, processed_images, total_images)
                
        messagebox.showinfo("Decryption Complete", "All images have been decrypted.")

def encryption_gui():
    encryption_window = tk.Toplevel()
    encryption_window.title("Encryption Operations")
    encryption_window.geometry("640x360")
    encryption_window.configure(background='#81BECE')

    progress_label = tk.Label(encryption_window, text="Processing: 0/0 images (0%)")
    progress_label.pack(pady=5)

    tk.Button(encryption_window, text="Encrypt Images", command=lambda: threading.Thread(target=encryption_process, args=('1', progress_label)).start()).pack(pady=10)
    tk.Button(encryption_window, text="Decrypt Images", command=lambda: threading.Thread(target=encryption_process, args=('2', progress_label)).start()).pack(pady=10)

# Web
def encryption_json(option):
    if option == 'encrypt':
        loader = datasets.coverloader
        other_loader = datasets.secretloader
    elif option == 'decrypt':
        loader = datasets.stegloader
    else:
        return {'error': 'Invalid option'}, 400

    total_images = len(loader.dataset)
    processed_images = 0
    result_paths = []

    with torch.no_grad():
        if option == 'encrypt':
            secret_loader_iter = cycle(other_loader)
            for cover_batch, secret_batch in zip(loader, secret_loader_iter):
                cover_imgs, secret_imgs = cover_batch[0].to(device), secret_batch[0].to(device)
                for i in range(cover_imgs.size(0)):
                    cover_img, secret_img = cover_imgs[i].unsqueeze(0), secret_imgs[i].unsqueeze(0)
                    steg_img = forward_encryption(cover_img, secret_img, net, dwt, iwt)
                    next_num = get_next_image_number(c.IMAGE_PATH_steg)
                    save_path = os.path.join(c.IMAGE_PATH_steg, f"{next_num:05d}.png")
                    torchvision.utils.save_image(steg_img, save_path)
                    result_paths.append(save_path)
        elif option == 'decrypt':
            for steg_batch in loader:
                steg_imgs = steg_batch[0].to(device)
                for i in range(steg_imgs.size(0)):
                    steg_img = steg_imgs[i].unsqueeze(0)
                    secret_rev = backward_decryption(steg_img, net, dwt, iwt)
                    next_num = get_next_image_number(c.IMAGE_PATH_secret_rev)
                    save_path = os.path.join(c.IMAGE_PATH_secret_rev, f"{next_num:05d}.png")
                    torchvision.utils.save_image(secret_rev, save_path)
                    result_paths.append(save_path)

        processed_images += len(result_paths)

    return {'message': f'Processed {processed_images} of {total_images} images.', 'result_paths': result_paths}

def run_test():
    cover_loader = datasets.coverloader
    secret_loader = datasets.secretloader

    total_encryption_time = 0
    total_decryption_time = 0
    psnr_cover_steg_values = []
    psnr_secret_recovered_values = []
    ssim_cover_steg_values = []
    ssim_secret_recovered_values = []
    processed_images = 0

    secret_loader_iter = cycle(secret_loader)

    for cover_batch, secret_batch in zip(cover_loader, secret_loader_iter):
        cover_imgs = cover_batch[0].to(device) 
        secret_imgs = secret_batch[0].to(device)

        for i in range(cover_imgs.size(0)):
            cover_img = cover_imgs[i].unsqueeze(0)
            secret_img = secret_imgs[i].unsqueeze(0)

            # 加密
            start_encryption_time = time.time()
            steg_img = forward_encryption(cover_img, secret_img, net, dwt, iwt)
            end_encryption_time = time.time()

            # 解密
            start_decryption_time = time.time()
            recovered_secret_img = backward_decryption(steg_img, net, dwt, iwt)
            end_decryption_time = time.time()

            # PSNR 计算
            psnr_cover_steg = computePSNR(cover_img.cpu().numpy(), steg_img.cpu().numpy())
            psnr_secret_recovered = computePSNR(secret_img.cpu().numpy(), recovered_secret_img.cpu().numpy())
            psnr_cover_steg_values.append(psnr_cover_steg)
            psnr_secret_recovered_values.append(psnr_secret_recovered)

            cover_img_np = cover_img.squeeze(0).cpu().permute(1, 2, 0).numpy()
            steg_img_np = steg_img.squeeze(0).cpu().permute(1, 2, 0).numpy()
            secret_img_np = secret_img.squeeze(0).cpu().permute(1, 2, 0).numpy()
            recovered_secret_img_np = recovered_secret_img.squeeze(0).cpu().permute(1, 2, 0).numpy()

            # 计算SSIM
            ssim_cover_steg = ssim(cover_img_np, steg_img_np, data_range=steg_img_np.max() - steg_img_np.min(), multichannel=True, channel_axis=2)
            ssim_secret_recovered = ssim(secret_img_np, recovered_secret_img_np, data_range=recovered_secret_img_np.max() - recovered_secret_img_np.min(), multichannel=True, channel_axis=2)
            ssim_cover_steg_values.append(ssim_cover_steg)
            ssim_secret_recovered_values.append(ssim_secret_recovered)

            # 时间计算
            total_encryption_time += (end_encryption_time - start_encryption_time)
            total_decryption_time += (end_decryption_time - start_decryption_time)

            processed_images += 1

    # 平均值
    avg_psnr_cover_steg = np.mean(psnr_cover_steg_values)
    avg_psnr_secret_recovered = np.mean(psnr_secret_recovered_values)
    avg_ssim_cover_steg = np.mean(ssim_cover_steg_values)
    avg_ssim_secret_recovered = np.mean(ssim_secret_recovered_values)

    print(f"Processed {processed_images} images.")
    print(f"Average PSNR between original covers and steg images: {avg_psnr_cover_steg:.2f} dB")
    print(f"Average PSNR between original secrets and recovered secrets: {avg_psnr_secret_recovered:.2f} dB")
    print(f"Average SSIM between original covers and steg images: {avg_ssim_cover_steg:.3f}")
    print(f"Average SSIM between original secrets and recovered secrets: {avg_ssim_secret_recovered:.3f}")
    print(f"Total encryption time: {total_encryption_time:.3f} seconds")
    print(f"Total decryption time: {total_decryption_time:.3f} seconds")
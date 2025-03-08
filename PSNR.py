# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np

def calculate_psnr(image_path_1, image_path_2):
    # 加载两张图像
    img1 = Image.open(image_path_1)
    img2 = Image.open(image_path_2)
    
    # 将图像转换为numpy数组
    img1_array = np.array(img1, dtype=np.float64)
    img2_array = np.array(img2, dtype=np.float64)
    
    # 确保两张图像尺寸相同
    if img1_array.shape != img2_array.shape:
        raise ValueError("Tow images is diffente!")
    
    # 计算均方误差(MSE)
    mse = np.mean((img1_array - img2_array) ** 2)
    
    if mse == 0:
        return "The same"
    
    # 计算PSNR值
    PIXEL_MAX = 255.0
    psnr = 20 * np.log10(PIXEL_MAX / np.sqrt(mse))
    
    return psnr

# 使用示例
image_path_1 = r'D:\Study\GraduationProjection\ProjectFiles\HiNet-main\Dataset\covers\0138_512x512.png'
image_path_2 = r'D:\Study\GraduationProjection\ProjectFiles\HiNet-main\Dataset\stegs\stego_20240325153728.png'

psnr_value = calculate_psnr(image_path_1, image_path_2)
print(f"PSNR value: {psnr_value}dB")

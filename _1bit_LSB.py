# -*- coding: utf-8 -*-
import math
from PIL import Image
import numpy as np

def embed_lsb(cover_image_path, data_to_hide):
    img = Image.open(cover_image_path)
    img_array = np.array(img)
    
    binary_data = ''.join(format(byte, '08b') for byte in data_to_hide)
    
    data_index = 0
    for i in range(img_array.shape[0]):
        if data_index >= len(binary_data):
            break
        for j in range(img_array.shape[1]):
            if data_index >= len(binary_data):
                break
            for k in range(3):  # ��RGBÿ��ͨ�����в���
                if data_index < len(binary_data):
                    pixel = img_array[i, j, k]
                    img_array[i, j, k] = (pixel & 0xFE) | int(binary_data[data_index])
                    data_index += 1
                else:
                    break
    
    # ���������غ���ͼ�����
    stego_img = Image.fromarray(img_array)
    return stego_img



def extract_lsb(stego_image_path):
    img = Image.open(stego_image_path)
    img_array = np.array(img)
    
    binary_data = ""
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):  # ����RGBͨ��
                pixel = img_array[i, j, k]
                binary_data += str(pixel & 1)
    
    # ��ֵͼ��ĳߴ�
    img_size = int(math.sqrt(len(binary_data)))
    binary_image = [int(bit) for bit in binary_data]
    
    # ������ֵͼ��
    extracted_img = Image.new('1', (img_size, img_size))
    extracted_img.putdata(binary_image[:img_size*img_size])
    return extracted_img

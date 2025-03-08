# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet
from PIL import Image
import numpy as np
import math
import os
import base64
import random
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from datetime import datetime
import _1bit_LSB as LSB


TEXT_FOLDER = 'imagetexts'
IMAGE_FOLDER = 'image/secret'
KEY_FOLDER = 'image/keys'
STEG_FOLDER = 'image/textencode'
START_MARKER = b"---START_OF_ENCRYPTED_TEXT---"
END_MARKER = b"---END_OF_ENCRYPTED_TEXT---"
MAX_LENGTH = 1024 * 1024 


def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


def generate_or_load_encrypted_key():
    if not os.path.exists(KEY_FOLDER):
        os.makedirs(KEY_FOLDER)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    key_file_path = os.path.join(KEY_FOLDER, f'{timestamp}_key')
    key = Fernet.generate_key()
    with open(key_file_path, 'wb') as key_out:
        key_out.write(key)
    print(f"Generated and saved a new key with timestamp {timestamp}.")
    return key, timestamp


def read_text_input():
    while True:  
        mode = input("Please select text reading method:\n1. Keyboard\n2. File\n")
        if mode == '1':
            text = input("Please input text: ")
        elif mode == '2':
            file_path = input("Please input file path: ")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            except FileNotFoundError:
                print("File not found. Please try again.")
                continue
        else:
            print("Input error. Please try again.")
            continue

        total_length = len(START_MARKER) + len(text.encode('utf-8')) + len(END_MARKER)
        total_length_bits = total_length * 8

        if total_length_bits > MAX_LENGTH:
            print(f"Text length with markers exceeds the maximum allowed length of {MAX_LENGTH // 8} bytes. Please input a shorter text or choose a different file.")
        else:
            return text


def encrypt_text_and_add_markers(text, key):
    f = Fernet(key)
    encrypted_text = f.encrypt(text.encode('utf-8'))
    encrypted_text_with_markers = START_MARKER + encrypted_text + END_MARKER
    return encrypted_text_with_markers


def save_as_binary_image(encrypted_text_with_markers, timestamp):
    binary_data = ''.join(format(byte, '08b') for byte in encrypted_text_with_markers)
    num_pixels = len(binary_data)
    img_size = int(math.ceil(math.sqrt(num_pixels)))
    if img_size > 1024:
        img_size = 1024
    padded_length = img_size ** 2
    padded_binary_data = binary_data.ljust(padded_length, '0')
    
    image = Image.new('1', (img_size, img_size))
    pixels = [int(padded_binary_data[i]) for i in range(padded_length)]
    image.putdata(pixels)
    
    IMAGE_FOLDER = 'image/textencode/binary'
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
    secret_image_path = os.path.join(IMAGE_FOLDER, f"secret_{timestamp}.png")
    image.save(secret_image_path)
    
    covers_folder = 'image/cover'
    cover_image_path = os.path.join(covers_folder, random.choice(os.listdir(covers_folder)))

    stego_img = LSB.embed_lsb(cover_image_path, encrypted_text_with_markers)

    stego_image_path = os.path.join('image/textencode', f'stego_{timestamp}.png')
    stego_img.save(stego_image_path)
    print(f"Data has been embedded and saved to {stego_image_path}.")


def image_to_text_and_extract_content(stego_image_path):
    img = LSB.extract_lsb(stego_image_path)
    pixels = list(img.getdata())
    binary_data = [0 if pixel == 0 else 1 for pixel in pixels]
    
    byte_array = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = 0
        for bit in binary_data[i:i+8]:
            byte = (byte << 1) | bit
        byte_array.append(byte)
    encrypted_text_with_markers = bytes(byte_array)
    print("start to find START_MARKER and END_MARKER...")
    start_index = encrypted_text_with_markers.find(START_MARKER)
    end_index = encrypted_text_with_markers.find(END_MARKER, start_index + len(START_MARKER))
    print("Over")

    if start_index != -1 and end_index != -1 and start_index < end_index:
        print("Finding encryption...")
        encrypted_text = encrypted_text_with_markers[start_index + len(START_MARKER):end_index]
        print("Over")
        return encrypted_text
    else:
        print("No find")
        encrypted_text = b""
        return encrypted_text


def select_encrypted_key():
    files = [f for f in os.listdir(KEY_FOLDER) if os.path.isfile(os.path.join(KEY_FOLDER, f))]
    print("Available keys:")
    for i, file in enumerate(files):
        print(f"{i+1}. {file}")
    choice = int(input("Select the key file by number: "))
    key_file_path = os.path.join(KEY_FOLDER, files[choice-1])
    with open(key_file_path, 'rb') as key_file:
        key = key_file.read()
    return key


def decrypt_text(encrypted_text, key):
    f = Fernet(key)
    try:
        decrypted_text = f.decrypt(encrypted_text).decode('utf-8')
        return decrypted_text
    except Exception as e:
        print("Error during decryption:", e)
        return None

# cmd
def text_coding_main():
    choice = input("Please select option:\n1. Text to binary image \n2. binary image to text\n")
    if choice == '1':
        text = read_text_input()
        if text:
            key, timestamp = generate_or_load_encrypted_key()
            encrypted_text_with_marker = encrypt_text_and_add_markers(text, key)
            save_as_binary_image(encrypted_text_with_marker, timestamp)
    elif choice == '2':
        image_path = input("Please input the path to the binary image: ")
        encrypted_text_with_marker = image_to_text_and_extract_content(image_path)
        if encrypted_text_with_marker:
            print("Encryption is enpty!")
        key = select_encrypted_key()
        decrypted_text = decrypt_text(encrypted_text_with_marker, key)
        print("Decrypted text:", decrypted_text)

        save_option = input("Do you want to save the decrypted text to a file? (yes/no): ").lower()
        if save_option == 'yes':
            if not os.path.exists(TEXT_FOLDER):
                os.makedirs(TEXT_FOLDER)
            save_path = os.path.join(TEXT_FOLDER, f"decrypted_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(decrypted_text)
            print(f"Decrypted text has been saved to {save_path}.")
        else:
            print("Decrypted text was not saved.")
    else:
        print("Input error, please choose again.")

# gui
def read_text_from_file():
    file_path = filedialog.askopenfilename(title="Select text file", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return None

def gui_text_to_grayscale():
    root = tk.Tk()
    root.withdraw()  

    choice = messagebox.askquestion("Text Input", "Do you want to load text from a file?")
    if choice == 'yes':
        text = read_text_from_file()
    else:
        text = simpledialog.askstring("Input Text", "Enter the text to convert to binary image:", parent=root)

    if text:
        key, timestamp = generate_or_load_encrypted_key()
        encrypted_text_with_marker = encrypt_text_and_add_markers(text, key)
        save_as_binary_image(encrypted_text_with_marker, timestamp)
        messagebox.showinfo("Success", "Text has been successfully converted to a binary image.", parent=root)

def gui_select_encrypted_key():
    key_path = filedialog.askopenfilename(title="Select the encryption key")
    if key_path:
        with open(key_path, "rb") as key_file:
            return key_file.read()
    return None

def gui_grayscale_to_text():
    root = tk.Tk()
    root.withdraw()  

    image_path = filedialog.askopenfilename(title="Select the binary image", filetypes=[("Image files", "*.png")], parent=root)
    if image_path:
        encrypted_text_with_marker = image_to_text_and_extract_content(image_path)
        key = gui_select_encrypted_key()
        if key:
            decrypted_text = decrypt_text(encrypted_text_with_marker, key)
            
            save_option = messagebox.askyesno("Save Decrypted Text", "Do you want to save the decrypted text to a file?", parent=root)
            if save_option:
                if not os.path.exists(TEXT_FOLDER):
                    os.makedirs(TEXT_FOLDER)
                save_path = os.path.join(TEXT_FOLDER, f"decrypted_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(decrypted_text)
                messagebox.showinfo("Success", f"Decrypted text has been saved to {save_path}.", parent=root)
            else:
                messagebox.showinfo("Decrypted Text", decrypted_text, parent=root)
        else:
            messagebox.showerror("Error", "No key selected for decryption.", parent=root)

def text_coding_main_gui():
    window = tk.Toplevel()
    window.title("Text Encoding Operations")
    window.geometry("640x360")
    window.configure(background='#81BECE')

    tk.Button(window, text="Text to Image", command=gui_text_to_grayscale).pack(pady=10)
    tk.Button(window, text="Image to Text", command=gui_grayscale_to_text).pack(pady=10)

def encode_text_json(data):
    text_input = data.get('text_input')
    file_path = data.get('file_path')

    if text_input:
        content = text_input
    elif file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            return {'error': f'Failed to read file: {str(e)}'}
    else:
        return {'error': 'No text input or file path provided'}

    key, timestamp = generate_or_load_encrypted_key()
    encrypted_text_with_marker = encrypt_text_and_add_markers(content, key)
    save_as_binary_image(encrypted_text_with_marker, timestamp)
    return {'message': f"Text has been successfully converted to a binary image.", 'timestamp': timestamp}

def decode_image_json(data):
    image_path = data.get('image_path')
    key_path = data.get('key_path') 

    if not image_path:
        return {'error': 'Image path is required'}

    try:
        encrypted_text_with_marker = image_to_text_and_extract_content(image_path)
    except Exception as e:
        return {'error': f'Failed to extract text from image: {str(e)}'}

    try:
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
        decrypted_text = decrypt_text(encrypted_text_with_marker, key)
    except Exception as e:
        return {'error': 'Decryption failed', 'detail': str(e)}

    return {'message': "Decryption successful", 'decrypted_text': decrypted_text}
# -*- coding: gbk -*-
import tkinter as tk
from tkinter import ttk 

# 引入模块
import folder_operations as fp
import text_encoding as tcoding
import config_setting as cs
import encryption as enc


def on_encryption():
    enc.encryption_gui()

def on_modify_config():
    cs.gui_modify_config()

def on_manage_folders():
    fp.manage_folder_images_gui()

def on_text_encoding():
    tcoding.text_coding_main_gui()

def create_main_window():
    window = tk.Tk()
    window.title("Steganography Toolkit")

    window_width = 746
    window_height = 420
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    ttk.Style().configure('TButton', padding=6, relief='RAISED', background='#E8EDE7', activeforeground='#036280')

    ttk.Button(window, text="Steganography or Extraction", command=on_encryption).pack(pady=10, fill='x', padx=50)
    ttk.Button(window, text="Manage Images in Folders", command=on_manage_folders).pack(pady=10, fill='x', padx=50)
    ttk.Button(window, text="Encode or Decode Text", command=on_text_encoding).pack(pady=10, fill='x', padx=50)
    ttk.Button(window, text="Modify Configuration Parameters", command=on_modify_config).pack(pady=10, fill='x', padx=50)
    ttk.Button(window, text="Exit", command=window.quit).pack(pady=10, fill='x', padx=50)
    
    # 设置窗口的背景颜色
    window.configure(background='#81BECE')
    # 进入消息循环
    window.mainloop()

if __name__ == "__main__":
    create_main_window()
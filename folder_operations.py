# -*- coding: gbk -*-
import os
import shutil
from pathlib import Path
from PIL import Image
import config as c
import tkinter as tk
from flask import request, jsonify
from tkinter import ttk, filedialog, simpledialog, messagebox
from werkzeug.utils import secure_filename


def custom_config():
    for key, value in c.config.items():
        print(f"{key}: {value}")

def convert_to_png(source_path, target_path):
    """
    Converts an image to PNG format and saves it to the target path.
    The target path should include the filename with a .png extension.
    """
    image = Image.open(source_path)
    image = image.convert("RGB")  # Convert to RGB in case it's a palette-based image like GIF
    image.save(target_path, "PNG")

def select_and_copy_images_manually():
    folder1_path = 'image/covers/'
    folder2_path = 'image/secrets/'
    output_folder_path = 'image/data/'
    # 获取文件夹中的所有图片文件
    folder1_images = [file for file in os.listdir(folder1_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    folder2_images = [file for file in os.listdir(folder2_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # 确保文件夹存在
    Path(output_folder_path).mkdir(parents=True, exist_ok=True)

    # 显示可选择的图片列表
    print("Secrets Images:")
    for i, image in enumerate(folder1_images, 1):
        print(f"{i}. {image}")

    selected_images1_indices = list(map(int, input("\nEnter the indices of the images from Secrets Folder to copy (comma-separated): ").split(',')))

    print("\nCovers Images:")
    for i, image in enumerate(folder2_images, 1):
        print(f"{i}. {image}")

    selected_images2_indices = list(map(int, input("\nEnter the indices of the images from Covers Folder to copy (comma-separated): ").split(',')))

    # 交替复制选择的图片到输出文件夹并转换成PNG格式
    for i, index1 in enumerate(selected_images1_indices):
        selected_image1 = folder1_images[index1 - 1]
        selected_image2 = folder2_images[selected_images2_indices[i] - 1]

        # 交替复制到输出文件夹并转换为PNG
        selected_image1_png = os.path.splitext(selected_image1)[0] + '.png'
        selected_image2_png = os.path.splitext(selected_image2)[0] + '.png'

        convert_to_png(os.path.join(folder1_path, selected_image1), os.path.join(output_folder_path, f'selected_{i + 1}_{selected_image1_png}'))
        convert_to_png(os.path.join(folder2_path, selected_image2), os.path.join(output_folder_path, f'selected_{i + 1}_{selected_image2_png}'))

    print(f"Alternate images selected, converted to PNG, and copied successfully to datas")

# cmd
def manage_folder_images():
   while True:  # 开始无限循环
        # 定义文件夹路径选项
        folders = {
            '1': 'image/cover/',
            '2': 'image/secrets/',
            '3': 'image/data/',
            '4': 'image/steg/'
        }

        # 选择文件夹
        print("\nSelect a folder:")
        for key, value in folders.items():
            print(f"{key}: {value}")
        folder_choice = input("Enter your choice (1/2/3/4): ")

        folder_path = folders.get(folder_choice)
        if not folder_path:
            print("Invalid choice. Exiting...")
            return

        # 确保文件夹存在
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        # 显示当前文件夹中的图片
        images = [file for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        print("\nImages in selected folder:")
        for i, image in enumerate(images, 1):
            print(f"{i}. {image}")

        # 选择添加或删除文件
        action = input("\nDo you want to add or delete an image? (add/delete): ").lower()
        if action not in ['add', 'delete']:
            print("Invalid action. Exiting...")
            return

        if action == 'delete':
            image_number = input("Enter the number of the image you want to delete: ")
            try:
                image_to_delete = images[int(image_number) - 1]
                os.remove(os.path.join(folder_path, image_to_delete))
                print(f"Image {image_to_delete} deleted successfully.")
            except (IndexError, ValueError):
                print("Invalid image number.")
            except Exception as e:
                print(f"Error deleting image: {e}")
        elif action == 'add':
            image_path = input("Enter the path of the image you want to add: ")
            try:
                shutil.copy(image_path, folder_path)
                print(f"Image added successfully to {folder_path}.")
            except Exception as e:
                print(f"Error adding image: {e}")

        # 询问是否继续
        continue_choice = input("\nDo you want to continue? (yes/no): ").lower()
        if continue_choice != 'yes':
            break  # 如果用户不想继续，退出循环

# GUI
def manage_folder_images_gui():
    window = tk.Toplevel()
    window.title("Manage Folder Images")
    window.configure(background='#81BECE')

    # 设置窗口大小为16:9比例，例如640x360
    window.geometry("640x360")

    # 使用辅助函数更新显示的文件夹路径
    def update_folder_path_display(*args):
        selected_folder_key = folder_var.get()
        selected_folder_path = folders[selected_folder_key]
        folder_path_label.config(text=f"Selected folder: {selected_folder_path}")
    def add_image(folder_path):
        image_path = filedialog.askopenfilename(title="Select an image to add", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if image_path:
            try:
                shutil.copy(image_path, folder_path)
                messagebox.showinfo("Success", "Image added successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add image: {e}")

    def delete_image(folder_path):
        images = [file for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        image_name = simpledialog.askstring("Delete Image", "Enter the name of the image to delete:")
        if image_name in images:
            try:
                os.remove(os.path.join(folder_path, image_name))
                messagebox.showinfo("Success", "Image deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete image: {e}")
        else:
            messagebox.showinfo("Info", "Image not found.")

    folders = {
        '' : 0,
        '1': c.IMAGE_PATH_cover,
        '2': c.IMAGE_PATH_secret,
        '3': c.IMAGE_PATH_steg,
        '4': c.VAL_PATH
    }

    label = ttk.Label(window, text="Select a folder:")
    label.pack(pady=10)

    folder_var = tk.StringVar(window)
    folder_var.set(list(folders.keys())[0])  # 默认值
    folder_var.trace("w", update_folder_path_display)  # 当选项变化时更新显示

    folder_menu = ttk.OptionMenu(window, folder_var, *folders.keys())
    folder_menu.pack(pady=10)

    # 标签用于显示当前选中的文件夹路径
    folder_path_label = ttk.Label(window, text="Selected folder: ")
    folder_path_label.pack(pady=10)

    # 使用ttk.Button
    add_button = ttk.Button(window, text="Add Image", command=lambda: add_image(folders[folder_var.get()]))
    add_button.pack(pady=5)

    delete_button = ttk.Button(window, text="Delete Image", command=lambda: delete_image(folders[folder_var.get()]))
    delete_button.pack(pady=5)

    # 调整按钮和标签的样式
    style = ttk.Style()
    style.configure('TButton', padding=6, relief='flat', background='#81BECE')
    style.configure('TLabel', padding=4, background='#81BECE')


# Web
def manage_folder_images_web(request_data):
    # 从请求数据中获取操作类型和相关信息
    action = request_data.get('action')  # 'add' 或 'delete'
    folder_choice = request_data.get('folder_choice')  # '1', '2', '3', '4'
    image_name = request_data.get('image_name', '')  # 对于删除操作
    image_path = request_data.get('image_path', '')  # 对于添加操作

    # 定义文件夹路径选项
    folders = {
        '1': 'image/cover/',
        '2': 'image/secret/',
        '3': 'image/data/',
        '4': 'image/steg/'
    }

    folder_path = folders.get(folder_choice,'')
    if not folder_path:
        return jsonify({'error': 'Invalid folder choice'}), 400

    # 确保文件夹存在
    Path(folder_path).mkdir(parents=True, exist_ok=True)

    if action == 'delete':
        # 执行删除操作
        try:
            os.remove(os.path.join(image_name))
            return jsonify({'message': f"Image {image_name} deleted successfully from {folder_path}."})
        except FileNotFoundError:
            return jsonify({'error': 'Image not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif action == 'add':
        # 执行添加操作
        try:
            # 使用原始文件名保存文件
            secure_filename(image_path)  # 确保文件名安全
            new_image_name = os.path.basename(image_name)
            new_file_path = os.path.join(folder_path, new_image_name)  # 构建新的文件路径
            # 复制文件到指定目录
            shutil.copy(image_path, new_file_path)
            # 返回文件名，不包含前缀路径
            return jsonify({'message': f"Image added successfully.", 'file_name': new_file_path})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid action'}), 400
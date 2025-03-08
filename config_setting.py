# -*- coding: gbk -*-
# 配置文件路径
import ast
import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# config.py路径
config_file_path = 'D:\Study\GraduationProjection\ProjectFiles\HiNet-tool\config.py'

# 显示当前所有参数
def display_config(config):
    for key, value in config.items():
        print(f'{key}: {value}')

# 读取配置文件
def load_config(path):
    expected_keys = [
    "clamp", "channels_in", "log10_lr", "lr", "epochs", "weight_decay", 
    "init_scale", "lamda_reconstruction", "lamda_guide", "lamda_low_frequency", 
    "device_ids", "batch_size", "cropsize", "betas", "weight_step", "gamma", 
    "cropsize_val", "batchsize_val", "shuffle_val", "val_freq", "TRAIN_PATH", 
    "VAL_PATH", "COVER_PATH", "SECRET_PATH", "STEG_PATH", "format_train", 
    "format_val", "format_cover", "format_secret", "format_steg", "loss_display_cutoff", 
    "loss_names", "silent", "live_visualization", "progress_bar", "MODEL_PATH", 
    "checkpoint_on_error", "SAVE_freq", "IMAGE_PATH", "IMAGE_PATH_cover", 
    "IMAGE_PATH_secret", "IMAGE_PATH_steg", "IMAGE_PATH_secret_rev", "suffix", 
    "tain_next", "trained_epoch"
    ]

    config = {}
    with open(path, 'r') as file:
        code = compile(file.read(), path, 'exec')
        exec(code, config)

    config = {k: v for k, v in config.items() if k in expected_keys}
    
    return config

# 保存配置文件
def save_config(config, path):
    with open(path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if '=' in line:
            key, _ = line.split('=', 1)
            key = key.strip()
            if key in config:
                new_line = f'{key} = {repr(config[key])}\n'
                updated_lines.append(new_line)
                continue
        updated_lines.append(line)

    with open(path, 'w') as file:
        file.writelines(updated_lines)

# 修改参数
def modify_config(config):
    param_to_modify = input("Enter the parameter name you want to modify: ")
    if param_to_modify in config:
        new_value = input(f"Enter the new value for {param_to_modify}: ")
        try:
            converted_value = eval(new_value)
        except NameError:
            converted_value = new_value
        config[param_to_modify] = converted_value
        print(f"{param_to_modify} has been updated to {converted_value}.")
    else:
        print(f"Parameter {param_to_modify} not found.")

# cmd
def setting_main():
    config = load_config(config_file_path)

    while True:
        print("\nCurrent Config:")
        display_config(config)
        print("\nOptions:")
        print("1. Modify a parameter")
        print("2. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            modify_config(config)
            save_config(config, config_file_path)
        elif choice == '2':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")

# GUI
def gui_modify_config():
    config = load_config(config_file_path)
    def update_config(param_to_modify):
        if param_to_modify in config:
            new_value = simpledialog.askstring("New Value", f"Enter the new value for {param_to_modify}:", parent=window)
            if new_value is not None:
                try:
                    config[param_to_modify] = eval(new_value, {"__builtins__": None}, {})
                except:
                    config[param_to_modify] = new_value
                messagebox.showinfo("Updated", f"{param_to_modify} has been updated.", parent=window)
                display_config() 
        else:
            messagebox.showerror("Error", f"Parameter {param_to_modify} not found.", parent=window)

    def display_config():
        for i in tree.get_children():
            tree.delete(i) 
        for key, value in config.items():
            tree.insert("", tk.END, values=(key, value))

    window = tk.Toplevel()
    window.title("Configuration Settings")
    window.geometry("640x360") 
    window.configure(background='#81BECE')

    tree = ttk.Treeview(window, columns=("Parameter", "Value"), show="headings")
    tree.heading("Parameter", text="Parameter")
    tree.heading("Value", text="Value")
    tree.pack(expand=True, fill=tk.BOTH)

    config = load_config(config_file_path)
    display_config()

    modify_button = ttk.Button(window, text="Modify a parameter", command=lambda: update_config(simpledialog.askstring("Modify Configuration", "Enter the parameter name you want to modify:", parent=window)))
    modify_button.pack(side=tk.BOTTOM, pady=5)

    def save_and_exit():
        save_config(config, config_file_path)
        window.destroy()
        messagebox.showinfo("Save and Exit", "Configuration saved successfully.")

    save_exit_button = ttk.Button(window, text="Save & Exit", command=save_and_exit)
    save_exit_button.pack(side=tk.BOTTOM, pady=5)

    window.mainloop()

# Web
def modify_config_with_json(data):
    config_item = data.get('config_item')
    new_value = data.get('new_value')
    updated = False
    response_message = ""
    
    try:
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
        
        with open(config_file_path, 'w') as file:
            for line in lines:
                if line.strip().startswith(config_item):
                    try:
                        evaluated_value = ast.literal_eval(new_value)
                    except (ValueError, SyntaxError):
                        evaluated_value = new_value  
                    
                    file.write(f"{config_item} = {repr(evaluated_value)}\n")
                    updated = True
                else:
                    file.write(line)
        
        response_message = f"Configuration item '{config_item}' updated to {new_value}." if updated else "Configuration item not found."
    except Exception as e:
        response_message = f"Failed to update configuration: {e}"
    
    return {'success': updated, 'message': response_message}

def query_config_as_json():
    config = load_config(config_file_path)
    config_json = json.dumps(config, indent=4)
    return config_json
# -*- coding: gbk -*-
import os
import json
import subprocess
from flask_cors import CORS
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# 引入模块
import folder_operations as fp
import text_encoding as tcoding
import config_setting as cs
import encryption as enc

app = Flask(__name__, static_folder='image', static_url_path='/image')
CORS(app)

FOLDERS = {
        '1': 'image/cover/',
        '2': 'image/secret/',
        '3': 'image/data/',
        '4': 'image/steg/'
}
TEXT_FOLDER = 'image/texts'
KEY_FOLDER = 'image/keys'
TEXTSTEG_FOLDER = 'image/textencode'

@app.route('/api/start_training', methods=['POST'])
def start_training():
    try:
        # 使用 Popen 启动训练脚本并捕获输出
        with subprocess.Popen(['python', 'one_click_train.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()

        if process.returncode == 0:
            # 训练成功完成
            return jsonify({
                'status': 'Training completed successfully',
                'output': stdout
            }), 200
        else:
            # 训练过程中发生错误，但我们希望将错误信息反馈给前端
            if stderr:
                return jsonify({
                    'status': 'Training completed with errors',
                    'errors': stderr
                }), 200
            else:
                # 没有错误信息，可能是启动失败
                return jsonify({
                    'status': 'Training failed to start',
                    'error': 'No error message from training script.'
                }), 500
    except Exception as e:
        # 启动训练脚本时发生错误
        error_message = str(e)
        return jsonify({
            'status': 'Training failed to start',
            'error': error_message
        }), 500

@app.route('/api/encrypt', methods=['GET'])
def encrypt():
    option = request.args.get('option')
    if option:
        response = enc.encryption_json(option)
    else:
        response = {'error': 'Missing option'}, 400
    return jsonify(response)

@app.route('/api/folder/images', methods=['GET'])
def get_images_in_folder():
    folder_choice = request.args.get('folder_choice')
    folder_path = FOLDERS.get(folder_choice)

    if not folder_path:
        return jsonify({'error': 'Invalid folder choice'}), 400

    try:
        images = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        return jsonify({'imgs':[FOLDERS[folder_choice]+os.path.basename(image) for image in images]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/folder/action', methods=['GET'])
def folder_action():
    action = request.args.get('action')                # 'add' 或 'delete'
    folder_choice = request.args.get('folder_choice')  # '1', '2', '3', '4'
    image_name = request.args.get('image_name', None)  # 对于删除操作
    image_path = request.args.get('image_path', None)  # 对于添加操作

    request_data = {
        'action': action,
        'folder_choice': folder_choice,
        'image_name': image_name,
        'image_path': image_path
    }
    response = fp.manage_folder_images_web(request_data)
    return response

@app.route('/api/folder/action2', methods=['POST'])
def folder_action_add():
    action = request.form.get('action')                # 'add' 或 'delete'
    folder_choice = request.form.get('folder_choice')  # '1', '2', '3', '4'
    image_path = request.files.get('image_path')       # 对于添加操作

    if action not in ['add', 'delete']:
        return jsonify({'error': 'Invalid action'}), 400
    if action == 'add' and not image_path:
        return jsonify({'error': 'No file part in the request'}), 400
    if action == 'delete' and not folder_choice:
        return jsonify({'error': 'Folder choice is required for delete operation'}), 400

    # 处理添加操作
    if action == 'add':
        filename = secure_filename(image_path.filename)
        directory = os.path.join('uploads', str(folder_choice))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        image_path.save(file_path)
        
    request_data = {
        'action': action,
        'folder_choice': folder_choice,
        'image_name': filename if action == 'add' else os.path.basename(request.form.get('image_name')),
        'image_path': file_path if action == 'add' else None
    }
    response_data = fp.manage_folder_images_web(request_data)

    return response_data

@app.route('/api/configset', methods=['POST'])
def configset():
    config_item = request.json.get('config_item')
    new_value = request.json.get('new_value')
    if config_item and new_value:
        response = cs.modify_config_with_json({'config_item': config_item, 'new_value': new_value})
    else:
        response = {'error': 'Invalid request'}, 400
    return jsonify(response)

@app.route('/api/configs', methods=['GET'])
def get_config():
    config_json = cs.query_config_as_json()
    config_dict = json.loads(config_json) 
    return jsonify(config_dict)

@app.route('/api/listTextFiles', methods=['GET'])
def list_text_files():
    texts_dir = 'Dataset/texts'
    try:
        files = [f for f in os.listdir(texts_dir) if os.path.isfile(os.path.join(texts_dir, f))]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/textencoding', methods=['GET'])
def textencoding():
    text_input = request.args.get('text_input')
    file_path = request.args.get('file_path')
    file_path = os.path.join(TEXT_FOLDER,file_path)
    if text_input or file_path:
        option = {'text_input': text_input, 'file_path': file_path}
        response = tcoding.encode_text_json(option)
    else:
        response = {'error': 'Invalid request'}, 400
    return jsonify(response)

@app.route('/api/textdecoding', methods=['POST'])
def textdecoding():
    image_file = request.files.get('image_path')
    key_file = request.files.get('key_path')
    
    if image_file and key_file:
        image_save_path = os.path.join(TEXTSTEG_FOLDER, image_file.filename)
        key_save_path = os.path.join(KEY_FOLDER, key_file.filename)
        
        with open(image_save_path, 'wb') as image_temp_file:
            image_temp_file.write(image_file.read())
        with open(key_save_path, 'wb') as key_temp_file:
            key_temp_file.write(key_file.read())

        option = {
            'image_path': image_save_path,
            'key_path': key_save_path
        }
        
        response = tcoding.decode_image_json(option)
        
        if response:
            return jsonify(response)
        else:
            return {'error': 'Decoding failed'}, 500
    else:
        return {'error': 'Invalid request'}, 400

if __name__ == '__main__':
    app.run(debug=True)
new Vue({
    el: '#app',
    data: {
        // 通用参数
        selectedDemo: 0, // 初始值，表示没有选中任何 demo        
        selectedFile: null, // 用于存储选中的文件           
        imageList: [],
        // 设置参数
        showSettings: false,
        settingsParams: {},
        selectedParamKey: null,
        selectedParamValue: null,
        // 隐写参数
        encryptResponse: null,
        // 文件管理参数
        selectedFolder: null,
        selectedImageIndex: -1,
        selectedFile_img: null,
        // 文本隐写参数
        textfile: null,
        stegImage: null, // 隐写后的图像
        selectedImage: null, //选择的待解密图像
        decryptedText: '', // 解密后的文本
        inputType: 'text', // 初始值设置为 'text'
        textInput: '',
        selectedKey: null,
    },

    methods: {
        // 常规方法
        toggleSettings() {
            this.showSettings = !this.showSettings;
            this.selectedDemo = null; // 关闭设置时重置demo选择
            if (this.showSettings) {
                this.showconfig(); // 当设置界面被打开时，自动获取配置参数
            }
        },
        backToMain() {
            this.showSettings = !this.showSettings;
            this.selectedDemo = null; // 关闭设置时重置demo选择
        },
        changeSelectedDemo(demo) {
            this.selectedDemo = demo;
            this.selectedFile = null;
        },
        scaleImage(event) {
            // 'event' is the event object, and 'target' refers to the hovered image element
            const imageElement = event.target;
            imageElement.style.transform = 'scale(1.2)'; // Scale the image to 120% of its original size
        },
        // Method to restore the image to its original size
        restoreImage(event) {
            // 'event' is the event object, and 'target' refers to the image element that the mouse left
            const imageElement = event.target;
            imageElement.style.transform = 'scale(1)'; // Reset the image to its original size
        },

        // 设置模块
        async showconfig() {
            try {
                const response = await fetch(`http://127.0.0.1:5000/api/configs`);
                if (response.ok) {
                    const configData = await response.json();
                    this.settingsParams = configData; // 更新Vue实例的settingsParams属性
                } else {
                    console.error('Network response was not ok.');
                }
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
            }
        },

        saveSettings() {
            // 从Vue实例的数据属性中获取参数名称和新值
            const configItem = this.selectedParamKey;
            const newValue = this.selectedParamValue;

            // 验证输入的有效性
            if (!configItem || !newValue) {
                alert('请选择参数并输入新值');
                return;
            }

            // 创建请求数据对象
            const requestData = {
                config_item: configItem,
                new_value: newValue
            };

            // 发送POST请求到后端更新配置
            fetch('http://127.0.0.1:5000/api/configset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // 根据后端返回的响应处理结果
                    if (data.error) {
                        alert(data.error);
                    } else {
                        // 更新前端的设置参数，以便用户看到更改
                        this.settingsParams[configItem] = newValue;
                        alert('参数保存成功');
                    }
                })
                .catch(error => {
                    console.error('There was a problem with the save settings operation:', error);
                    alert('保存参数时发生错误');
                });
        },
        startTraining() {
            fetch('http://127.0.0.1:5000/api/start_training', {
                    method: 'POST',
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'Training completed successfully') {
                        alert('训练已成功完成');
                    } else if (data.status === 'Training completed with errors') {
                        alert('训练完成但存在错误');
                        console.error('Training errors:', data.errors);
                    } else if (data.status === 'Training failed to start') {
                        alert('训练启动失败');
                    }
                    console.log('Training output:', data.output);
                })
                .catch(error => {
                    console.error('Error starting training:', error);
                    alert('训练启动时发生错误');
                });
        },

        // 图像隐写模块
        async ImageEncrypt() {
            let res = await this.encrypt('encrypt')
            this.encryptResponse = res
            console.log(res);
        },

        async ImageDecrypt() {
            let res = await this.encrypt('decrypt')
            this.encryptResponse = res
            console.log(res);
        },

        async encrypt(data) {
            return new Promise((resolve, reject) => {
                fetch(`http://127.0.0.1:5000/api/encrypt?option=${data}`)
                    .then(response => {
                        if (response.ok) {
                            return response.json()
                        } else {
                            throw new Error('Network response was not ok.');
                        }
                    })
                    .then(data => {
                        resolve(data)
                    })
                    .catch(error => {
                        reject(error)
                    });
            })
        },
        // 文本管理模块
        async showFolder() {
            try {
                const response = await fetch(
                    `http://127.0.0.1:5000/api/folder/images?folder_choice=${encodeURIComponent(this.selectedFolder)}`
                );

                if (response.ok) {
                    const images = await response.json();
                    console.log('images', images);
                    this.imageList = images['imgs'] || []; // 确保 this.imageList 是一个数组
                    this.maxImageIndex = this.imageList.length;

                    // 检查图片列表是否为空，并弹出相应的警告
                    if (this.imageList.length === 0) {
                        alert("这个文件夹是空的");
                    }

                    console.log(this.maxImageIndex);
                } else {
                    console.error('Network response was not ok.');
                }
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
            }
        },

        deleteFile() {
            if (this.selectedImageIndex >= 0 && this.selectedImageIndex < this.imageList.length) {
                // 获取用户选择的图片文件名
                const imageToDelete = this.imageList[this.selectedImageIndex];
                // 构建请求参数
                const requestData = {
                    action: 'delete',
                    folder_choice: this.selectedFolder, // 使用selectedFolder的值
                    image_name: imageToDelete // 使用imageList中对应的图片文件名
                };

                // 发送请求到后端进行图片删除
                fetch(`http://127.0.0.1:5000/api/folder/action?${new URLSearchParams(requestData)}`)
                    .then(response => {
                        if (response.ok) {
                            return response.json();
                        } else {
                            throw new Error('Failed to delete file');
                        }
                    })
                    .then(data => {
                        if (data && data.message) {
                            // 如果删除成功，从列表中移除该图片
                            this.imageList.splice(this.selectedImageIndex, 1);
                            // 更新selectedImageIndex以反映新的列表状态
                            this.selectedImageIndex = -1;
                            // 可选：清除已删除图片的预览
                            this.selectedFile = null;
                            console.log('File deleted successfully');
                        } else {
                            console.error('Failed to delete file', data);
                        }
                    })
                    .catch(error => {
                        console.error('Error during file deletion:', error);
                    });
            }
        },

        async uploadFile() {
            if (this.selectedFile) {
                // 创建一个FormData对象
                const formData = new FormData();
                // 可以添加其他数据，例如文件夹选择
                formData.append('action', 'add')
                formData.append('folder_choice', this.selectedFolder);
                // 将文件添加到FormData对象中            
                formData.append('image_path', this.selectedFile);
                // 发送POST请求到后端进行文件上传
                fetch('http://127.0.0.1:5000/api/folder/action2', {
                        method: 'POST',
                        body: formData // 将FormData对象作为请求体
                    })
                    .then(response => {
                        if (!response.ok) {
                            // 如果响应不是2xx，抛出错误
                            throw new Error(`Network response was not ok: ${response.status}`);
                        }
                        return response.json();
                    }).then(data => {
                        if (data && data.message) {
                            this.imageList.push(data.file_name);
                            console.log('File uploaded successfully');
                        } else {
                            console.error('Failed to upload file', data);
                        }
                    }).catch(error => {
                        console.error('Error during file upload:', error);
                        alert('上传文件时出现问题。请检查网络连接和后端服务器是否正常工作，然后重试。');
                    });
            }
        },

        selectFile_img(event) {
            const file = event.target.files;
            if (file.length > 0) {
                this.selectedFile_img = URL.createObjectURL(file[0]);
                this.selectedFile = file[0];
            } else {
                this.selectedFile = null;
            }
        },

        // 文本隐写模块
        toggleInputType(type) {
            this.inputType = type;
        },

        handleFileSelection(event) {
            this.selectedFile = event.target.files[0];
        },

        handleStegSelection(event) {
            this.selectedImage = event.target.files[0];
        },

        handleKeySelection(event) {
            this.selectedKey = event.target.files[0];
        },

        textEncoding() {
            // 获取用户输入的文本和选择的文件
            const inputType = this.inputType;
            const textInput = this.textInput;
            const selectedFile = this.selectedFile;

            const requestData = {
                text_input: textInput,
                file_path: selectedFile
            }

            // 发送请求到后端进行文本隐写
            fetch(`http://127.0.0.1:5000/api/textencoding?${new URLSearchParams(requestData)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // 处理后端返回的隐写结果
                    this.stegImage = data.steg_image; // 将隐写后的图像信息存储在data属性中
                    this.$forceUpdate(); // 强制更新视图以显示隐写后的图像    
                    console.log('Text encoding result:', data);
                    alert('隐写成功！');
                }).catch(error => {
                    console.error('There was a problem with the text encoding operation:', error);
                });
        },

        textDecoding() {
            const selectImage = this.selectedImage; // 获取用户选择的含密图像文件 
            const selectedKey = this.selectedKey; // 获取用户选择的密钥文件
            console.log(selectImage);
            console.log(selectedKey);
            // 验证所选文件的有效性
            if (!selectImage || !selectedKey) {
                alert('请选择含密图像和密钥文件');
                return;
            }

            // 创建FormData对象
            const requestData = new FormData();
            requestData.append('image_path', selectImage, selectImage.name); // 直接将文件对象添加到FormData
            requestData.append('key_path', selectedKey, selectedKey.name); // 直接将文件对象添加到FormData
            console.log(requestData);
            // 发送POST请求到后端进行文本解密
            fetch('http://127.0.0.1:5000/api/textdecoding', {
                    method: 'POST',
                    body: requestData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // 处理后端返回的解密结果
                    this.decryptedText = data.decrypted_text; // 将解密后的文本存储在data属性中
                    this.$forceUpdate(); // 强制更新视图以显示解密后的文本    
                    console.log('Text decoding result:', data);
                    alert('解密成功！');
                }).catch(error => {
                    console.error('There was a problem with the text decoding operation:', error);
                });
        }
    },
});
import os
import random

def generate_random_name(min_val=1, max_val=9999):
    """生成一個隨機數字名稱"""
    number = random.randint(min_val, max_val)
    new_name = f"{number:04d}.mp3"
    return new_name

def shuffle_mp3_files(directory_path):
    """隨機更改目錄中 MP3 檔案的名稱以打亂播放順序"""
    files = [f for f in os.listdir(directory_path) if f.endswith('.mp3')]
    
    for filename in files:
        file_path = os.path.join(directory_path, filename)
        new_name = generate_random_name()
        new_file_path = os.path.join(directory_path, new_name)
        
        # 如果新名稱已存在於目錄中，則重新生成一個名稱
        while os.path.exists(new_file_path):
            new_name = generate_random_name()
            new_file_path = os.path.join(directory_path, new_name)
        
        os.rename(file_path, new_file_path)
        print(f'Renamed: {filename} -> {new_name}')

directory_path = '/Users/little/Downloads/music'  
shuffle_mp3_files(directory_path)
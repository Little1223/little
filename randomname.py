import os
import random

def generate_unique_name(existing_names, min_val=1, max_val=9999):
    """生成一個唯一的隨機數字名稱"""
    while True:
        number = random.randint(min_val, max_val)
        new_name = f"{number:04d}.mp3"
        if new_name not in existing_names:
            existing_names.add(new_name)
            return new_name

def shuffle_mp3_files(directory_path):
    """隨機更改目錄中 MP3 檔案的名稱為唯一的數字，打亂播放順序"""
    files = [f for f in os.listdir(directory_path) if f.endswith('.mp3')]
    existing_names = set()
    
    for filename in files:
        file_path = os.path.join(directory_path, filename)
        new_name = generate_unique_name(existing_names)
        new_file_path = os.path.join(directory_path, new_name)
        os.rename(file_path, new_file_path)
        print(f'Renamed: {filename} -> {new_name}')

directory_path = '/Users/little/Downloads/music'  
shuffle_mp3_files(directory_path)

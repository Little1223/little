import os
import random

def shuffle_mp3_files(directory_path):
    """隨機更改目錄中 MP3 檔案的名稱，以便打亂播放順序"""
    files = [f for f in os.listdir(directory_path) if f.endswith('.mp3')]
    random.shuffle(files)
    
    for i, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        new_name = f"{i + 1:03d}.mp3"
        new_file_path = os.path.join(directory_path, new_name)
        os.rename(file_path, new_file_path)
        print(f'Renamed: {filename} -> {new_name}')

# 使用範例
directory_path = '/Users/little/Downloads/music'  
shuffle_mp3_files(directory_path)

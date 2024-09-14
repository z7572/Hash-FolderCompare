import os
import sys
import time
import hashlib
import tempfile
import subprocess
from collections import defaultdict

def calculate_hash(file_path):
    """计算文件的SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def compare_folders(folder1, folder2, output_file):
    folder1_files = {}
    folder2_files = {}
    folder1_dirs = {}
    folder2_dirs = {}
    hash_to_file1 = defaultdict(list)
    hash_to_file2 = defaultdict(list)

    # 遍历文件夹1并计算哈希值，区分文件和文件夹
    for root, dirs, files in os.walk(folder1):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder1)
            file_hash = calculate_hash(full_path)
            folder1_files[relative_path] = file_hash
            hash_to_file1[file_hash].append(relative_path)
        for dir in dirs:
            full_path = os.path.join(root, dir)
            relative_path = os.path.relpath(full_path, folder1)
            folder1_dirs[relative_path] = dir

    # 遍历文件夹2并计算哈希值，区分文件和文件夹
    for root, dirs, files in os.walk(folder2):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder2)
            file_hash = calculate_hash(full_path)
            folder2_files[relative_path] = file_hash
            hash_to_file2[file_hash].append(relative_path)
        for dir in dirs:
            full_path = os.path.join(root, dir)
            relative_path = os.path.relpath(full_path, folder2)
            folder2_dirs[relative_path] = dir

    # 定义存储差异的列表
    added_files = []
    removed_files = []
    modified_files = []
    moved_files = []
    moved_files_to_path = []

    # 检查文件夹1中的文件和文件夹是否在文件夹2中
    folder1_paths = set(folder1_files.keys())
    folder2_paths = set(folder2_files.keys())
    folder1_dir_paths = set(folder1_dirs.keys())
    folder2_dir_paths = set(folder2_dirs.keys())

    # 文件检测
    for file in folder1_files:
        if file not in folder2_paths:
            file_hash = folder1_files[file]
            matched_files = hash_to_file2.get(file_hash, [])
            if len(matched_files) == 1 and matched_files[0] not in folder1_paths:
                moved_files.append(matched_files[0])
                moved_files_to_path.append(f"{file} > {matched_files[0]}")
            else:
                removed_files.append(file)
        else:
            if folder1_files[file] != folder2_files[file]:
                modified_files.append(file)

    for file in folder2_files:
        if file not in folder1_paths and file not in moved_files:
            added_files.append(file)

    # 文件夹检测
    for dir in folder1_dirs:
        if dir not in folder2_dir_paths:
            similar_dir = None
            max_similarity = 0
            for other_dir in folder2_dirs:
                if os.path.basename(dir) == os.path.basename(other_dir):
                    # 计算相似度
                    similarity = calculate_directory_similarity(os.path.join(folder1, dir), os.path.join(folder2, other_dir))
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_dir = other_dir
            if similar_dir and max_similarity > 0.5:  # 设置相似度阈值
                moved_files_to_path.append(f"{dir} > {similar_dir}")
            else:
                removed_files.append(dir)

    for dir in folder2_dirs:
        if dir not in folder1_dir_paths:
            similar_dir = None
            max_similarity = 0
            for other_dir in folder1_dirs:
                if os.path.basename(dir) == os.path.basename(other_dir):
                    similarity = calculate_directory_similarity(os.path.join(folder2, dir), os.path.join(folder1, other_dir))
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_dir = other_dir
            if not similar_dir or max_similarity <= 0.5:
                added_files.append(dir)

    # 写入差异结果到临时文件
    with open(output_file, 'w', encoding='utf-8') as f:
        if added_files or removed_files or moved_files_to_path or modified_files:
            f.write(f"{folder1}\n{folder2}\n\n")
            if moved_files_to_path:
                f.write("移动的文件:\n" + "=" * 30 + "\n")
                f.write("\n".join(moved_files_to_path) + "\n\n")
            if added_files:
                f.write("新增的文件:\n" + "=" * 30 + "\n")
                f.write("\n".join(added_files) + "\n\n")
            if removed_files:
                f.write("删除的文件:\n" + "=" * 30 + "\n")
                f.write("\n".join(removed_files) + "\n\n")
            if modified_files:
                f.write("修改的文件:\n" + "=" * 30 + "\n")
                f.write("\n".join(modified_files) + "\n\n")
        else:
            f.write("未找到任何差异\n")

def calculate_directory_similarity(dir1, dir2):
    """计算两个目录的相似度"""
    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))
    intersection = files1.intersection(files2)
    union = files1.union(files2)
    return len(intersection) / len(union) if union else 0

if __name__ == "__main__":
    try:
        folder1 = sys.argv[1]
        print(folder1)
    except IndexError:
        folder1 = input("请拖拽或输入原文件路径: ").strip('"')
    folder2 = input("请拖拽或输入新文件路径: ").strip('"')
    start_time = time.time()
    print("处理中...")

    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        output_file = temp_file.name

    compare_folders(folder1, folder2, output_file)

    end_time = time.time()
    print(f"对比完成，共耗时 {end_time - start_time:.2f} 秒")

    # 使用默认文本编辑器打开临时文件
    subprocess.call(['notepad', output_file])

    # 删除临时文件
    os.remove(output_file)

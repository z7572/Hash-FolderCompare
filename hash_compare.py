import os
import sys
import time
import zlib
import hashlib
import tempfile
import subprocess

# 计算文件的哈希值函数
def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def calculate_sha1(file_path):
    sha1_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha1_hash.update(byte_block)
    return sha1_hash.hexdigest()

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_crc32(file_path):
    crc32_value = 0
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            crc32_value = zlib.crc32(byte_block, crc32_value)
    return format(crc32_value & 0xFFFFFFFF, '08x')

# 对比两个文件的哈希值并将结果写入输出文件
def compare_hashes(file1, file2, output_file):
    hash_results = []
    
    md5_1, md5_2 = calculate_md5(file1), calculate_md5(file2)
    sha1_1, sha1_2 = calculate_sha1(file1), calculate_sha1(file2)
    sha256_1, sha256_2 = calculate_sha256(file1), calculate_sha256(file2)
    crc32_1, crc32_2 = calculate_crc32(file1), calculate_crc32(file2)

    hash_results.append(f"[MD5]\n{'✔' if md5_1 == md5_2 else '✘'} {md5_1}\n{'✔' if md5_1 == md5_2 else '✘'} {md5_2}\n")
    hash_results.append(f"[SHA1]\n{'✔' if sha1_1 == sha1_2 else '✘'} {sha1_1}\n{'✔' if sha1_1 == sha1_2 else '✘'} {sha1_2}\n")
    hash_results.append(f"[SHA256]\n{'✔' if sha256_1 == sha256_2 else '✘'} {sha256_1}\n{'✔' if sha256_1 == sha256_2 else '✘'} {sha256_2}\n")
    hash_results.append(f"[CRC32]\n{'✔' if crc32_1 == crc32_2 else '✘'} {crc32_1}\n{'✔' if crc32_1 == crc32_2 else '✘'} {crc32_2}\n")

    # 写入到输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{file1}\n{file2}\n\n")
        f.write("\n".join(hash_results))

if __name__ == "__main__":
    try:
        file1 = sys.argv[1]
        print(file1)
    except IndexError:
        file1 = input("请拖拽或输入第一个文件路径: ").strip('"')
    
    file2 = input("请拖拽或输入第二个文件路径: ").strip('"')
    start_time = time.time()
    print("处理中...")

    # 创建临时文件用于保存对比结果
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        output_file = temp_file.name

    # 进行哈希对比
    compare_hashes(file1, file2, output_file)

    end_time = time.time()
    print(f"对比完成，共耗时 {end_time - start_time:.2f} 秒")

    # 使用记事本打开结果文件
    subprocess.call(['notepad', output_file])

    # 删除临时文件
    os.remove(output_file)

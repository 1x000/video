import os
import subprocess

def convert_videos(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp4"):
                input_file = os.path.join(root, file)
                if os.path.isfile(input_file):  # 检查文件是否存在
                    output_dir = os.path.join(root, os.path.splitext(file)[0])
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, "output.m3u8")
                    command = ["ffmpeg", "-i", input_file, "-threads", "8", "-c:v", "libx264", "-c:a", "aac", "-strict", "-2", "-f", "hls", "-hls_list_size", "0", "-hls_time", "1", output_file]
                    subprocess.run(command)
                else:
                    print(f"文件 {input_file} 不存在")

convert_videos(os.getcwd())

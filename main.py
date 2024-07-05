import os
import mimetypes
from datetime import datetime
import json
import ffmpeg
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify

# 配置项
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UP_DIR = os.path.join(SCRIPT_DIR, 'UP')
OUTPUT_FILE = 'index.html'

# Jinja2模板加载器
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

# 提取视频标题的函数
def extract_video_title(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is not None:
            return video_stream.get('tags', {}).get('title', os.path.splitext(os.path.basename(video_path))[0])
    except Exception:
        return os.path.splitext(os.path.basename(video_path))[0]

# 生成文件信息列表
def generate_file_info_list(directory):
    files = []
    for root, dirs, files_in_dir in os.walk(directory):
        for file in files_in_dir:
            file_path = os.path.join(root, file)
            file_mime = mimetypes.guess_type(file_path)[0]
            if file_mime and file_mime.startswith('video'):
                relative_path = os.path.relpath(file_path, SCRIPT_DIR)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                file_mtime_str = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
                file_info = {
                    'path': relative_path.replace('\\', '/'),  # 使用正斜杠作为路径分隔符
                    'size': file_size,
                    'modified': file_mtime_str,
                    'type': 'video',
                    'mimeType': file_mime,
                    'title': extract_video_title(file_path)
                }
                files.append(file_info)
    return files

# 渲染模板并混淆HTML和JavaScript
def render_template(files):
    video_files_json = json.dumps(files)
    html = template.render(video_files_json=video_files_json)
    minified_html = minify(html, remove_comments=True, remove_empty_space=True, remove_all_empty_space=True)
    return minified_html

# 写入HTML文件
def write_html_file(html, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

# 主函数
def main():
    files = generate_file_info_list(UP_DIR)
    html = render_template(files)
    write_html_file(html, OUTPUT_FILE)

if __name__ == '__main__':
    main()

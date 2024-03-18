import os
import mimetypes
from datetime import datetime
import ffmpeg
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify

# 配置项
DIRECTORY = './'
FILE_TYPES = ['video', 'image', 'document']
OUTPUT_FILE = 'index.html'
WALINE_SERVER_URL = 'https://video-pl.vercel.app'

# Jinja2模板加载器
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')


# 提取视频标题的函数
def extract_video_title(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is not None:
            return video_stream.get('title', os.path.splitext(os.path.basename(video_path))[0])
    except Exception:
        return os.path.splitext(os.path.basename(video_path))[0]


# 生成文件信息列表
files = []
for root, dirs, files_in_dir in os.walk(DIRECTORY):
    for file in files_in_dir:
        file_path = os.path.join(root, file)
        file_mime = mimetypes.guess_type(file_path)[0]
        if file_mime:
            for file_type in FILE_TYPES:
                if file_mime.startswith(file_type):
                    file_size = os.path.getsize(file_path)
                    file_mtime = os.path.getmtime(file_path)
                    file_mtime_str = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    file_info = {
                        'path': file_path,
                        'size': file_size,
                        'modified': file_mtime_str,
                        'type': file_type
                    }
                    if file_type == 'video':
                        file_info['title'] = extract_video_title(file_path)
                    files.append(file_info)

# 渲染模板并混淆HTML和JavaScript
html = template.render(files=files, waline_server_url=WALINE_SERVER_URL, mimetypes=mimetypes)
minified_html = minify(html, remove_comments=True, remove_empty_space=True, remove_all_empty_space=True)

# 写入HTML文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(minified_html)

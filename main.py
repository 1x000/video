# -*- coding: utf-8 -*-
"""雷锋视频归档网站生成脚本。

该脚本用于生成雷锋视频归档网站，包括生成网站的 HTML 文件和 sitemap.xml 文件。
"""

import os
import mimetypes
from datetime import datetime
import json
import ffmpeg
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify
from jsmin import jsmin

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_UP_DIR = os.path.join(_SCRIPT_DIR, 'UP')
_OUTPUT_FILE = 'index.html'
_SITEMAP_FILE = 'sitemap.xml'

_ENV = Environment(loader=FileSystemLoader('templates'))
_TEMPLATE = _ENV.get_template('index.html')
_SITEMAP_TEMPLATE = _ENV.get_template('sitemap.xml')


def extract_video_title(video_path: str) -> str:
    """从视频文件中提取标题。

    如果视频文件中存在标题信息，则提取该信息；否则使用文件名作为标题。

    Args:
      video_path: 视频文件路径。

    Returns:
      视频标题。
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
            None,
        )
        if video_stream is not None:
            return video_stream.get('tags', {}).get(
                'title', os.path.splitext(os.path.basename(video_path))[0]
            )
    except Exception:  # pylint: disable=broad-except
        return os.path.splitext(os.path.basename(video_path))[0]


def generate_file_info_list(directory: str) -> list:
    """遍历指定目录，生成视频文件信息列表。

    Args:
      directory: 要遍历的目录路径。

    Returns:
      视频文件信息列表。
    """
    files = []
    for root, _, files_in_dir in os.walk(directory):
        for file in files_in_dir:
            file_path = os.path.join(root, file)
            file_mime = mimetypes.guess_type(file_path)[0]
            if file_mime and file_mime.startswith('video'):
                relative_path = os.path.relpath(file_path, _SCRIPT_DIR)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                file_mtime_str = datetime.fromtimestamp(file_mtime).strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
                file_info = {
                    'path': relative_path.replace('\\', '/'),
                    'size': file_size,
                    'modified': file_mtime_str,
                    'type': 'video',
                    'mimeType': file_mime,
                    'title': extract_video_title(file_path),
                }
                files.append(file_info)
    return files


def render_template(files: list) -> str:
    """渲染 HTML 模板，生成网站 HTML 内容，并对 HTML 和 JavaScript 进行混淆。

    Args:
      files: 视频文件信息列表。

    Returns:
      生成的 HTML 内容。
    """
    displayed_videos = files[:10]
    video_files_json = json.dumps(files)
    html = _TEMPLATE.render(
        video_files_json=video_files_json,
        displayed_videos=displayed_videos,
    )

    # 混淆内嵌的 JavaScript 代码
    html_parts = html.split('<script>')
    minified_html = html_parts[0]
    for i in range(1, len(html_parts)):
        if i % 2 == 1:
            js_code = html_parts[i]
            end_index = js_code.find('</script>')
            if end_index != -1:
                js_code = js_code[:end_index]  # 截取到 `</script>` 之前
            minified_js = jsmin(js_code)
            minified_html += '<script>' + minified_js + '</script>'
        else:
            minified_html += '<script>' + html_parts[i]

    # 进行 HTML 混淆
    minified_html = minify(
        minified_html,
        remove_comments=True,
        remove_empty_space=True,
        remove_all_empty_space=True,
    )

    return minified_html


def generate_sitemap(files: list) -> str:
    """生成 sitemap.xml 内容。

    Args:
      files: 视频文件信息列表。

    Returns:
      生成的 sitemap.xml 内容。
    """
    urls = []
    for file in files:
        urls.append(
            {
                'loc': f'https://video.xpdbk.com/{file["path"]}',  # 替换为您的域名
                'lastmod': file['modified'],
                'changefreq': 'weekly',
                'priority': '0.8',
            }
        )
    sitemap_xml = _SITEMAP_TEMPLATE.render(urls=urls)
    return sitemap_xml


def write_html_file(html: str, output_file: str) -> None:
    """将生成的 HTML 内容写入指定文件。

    Args:
      html: 生成的 HTML 内容。
      output_file: 要写入的文件路径。
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)


def write_sitemap_file(sitemap_xml: str, output_file: str) -> None:
    """将生成的 sitemap.xml 内容写入指定文件。

    Args:
      sitemap_xml: 生成的 sitemap.xml 内容。
      output_file: 要写入的文件路径。
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)


def main() -> None:
    """主函数，执行网站生成过程。
    """
    files = generate_file_info_list(_UP_DIR)
    html = render_template(files)
    write_html_file(html, _OUTPUT_FILE)

    sitemap_xml = generate_sitemap(files)
    write_sitemap_file(sitemap_xml, _SITEMAP_FILE)


if __name__ == '__main__':
    main()

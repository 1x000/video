import os
import subprocess
import shlex

script_dir = os.path.dirname(os.path.realpath(__file__))
video_dir = script_dir

for root, dirs, files in os.walk(video_dir):
    for video in files:
        if video.endswith('.mp4'):
            filename, ext = os.path.splitext(video)

            out_file1 = filename + '_1' + ext
            cmd1 = f'ffmpeg -i {shlex.quote(os.path.join(root, video))} -threads 8 -g 90 -b:v 2000k -bufsize 2000k -maxrate 2500k {shlex.quote(os.path.join(root, out_file1))}'
            subprocess.run(cmd1, shell=True)

            out_file2 = filename + '_2' + ext
            cmd2 = f'ffmpeg -i {shlex.quote(os.path.join(root, out_file1))} -threads 8 -g 90 -r 30 {shlex.quote(os.path.join(root, out_file2))}'
            subprocess.run(cmd2, shell=True)

            os.remove(os.path.join(root, out_file1))

print('Done!')

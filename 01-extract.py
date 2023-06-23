import os
import re
import subprocess

inputPath  = '/path/to/your/anime/files'
outputPath = '/path/to/your/anime/keyframe'

for inputName in os.listdir(inputPath):
    if re.search(r'\.(avi|mp4|mkv|ogm|webm)$', inputName):
        os.makedirs(outputPath, exist_ok=True)
        videoPath = os.path.join(inputPath, inputName)
        frameName = f'{inputName}-%06d.png'
        framePath = os.path.join(outputPath, frameName)
        subprocess.run(['ffmpeg', '-i', videoPath, '-vf', 'select=eq(pict_type\\,I)', '-vsync', 'vfr', framePath], check=True)

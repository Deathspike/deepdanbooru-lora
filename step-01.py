import config
import os
import subprocess

for inputName in os.listdir(config.inputPath):
    os.makedirs(config.framePath, exist_ok=True)
    inputPath = os.path.join(config.inputPath, inputName)
    frameName = f'{inputName}-%06d.png'
    framePath = os.path.join(config.framePath, frameName)
    subprocess.run(['ffmpeg', '-i', inputPath, '-vf', 'select=eq(pict_type\\,I)', '-vsync', 'vfr', framePath], check=True)

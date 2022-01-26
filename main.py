import sounddevice as sd
import numpy as np
import requests
import os
import time
from subprocess import Popen

def print_sound(indata, outdata, frames, time, status):
    volume_norm = np.linalg.norm(indata)
    print (int(volume_norm))

# def lock():
# #os.system("xdg-screensaver lock")
#     requests.get("http://192.168.1.71:5000")
#     #input()

sound_list = []
light_status = 0

def read_mic_data(indata, outdata, frames, time, status):
    global light_status
    
    volume_norm = np.linalg.norm(indata) * 10
    n = int(volume_norm)
    if n >= 3:
        print(n)
    sound_list.append(n) 
    if n >= 400 and n <= 700 and n != 598 and n != 444:
        
        sd.sleep(2000)
        


        if light_status == 0:
            os.system("/home/justin/Python/mic/lights_on.py 192.168.1.129")
            light_status = 1
          
        elif light_status == 1:
            os.system("/home/justin/Python/mic/lights_off.py 192.168.1.129")
            light_status = 0
        


with sd.Stream(callback=read_mic_data):
    
    sd.sleep(1000000)


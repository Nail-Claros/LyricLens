import asyncio
import time
from apis import read_audio_file
from shazamio import Shazam, Serialize
import sys
import json
import time
import os
import glob
import requests
import base64
import json
path_to_dir = "audio_stream/ex.wav"
check_delay = 1  # (seconds) limit requests for Shazam

sys.path.append('/snap/bin/ffmpeg')
shazam = Shazam()

boll_th = 0
    
async def main():
    files = glob.glob('audio_stream/clips/*')
    for f in range(len(files)):
        # 
        out = await shazam.recognize(f"audio_stream/ex.wav")
        print("CYCLE: _______________________ " + str(f))
        if "track" in out and boll_th == 0:
            song_name = out['track']['title']
            song_artist = out['track']['subtitle']
            print(f'Title Name: {song_name}')
            print(f'Artist: {song_artist}')
            full_title = song_name + " " + song_artist
            print(full_title)
            hub_actions = out['track']['key']
            print(f"ID__Shazam_lib==== ({hub_actions})")
            print(full_title)
            boll_th == 1
            return full_title
    return None

loop = asyncio.get_event_loop()
loop.run_until_complete(main())




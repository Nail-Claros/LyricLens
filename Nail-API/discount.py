import time
import os
import glob
import requests
import base64
import json

from playg import main

def step2(full_title):
    key = os.environ.get('SHAZ_API_KEY')
    files = glob.glob('audio_stream/clips/*')
    genius_id = 0
    url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
    querystring = {"q":str(full_title),"per_page":"1","page":"1", "text_format":"String"}
    headers = {
        "x-rapidapi-key": str(key),
        "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    print(response.text)
    ax = json.loads(response.text)
    #look up song name for ID
    if response.status_code == 200 and 0 in ax["hits"]:
            print("IN____________________ ID FOUND")
            genius_id = ax['hits'][0]['result']['id']
            print(f'Genius ID: {genius_id}')
            # break

            url = "https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"
            # genius_id = 115478
            querystring = {"id":str(genius_id), "text_format":"html"}
            headers = {
                "x-rapidapi-key": str(key),
                "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring)
            print(response.text)
            ax = json.loads(response.text)
            #Return Song Lyrics
            if response.status_code == 200 and "lyrics" in ax:
                    print("IN____________________ LYRICS FOUND")
                    print('Lyrics: \n\n')
                    lyric_check = ax['lyrics']['lyrics']['body']['html']	
                    if lyric_check:
                        if not isinstance(lyric_check, str):lyric_check = str(lyric_check)
                        import sys
                        import io
                        # Set encoding for stdout
                        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
                        print('Lyrics_after wrapper: \n\n')
                        print(lyric_check)
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(lyric_check, features="html.parser")
                        s_txt = soup.get_text()
                        print('\n\n s_txt Lyrics: \n\n')
                        print(s_txt)
                        
                    else:
                        print("Cool song, however there are no lyrics for this cool tune")
            elif response.status_code == 200:
                print('Error: cant find track___________________lyrics' )

    elif response.status_code == 200:
        print('Error: cant find track___________________Id' )

titole = main()
if titole != None:
    step2(titole)
   
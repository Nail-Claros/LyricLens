import requests
import base64
import json
from bs4 import BeautifulSoup
import os
import boto3

key = os.getenv('SHAZ_API_KEY')
akey = os.getenv('alt_key')

coverart = ""
full_title = ""

# Configure AWS S3
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)


def get_s3_file_binary(bucket_name, object_key):
    try:
        # Fetch binary content from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_binary = response['Body'].read()
        
        # Encode binary data to base64
        return base64.b64encode(file_binary).decode('utf-8')
    except Exception as e:
        print(f"Error reading audio file from S3: {e}")
        return None




def run_apis(bucket_name, object_key):
    genius_id = 0

    # Get binary content from S3
    file_binary = get_s3_file_binary(bucket_name, object_key)
    if file_binary is None:
        return 0, "", "", "", "", ""

    url = "https://shazam.p.rapidapi.com/songs/v2/detect"
    querystring = {"timezone": "America/Chicago", "locale": "en-US"}
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": "shazam.p.rapidapi.com",
        "Content-Type": "application/octet-stream"
    }

    try:
        # Sending the binary audio content as payload
        response = requests.post(url, data=file_binary, headers=headers, params=querystring, timeout=10)

        # Log the raw response for debugging
        print(f"Response Content: {response.text}")
        
        # Check for successful response
        if response.status_code == 204:
            print("Error: No content returned from Shazam (status code 204). This might indicate no song detected.")
            return 0, "", "", "", "", ""

        if response.status_code != 200:
            print(f"Error: Received unexpected status code {response.status_code}")
            print(f"Response Content: {response.text}")
            return 0, "", "", "", "", ""

        # Log the raw response for debugging
        print(f"Response Content: {response.text}")

        # Parse the response as JSON
        try:
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON from the response")
            return 0, "", "", "", "", ""

        if "track" in ax:
            print("IN____________________ SONG FOUND")
            song_name = ax['track']['title']
            song_artist = ax['track']['subtitle']
            full_title = song_name + " " + song_artist
            print(full_title)

            if 'images' in ax['track']:
                coverart = ax['track']['images']['coverart']
            else:
                coverart = "fail"

            ax = return_lyrics(song_name, song_artist)
            if "hits" in ax:
                print("IN____________________ ID FOUND")
                genius_id = ax['hits'][0]['result']['id']

                if ax['hits'][0]['result']['instrumental']:
                    print("This song is a confirmed instrumental")
                    return 2, song_name, song_artist, "", "", coverart

                url = "https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"
                querystring = {"id": str(genius_id), "text_format": "html"}
                headers = {
                    "x-rapidapi-key": str(key),
                    "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
                }
                response = requests.get(url, headers=headers, params=querystring)
                
                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code}")
                    print(f"Response Content: {response.text}")
                    return 0, "", "", "", "", ""

                ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

                if "lyrics" in ax:
                    print("IN____________________ LYRICS FOUND")
                    lyric_check = ax['lyrics']['lyrics']['body']['html']
                    if lyric_check:
                        if not isinstance(lyric_check, str):
                            lyric_check = str(lyric_check)
                        ret_val = lyric_check
                        soup = BeautifulSoup(lyric_check, features="html.parser", from_encoding='utf-8')
                        ret_val = soup.get_text()
                        ret_val = ret_val.encode('utf-8') 
                        ret_val = ret_val.decode('utf-8')
                        ret_val = ret_val.replace('�', '')
                        print(f"###################RET_VAL********************** ====", {ret_val})
                        print(f"################################LYRIC_CHECK", {lyric_check})
                        
                        from trans import detect
                        co, la = detect(ret_val[:130])
                        if co == "MUL":
                            return 4, song_name, song_artist, la, ret_val, coverart
                        return 3, song_name, song_artist, la, ret_val, coverart
                    return 1, song_name, song_artist, "", "", coverart

                print('Error: cant find track___________________lyrics')
                return 1, song_name, song_artist, "", "", coverart

            ax = return_lyrics_MM(song_name, song_artist)
            if ax != 'fail':
                print("IN____________________ LYRICS FOUND")
                ret_val = str(ax)
                from trans import detect
                co, la = detect(ret_val[:130])
                if co == "MUL":
                    return 4, song_name, song_artist, la, ret_val, coverart
                return 3, song_name, song_artist, la, ret_val, coverart

            print('Error: cant find track___________________Id')
            print("Songs lyrics have not been located on the API/not recorded or song is likely an instrumental")
            return 1, song_name, song_artist, "", "", coverart

        else:
            print('Error: cant find track___________________at all')
            return 0, "", "", "", "", ""

    except Exception as e:
        print(f"Error in run_apis: {e}")
        return 0, "", "", "", "", ""

    # Default return if no condition above matches
    return 0, "", "", "", "", ""
    
    

        
# def run_apis(full_title):
#     genius_id = 0
#     url = "https://shazam.p.rapidapi.com/songs/v2/detect"
#     querystring = {"timezone": "America/Chicago", "locale": "en-US"}
#     payload = full_title
#     # payload = read_audio_file(full_title)
#     payload = full_title
#     headers = {
#         "x-rapidapi-key": key,
#         "x-rapidapi-host": "shazam.p.rapidapi.com",
#         "Content-Type": "text/plain"
#     }

#     response = requests.post(url, data=payload, headers=headers, params=querystring, timeout=10)
#     ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

#     if response.status_code == 200 and "track" in ax:
#         print("IN____________________ SONG FOUND")
#         song_name = ax['track']['title']
#         song_artist = ax['track']['subtitle']
        
#         print(f'Title Name: {song_name}')
#         print(f'Artist: {song_artist}')
#         full_title = song_name + " " + song_artist
#         print(full_title)
        
#         if 'images' in ax['track']:
#             coverart = ax['track']['images']['coverart']
#         else:
#             coverart = "fail"
        
#         ax = return_lyrics(song_name, song_artist)
        
#         if response.status_code == 200 and "hits" in ax:
#             print("IN____________________ ID FOUND")
#             genius_id = ax['hits'][0]['result']['id']
#             print(f'Genius ID: {genius_id}')
            
#             if ax['hits'][0]['result']['instrumental']:
#                 print("This song is a confirmed instrumental")
#                 return 2, song_name, song_artist, "", "", coverart

#             url = "https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"
#             querystring = {"id": str(genius_id), "text_format": "html"}
#             headers = {
#                 "x-rapidapi-key": str(key),
#                 "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
#             }
#             response = requests.get(url, headers=headers, params=querystring)
#             ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

#             if response.status_code == 200 and "lyrics" in ax:
#                 print("IN____________________ LYRICS FOUND")
#                 lyric_check = ax['lyrics']['lyrics']['body']['html']
#                 if lyric_check:
#                     if not isinstance(lyric_check, str):
#                         lyric_check = str(lyric_check)
#                     ret_val = lyric_check
#                     soup = BeautifulSoup(lyric_check, features="html.parser")
#                     ret_val = soup.get_text()
#                     from trans import detect, translate
#                     co, la = detect(ret_val[:130])
#                     if co == "MUL":
#                         return 4, song_name, song_artist, la, ret_val, coverart
#                     return 3, song_name, song_artist, la, ret_val, coverart
#                 return 1, song_name, song_artist, "", "", coverart
#             elif response.status_code == 200:
#                 print('Error: cant find track___________________lyrics')
#                 return 1, song_name, song_artist, "", "", coverart

#         ax = return_lyrics_MM(song_name, song_artist)
#         if ax != 'fail':
#             print("IN____________________ LYRICS FOUND")
#             ret_val = str(ax)
#             from trans import detect
#             co, la = detect(ret_val[:130])
#             if co == "MUL":
#                 print(co)
#                 return 4, song_name, song_artist, la, ret_val, coverart
#             return 3, song_name, song_artist, la, ret_val, coverart

#         elif response.status_code == 200:
#             print('Error: cant find track___________________Id')
#             print("Songs lyrics have not been located on the API/not recorded or song is likely an instrumental")
#             return 1, song_name, song_artist, "", "", coverart
    
#     elif response.status_code == 200:
#         print('Error: cant find track___________________at all')
#         return 0, "", "", "", "", ""

def return_lyrics(s_name, s_artist):
	# Try s_name and one artist if possible only
    print("RUN 1")
    if "," in s_artist: 
        if "-" in s_name:
            url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
            querystring = {"q": str(s_name.split("-")[0].strip() + " " + s_artist.split(",")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and ax["hits"] and \
                (ax['hits'][0]['result']['artist_names'] in s_artist.split(",")[0].strip() or 
                 s_artist.split(",")[0].strip() in ax['hits'][0]['result']['artist_names']):

                print("NO ,: " + s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip())
                return ax
        if "(" in s_name:
            url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
            querystring = {"q": str(s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and ax["hits"] and \
                (ax['hits'][0]['result']['artist_names'] in s_artist.split(",")[0].strip() or 
                 s_artist.split(",")[0].strip() in ax['hits'][0]['result']['artist_names']):

                print("NO ,: " + s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip())
                return ax
        if "(" not in s_name and "-" not in s_name:
            url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
            querystring = {"q": str(s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
			# print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and ax["hits"] and \
                (ax['hits'][0]['result']['artist_names'] in s_artist.split(",")[0].strip() or 
                 s_artist.split(",")[0].strip() in ax['hits'][0]['result']['artist_names']):
                print("NO , and clean s_name: " + s_name + " " + s_artist.split(",")[0].strip())
                return ax
    if "&" in s_artist:
        if "-" in s_name:
            url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
            querystring = {"q": str(s_name.split("-")[0].strip() + " " + s_artist.split("&")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and ax["hits"] and \
                (ax['hits'][0]['result']['artist_names'] in s_artist.split("&")[0].strip() or
                 s_artist.split("&")[0].strip() in ax['hits'][0]['result']['artist_names']):

                print("NO &: " + s_name.split("-")[0].strip() + " " + s_artist.split("&")[0].strip())
                return ax
        if "(" in s_name:
            url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
            querystring = {"q": str(s_name.split("(")[0].strip() + " " + s_artist.split("&")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and ax["hits"] and \
            (ax['hits'][0]['result']['artist_names'] in s_artist.split("&")[0].strip() or 
             s_artist.split("&")[0].strip() in ax['hits'][0]['result']['artist_names']):
                
                print("NO &: " + s_name.split("(")[0].strip() + " " + s_artist.split("&")[0].strip())
                return ax
        if "(" not in s_name and "-" not in s_name:
            url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
            querystring = {"q": str(s_name + " " + s_artist.split("&")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and ax["hits"] and \
                (ax['hits'][0]['result']['artist_names'] in s_artist.split("&")[0].strip() or 
                 s_artist.split("&")[0].strip() in ax['hits'][0]['result']['artist_names']):

                print("NO & and clean s_name: " + s_name + " " + s_artist.split("&")[0].strip())
                return ax





    print("RUN 2")
    # Try artist and song name together
    print(str(s_name + " " + s_artist))
    url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
    querystring = {"q": str(s_name + " " + s_artist), "per_page": "1", "page": "1", "text_format": "String"}
    headers = {
        "x-rapidapi-key": str(key),
        "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    # print(response.text)
    ax = json.loads(response.text.encode('utf-8').decode('utf-8'))
    if response.status_code == 200 and ax["hits"] and \
        (ax['hits'][0]['result']['artist_names'].casefold() in s_artist.casefold() or 
         s_artist.casefold() in ax['hits'][0]['result']['artist_names'].casefold() or
         (s_artist.casefold() in ax['hits'][0]['result']['full_title'].casefold() and \
          s_name.casefold() in ax['hits'][0]['result']['full_title'].casefold())):
        print("STANDARD PROCEDURE")
        return ax




    print("RUN 3")
    # Try formatted s_name
    url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
    querystring = {"q": str(s_name.split("(")[0].strip() + " " + s_artist), "per_page": "1", "page": "1", "text_format": "String"}
    headers = {
        "x-rapidapi-key": str(key),
        "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    # print(response.text)
    ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

    if response.status_code == 200 and ax["hits"] and \
        (ax['hits'][0]['result']['artist_names'].casefold() in s_artist.casefold() or 
         s_artist.casefold() in ax['hits'][0]['result']['artist_names'].casefold() or
         (s_artist.casefold() in ax['hits'][0]['result']['full_title'].casefold() and \
          s_name.split("(")[0].strip().casefold() in ax['hits'][0]['result']['full_title'].casefold())):
        return ax


    print("RUN 4")
	#LAST RESORT, STRIP SNAME ONLY
    url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
    querystring = {"q": str(s_name.split("(")[0].strip()), "per_page": "1", "page": "1", "text_format": "String"}
    headers = {
        "x-rapidapi-key": str(key),
        "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    # print(response.text)
    ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

    if response.status_code == 200 and ax["hits"] and \
        (ax['hits'][0]['result']['artist_names'].casefold() in s_artist.casefold() or 
         s_artist.casefold() in ax['hits'][0]['result']['artist_names'].casefold() or
         (s_artist.casefold() in ax['hits'][0]['result']['full_title'].casefold() and \
          s_name.split("(")[0].strip().casefold() in ax['hits'][0]['result']['full_title'].casefold())):
        
        print("LAST RESORT: " + s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip())
        return ax

    return []

def return_lyrics_MM(s_name, s_artist):
	# Try s_name and one artist if possible only
    print("RUN 1")
    if "," in s_artist: 
        if "-" in s_name:
            url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
            querystring = {"t": str(s_name.split("-")[0].strip()),"a":str(s_artist.split(",")[0].strip()),"type":"json"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and 'error' not in ax and ax:
                print("NO ,: " + s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip())
                return extract_text_with_newlines(ax)
        if "(" in s_name:
            url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
            querystring = {"t": str(s_name.split("(")[0].strip()),"a":str(s_artist.split(",")[0].strip()),"type":"json"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and 'error' not in ax and ax:

                print("NO ,: " + s_name.split("(")[0].strip() + " " + s_artist.split(",")[0].strip())
                return extract_text_with_newlines(ax)
        if "(" not in s_name and "-" not in s_name:
            url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
            querystring = {"t": str(s_name),"a":str(s_artist.split(",")[0].strip()),"type":"json"}

            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
			# print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and 'error' not in ax and ax:
                print("NO , and clean s_name: " + s_name + " " + s_artist.split(",")[0].strip())
                return extract_text_with_newlines(ax)
    if "&" in s_artist:
        if "-" in s_name:
            url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
            querystring = {"t": str(s_name.split("-")[0].strip()),"a":str(s_artist.split("&")[0].strip()),"type":"json"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and 'error' not in ax and ax:
                print("NO &: " + s_name.split("-")[0].strip() + " " + s_artist.split("&")[0].strip())
                return extract_text_with_newlines(ax)
        if "(" in s_name:
            url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
            querystring = {"t": str(s_name.split("(")[0].strip()),"a":str(s_artist.split("&")[0].strip()),"type":"json"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and 'error' not in ax and ax:  
                print("NO &: " + s_name.split("(")[0].strip() + " " + s_artist.split("&")[0].strip())
                return extract_text_with_newlines(ax)
        if "(" not in s_name and "-" not in s_name:
            url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
            querystring = {"t": str(s_name),"a":str(s_artist.split("&")[0].strip()),"type":"json"}
            headers = {
				"x-rapidapi-key": str(key),
				"x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
			}
            response = requests.get(url, headers=headers, params=querystring)
            print(response.json())
            # print(response.text)
            ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

            if response.status_code == 200 and 'error' not in ax and ax:
                print("NO & and clean s_name: " + s_name + " " + s_artist.split("&")[0].strip())
                return extract_text_with_newlines(ax)


    print("RUN 2")
    # Try artist and song name together
    url = "https://musixmatch-lyrics-songs.p.rapidapi.com/songs/lyrics"
    querystring = {"t": str(s_name),"a":str(s_artist),"type":"json"}

    headers = {
        "x-rapidapi-key": str(key),
        "x-rapidapi-host": "musixmatch-lyrics-songs.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print("TRYING!")
    if response.status_code == 200:
        try:
            ax = response.json()  
            if 'error' not in ax and ax:
                print("STANDARD PROCEDURE")
                return extract_text_with_newlines(ax)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Response text was: {response.text}")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(f"Response text: {response.text}")
        return 'fail'

    print("MM also failed-------------------------- Got nothing")
    return 'fail'

def extract_text_with_newlines(data):
    multi_line_text = ""

    for item in data:
        text = item.get("text", "")
        multi_line_text += text + "\n"

    return multi_line_text
		
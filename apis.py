# import http.client

# conn = http.client.HTTPSConnection("shazam.p.rapidapi.com")

# with open('audio_stream/audio.wav', 'rb') as payload:
#     headers = {
#         'x-rapidapi-key': "8e1539527bmsh23f03950fb773c9p19b7b6jsnfd6fee6382de",
#         'x-rapidapi-host': "shazam.p.rapidapi.com",
#         'Content-Type': "audio/wav"
#     }
    
#     # Make the request
#     conn.request("POST", "/songs/v2/detect?timezone=America%2FChicago&locale=en-US", payload, headers)

#     # Get the response
#     res = conn.getresponse()
    
#     # Read the data
#     data = res.read()

#     # Print the response data
#     print(data)

#     # Decode the response data
#     testme = data.decode("utf-8")
#     print(testme)

# # Close the connection
# conn.close()
import time
import os
import glob
import requests
import base64
import json
import sys
import io

coverart = ""
full_title = ""
# Set encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

key = os.environ.get('SHAZ_API_KEY')
def read_audio_file(file_path):
		with open(file_path, 'rb') as audio_file:
			return base64.b64encode(audio_file.read()).decode('utf-8')
		
def run_apis_1():
	key = os.environ.get('SHAZ_API_KEY')
	
	files = glob.glob('audio_stream/clips/*')
	genius_id = 0
	for f in range(len(files)):

		url = "https://shazam.p.rapidapi.com/songs/v2/detect"
		querystring = {"timezone":"America/Chicago","locale":"en-US"}
		payload = read_audio_file(f"audio_stream/clips/clip_{f + 1}.wav")
		# payload = read_audio_file(f"audio_stream/clips/clip_1.wav")
		# payload = read_audio_file("audio_stream/ex.wav")
		# payload = open('audio_stream/clinteastwood_portion_mono.txt', 'rb')
		headers = {
			"x-rapidapi-key": key,
			"x-rapidapi-host": "shazam.p.rapidapi.com",
			"Content-Type": "text/plain"
		}

		response = requests.post(url, data=payload, headers=headers, params=querystring)
		print(response.json())
		print(response.text)
		ax = json.loads(response.text)

		#Song ID'd
		if response.status_code == 200 and "track" in ax:
			print("IN____________________ SONG FOUND")
			song_name = ax['track']['title']
			song_artist = ax['track']['subtitle']
			print(f'Title Name: {song_name}')
			print(f'Artist: {song_artist}')
			full_title = song_name + " " + song_artist
			print(full_title)
			coverart = ax['track']['images']['coverart']



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
			if response.status_code == 200 and ax["hits"]:
					print("IN____________________ ID FOUND")
					genius_id = ax['hits'][0]['result']['id']
					print(f'Genius ID: {genius_id}')
					
					if ax['hits'][0]['result']['instrumental']:
						print("This song is a confirmed instrumental")
						break



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
							
							print('Lyrics_after wrapper: \n\n')
							print(lyric_check)
							from bs4 import BeautifulSoup
							soup = BeautifulSoup(lyric_check, features="html.parser")
							s_txt = soup.get_text()
							print('\n\n s_txt Lyrics: \n\n')
							print(s_txt)
							break
					elif response.status_code == 200:
						print('Error: cant find track___________________lyrics' )
						break

			elif response.status_code == 200:
				print('Error: cant find track___________________Id' )
				print("Songs lyrics have not been located on the API/not recorded or song is likely an instrumental")
				break
		
		elif response.status_code == 200:
			print('Error: cant find track___________________at all' )
			time.sleep(1.1)
		# full_title = "Bye Bye Bye *NSYNC"

	


# full_title = ""

# key = os.environ.get('SHAZ_API_KEY')

# files = glob.glob('audio_stream/clips/*')
# genius_id = 0
# for f in range(len(files)):
# 	url = "https://shazam.p.rapidapi.com/songs/v2/detect"

# 	querystring = {"timezone":"America/Chicago","locale":"en-US"}
# 	# from splitter import wav_to_base64
# 	payload = read_audio_file(f"audio_stream/clips/clip_{f + 1}.wav")
# 	# payload = read_audio_file(f"audio_stream/clips/clip_1.wav")
# 	# payload = read_audio_file("audio_stream/ex.wav")
# 	# payload = open('audio_stream/clinteastwood_portion_mono.txt', 'rb')
# 	headers = {
# 		"x-rapidapi-key": key,
# 		"x-rapidapi-host": "shazam.p.rapidapi.com",
# 		"Content-Type": "text/plain"
# 	}

# 	response = requests.post(url, data=payload, headers=headers, params=querystring)
# 	# print(response.json())
# 	# print(response.text)
# 	ax = json.loads(response.text)

# 	#Song ID'd
# 	if response.status_code == 200 and "track" in ax:
# 		print("IN____________________ SONG FOUND")
# 		song_name = ax['track']['title']
# 		song_artist = ax['track']['subtitle']
# 		print(f'Title Name: {song_name}')
# 		print(f'Artist: {song_artist}')
# 		full_title = song_name + " " + song_artist
# 		print(full_title)
		
# 		url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
# 		querystring = {"q":str(full_title),"per_page":"1","page":"1", "text_format":"String"}
# 		headers = {
# 			"x-rapidapi-key": str(key),
# 			"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
# 		}
# 		response = requests.get(url, headers=headers, params=querystring)
# 		print(response.json())
# 		print(response.text)
# 		ax = json.loads(response.text)
# 		#look up song name for ID
# 		if response.status_code == 200 and ax['hits']:
# 				print("IN____________________ ID FOUND")
# 				genius_id = ax['hits'][0]['result']['id']
# 				print(f'Genius ID: {genius_id}')
# 				# break

# 				url = "https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"
# 				# genius_id = 115478
# 				querystring = {"id":str(genius_id), "text_format":"html"}
# 				headers = {
# 					"x-rapidapi-key": str(key),
# 					"x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
# 				}
# 				response = requests.get(url, headers=headers, params=querystring)
# 				print(response.text)
# 				ax = json.loads(response.text)
# 				#Return Song Lyrics
# 				if response.status_code == 200 and "lyrics" in ax:
# 						print("IN____________________ LYRICS FOUND")
# 						print('Lyrics: \n\n')
# 						lyric_check = ax['lyrics']['lyrics']['body']['html']	
# 						if lyric_check:
# 							if not isinstance(lyric_check, str):lyric_check = str(lyric_check)
# 							import sys
# 							import io
# 							# Set encoding for stdout
# 							sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 							print('Lyrics_after wrapper: \n\n')
# 							print(lyric_check)
# 							from bs4 import BeautifulSoup
# 							soup = BeautifulSoup(lyric_check, features="html.parser")
# 							s_txt = soup.get_text()
# 							print('\n\n s_txt Lyrics: \n\n')
# 							print(s_txt)
# 							break
# 						else:
# 							print("Cool song, however there are no lyrics for this cool tune")
# 				elif response.status_code == 200:
# 					print('Error: cant find track___________________lyrics' )

# 		elif response.status_code == 200:
# 			print('Error: cant find track___________________Id' )
	
# 	elif response.status_code == 200:
# 		print('Error: cant find track___________________at all' )
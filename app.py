from flask import Flask, jsonify, render_template, url_for, redirect, request, session, make_response
import trans
import redis
import os
from apis import run_apis
import boto3
from urllib.parse import urlparse
import uuid
import json

redis_url = urlparse(os.getenv("REDIS_URL"))

redis_client = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password, ssl=(redis_url.scheme == "rediss"), ssl_cert_reqs=None)

# Configure AWS S3
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

# Create S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

db = []
app = Flask(__name__)
app.secret_key = os.getenv('sec_key')
nkey = os.getenv('key_n')

@app.before_request
def set_user_identifier():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        request.environ['new_user_cookie'] = user_id  # Pass the user_id in the request object
        print(f"New user ID generated: {user_id}")
    else:
        print(f"Existing user ID: {user_id}")

@app.get('/')
def index():
    # Check if a new cookie needs to be set
    new_user_id = request.environ.get('new_user_cookie')
    if new_user_id:
        resp = make_response(render_template('index.html'))
        resp.set_cookie('user_id', new_user_id)
        return resp

    return render_template('index.html')

@app.get('/search')
def search():
    query = request.args.get('query', '')  # Get query parameter from the request
    try:
        import requests
        url = "https://genius-song-lyrics1.p.rapidapi.com/search/"
        querystring = {"q":f"{query}","per_page":"15","page":"1"}
        headers = {
            "x-rapidapi-key": f"{nkey}",
            "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)

        data = json.loads(response.text)  # Replace this with your actual data source
        hits = data.get("hits", [])
        
        filtered_songs = []
        for hit in hits:
            result = hit.get("result", {})
            #no point displaying songs that have no lyrics
            if result.get("lyrics_state") == "complete" and not result.get("instrumental", True):
                full_title = result.get("full_title", "")
                if "by" in full_title:
                    song_name, artist_names = full_title.split("by", 1)
                    song_name = song_name.strip()
                    artist_names = artist_names.strip()
                    
                    # Filter based on the search query, ensure we show relevant sonds
                    if query.lower() in song_name.lower() or query.lower() in artist_names.lower():
                        filtered_songs.append({
                            "song_name": song_name,
                            "artist_names": artist_names,
                            "full_title": full_title,
                            "header_image_url": result.get("header_image_url"),
                            "id": result.get("id"),
                        })
        for song in filtered_songs:
            print(song)
        return jsonify(filtered_songs) 
    
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return jsonify({"error": f"Error processing JSON data: {e}"}), 500


@app.get('/searched')
def searched():
    song_data = request.args.get('song', '{}')  # Get the JSON string
    try:
        import requests
        from bs4 import BeautifulSoup
        song = json.loads(song_data)  # Parse JSON string to a dictionary


        
        url = "https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"
        querystring = {"id": str(song["id"]), "text_format": "html"}
        headers = {
            "x-rapidapi-key": str(nkey),
            "x-rapidapi-host": "genius-song-lyrics1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        ax = json.loads(response.text.encode('utf-8').decode('utf-8'))

        if response.status_code == 200 and "lyrics" in ax:
            print("IN____________________ LYRICS FOUND")
            lyric_check = ax['lyrics']['lyrics']['body']['html']
            if lyric_check:
                if not isinstance(lyric_check, str):
                    lyric_check = str(lyric_check)
                ret_val = lyric_check
                soup = BeautifulSoup(lyric_check, features="html.parser")
                ret_val = soup.get_text()
                from trans import detect, translate
                co, la = detect(ret_val[:130])
                if co == "MUL":
                    complete = {
                                'code': "",
                                'songName': song["song_name"],
                                'artistName': song["artist_names"],
                                'songLang': "",
                                'songLyric': "",
                                'albumCover': song["header_image_url"]
                                }
                    return render_template('song_details.html', song=complete)
        complete = {
            'code': "",
            'songName': song["song_name"],
            'artistName': song["artist_names"],
            'songLang': "",
            'songLyric': "",
            'albumCover': song["header_image_url"]
        }
        # song_key = f"song:{uuid.uuid4().hex}"  # Unique identifier for the song

        # # Store the song data in Redis
        # redis_client.set(song_key, json.dumps(song_data))

        return render_template('song_details.html', song=complete)
    except json.JSONDecodeError:
        return "Error: Invalid song data", 400


def add_to_history(user_id, song_data, song_key):
    key = f"user:{user_id}"  # Key for Redis
    existing_history = redis_client.get(key)  # Get existing history
    
    # Parse existing history or initialize an empty list if not found
    history = json.loads(existing_history) if existing_history else [] 
    
    # Include the song_key along with the song_data
    song_data_with_key = song_data.copy()  # Create a copy of song_data
    song_data_with_key['song_key'] = song_key  # Add the song_key to the data
    
    # Append the song data (now with the song_key) to the history
    history.append(song_data_with_key)
    
    # Save updated history back to Redis
    redis_client.set(key, json.dumps(history))
    
    print(f"History updated for user {user_id}: {history}")

@app.get('/history')
def history():
    user_id = request.cookies.get('user_id')
    history = redis_client.get(f"user:{user_id}")
    song_history = json.loads(history) if history else []
    return render_template('history.html', song_history=song_history)

@app.post('/clear_history')
def clear_history():
    user_id = request.cookies.get('user_id')
    redis_client.delete(f"user:{user_id}")
    return redirect(url_for('history'))

@app.get('/redistest')
def redis_test():
    message = redis_client.get('my_message')
    message = message.decode('utf-8') if message else "No message found."
    return render_template('redistest.html', message=message)

@app.get('/about')
def about():
    return render_template('about.html')

@app.get('/detected')
def detected():
    user_id = request.cookies.get('user_id')  # Retrieve user_id from cookies
    if not user_id:
        return "User ID not found!", 400  # Handle missing user ID
    
    song_key = request.args.get('key')
    if song_key == 0 or song_key == "0":
        return render_template(
            'detected.html',
            code=0,
            songName="",
            artistName="",
            songLang="",
            songLyric="",
            albumCover="",
            song_key=""  # Pass the song_key to the template
        )
    print(f"Received song key: {song_key}")
  
    if not song_key:
        return jsonify({"error": "Missing or invalid key"}), 400

    try:
        song_data_json = redis_client.get(song_key)
        print(f"Song data retrieved: {song_data_json}")

        if not song_data_json:
            return jsonify({"error": "No data found for the provided key"}), 404

        song_data = json.loads(song_data_json)

        add_to_history(user_id=user_id, song_data=song_data, song_key=song_key)


        # Pass the song data and song_key to the template
        return render_template(
            'detected.html',
            code=song_data['code'],
            songName=song_data['songName'],
            artistName=song_data['artistName'],
            songLang=song_data['songLang'],
            songLyric=song_data['songLyric'],
            albumCover=song_data['albumCover'],
            song_key=song_key  # Pass the song_key to the template
        )
    except Exception as e:
        print(f"Error retrieving or rendering song data: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.get('/translations')
def translations():
    song_key = request.args.get('key')
    print(f"Received song key: {song_key}")
    
    if not song_key:
        return jsonify({"error": "Missing or invalid key"}), 400


    try:
        # Retrieve song data from Redis
        song_data_json = redis_client.get(song_key)
        print(f"Song data retrieved: {song_data_json}")

        if not song_data_json:
            return jsonify({"error": "No data found for the provided key"}), 404
        song_data = json.loads(song_data_json)
        print(f"Song data: {song_data}")

        # Pass the retrieved data to the template
        return render_template(
            'translation.html',
            name=song_data['songName'],
            art=song_data['artistName'],
            lang=song_data['songLang'],
            lyric=song_data['songLyric'],
            ca=song_data['albumCover'],
            ldict=trans.languages_dict 
        )
    except Exception as e:
        print(f"Error retrieving or rendering song data: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.post('/translate')
def translate():
    data = request.get_json()
    text = data.get('text')
    lang = data.get('lang')

    translated_text = trans.translate(text=text, lang=lang) 

    return jsonify({'translatedText': translated_text})

@app.post('/upload-audio')
def upload_audio():

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files['audio']
    file_name = audio_file.filename
    s3_path = f"audio/{file_name}"

    try:
        # Upload the audio file to S3
        s3_client.upload_fileobj(audio_file, S3_BUCKET, s3_path)
        print(f"Audio file uploaded to S3: {s3_path}")
        # Process the audio file and retrieve song metadata
        result = run_apis(S3_BUCKET, s3_path)
        print(f"run_apis returned: {result}")

        if result is None:
            return jsonify({"error": "run_apis returned None"}), 500


        code, song_name, song_artist, la, ret_val, coverart = result


        

        # Prepare song data for Redis
        song_data = {
            'code': code,
            'songName': song_name,
            'artistName': song_artist,
            'songLang': la,
            'songLyric': ret_val,
            'albumCover': coverart
        } 

        if code == 0:
            return jsonify({"endLoop": False, "code":code}), 400

        # Generate a unique key for storing the song data in Redis
        song_key = f"song:{uuid.uuid4().hex}"  # Unique identifier for the song

        # Store the song data in Redis
        redis_client.set(song_key, json.dumps(song_data))

        # Respond with the song key and endLoop flag
        return jsonify({
            "endLoop": True,  # This will signal the front-end to stop the loop
            "key": song_key   # Return the song key so the client can use it in the redirect
        })

    except Exception as e:
        print(f"Error uploading or processing file: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.get('/lyrics')
def lyrics():
    song_key = request.args.get('song_key')  # Retrieve the song_key from the URL
    user_id = request.cookies.get('user_id')  # Get the user_id from cookies
    
    # Get the user's song history from Redis
    history = redis_client.get(f"user:{user_id}")
    song_history = json.loads(history) if history else []
    
    # Find the song data based on the song_key
    song_data = next((song for song in song_history if song['song_key'] == song_key), None)
    
    if song_data:
        # Extract the song data
        songName = song_data['songName']
        artistName = song_data['artistName']
        songLang = song_data['songLang']
        songLyric = song_data['songLyric']
        albumCover = song_data['albumCover']
        
        # Render the template with the unpacked song data
        return render_template('lyrics.html', songName=songName, artistName=artistName, 
                               songLang=songLang, songLyric=songLyric, albumCover=albumCover)
    else:
        # If no song is found with the given song_key, you can handle it accordingly
        return "Song not found", 404








from flask import Flask, jsonify, render_template, url_for, redirect, request, session
import requests
import trans
import redis
import os
from apis import run_apis
import boto3
import unicodedata
import re
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

def db_check(code, val):
    if db.__contains__(val):
        x = db.pop(db.index(val))
        db.append(x)
    else:
        if code != 0:
            db.append(val)

@app.route('/redistest')
def redis_test():
    message = redis_client.get('my_message')
    message = message.decode('utf-8') if message else "No message found."
    return render_template('redistest.html', message=message)

@app.route('/')
def index():
    try:
        redis_client.ping()
        print("Redis connection is healthy!")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
    
    return render_template('index.html')

@app.route('/history', methods=['get'])
def history():
    return render_template('history.html', red=db)

@app.get('/about')
def about():
    return render_template('about.html')


@app.route('/detected')
def detected():
    song_key = request.args.get('key')
    print(f"Received song key: {song_key}")
  
    if not song_key:
        return jsonify({"error": "Missing or invalid key"}), 400

    try:
        song_data_json = redis_client.get(song_key)
        print(f"Song data retrieved: {song_data_json}")

        if not song_data_json:
            return jsonify({"error": "No data found for the provided key"}), 404

        song_data = json.loads(song_data_json)


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


        if code == 0:
            return jsonify({"message": "Unable to process audio file"}), 400

        # Prepare song data for Redis
        song_data = {
            'code': code,
            'songName': song_name,
            'artistName': song_artist,
            'songLang': la,
            'songLyric': ret_val,
            'albumCover': coverart
        }

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
    
#unused code
# @app.route('/translations', methods=['GET'])
# def from_history():
#     name = request.args.get('songName')
#     art =  request.args.get('artistName')
#     lyric =  request.args.get('songLyric')
#     lang =  request.args.get('songLang')
#     ca =  request.args.get('albumCover')
#     return render_template('translation.html', name=name, art=art, lang=lang, lyric=lyric, ca=ca, ldict=trans.languages_dict)

# @app.route('/lyrics')
# def lyrics():
#     songName = request.args.get('songName')
#     artistName = request.args.get('artistName')
#     songLang = request.args.get('songLang')
#     songLyric = request.args.get('songLyric')
#     albumCover = request.args.get('albumCover')
#     return render_template('lyrics.html', songName=songName, artistName=artistName, songLang=songLang, songLyric=songLyric, albumCover=albumCover)


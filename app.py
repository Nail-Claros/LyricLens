from flask import Flask, render_template, url_for, redirect, request
import requests
import redis
import os

# redis_url = os.getenv('REDIS_URL')
key = os.getenv('SHAZ_API_KEY')

app = Flask(__name__)

db = []
def db_check(val):
    if db.__contains__(val):
        x = db.pop(db.index(val))
        db.append(x)
    else:
        db.append(val)
# redis db
# r = redis.Redis(host='redis', port=6379)
# r = redis.from_url(redis_url)


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/detected')
def detected():
    code = request.args.get('code')
    songName = request.args.get('name')
    artistName = request.args.get('artist')
    songLang = request.args.get('lang')
    songLyric = request.args.get('lyric')
    albumCover = request.args.get('ca')
    code = int(code)
    return render_template('detected.html',code=code, songName=songName, artistName=artistName, songLang=songLang, songLyric=songLyric, albumCover=albumCover)

@app.route('/translation', methods=['POST'])
def translations():
    name = request.form.get('songName')
    art = request.form.get('artistName')
    lyric = request.form.get('songLyric')
    lang = request.form.get('songLang')
    ca = request.form.get('albumCover')
    return render_template('translation.html', name=name, art=art, lang=lang, lyric=lyric, ca=ca)

@app.route('/history', methods=['get'])
def history():
    return render_template('history.html', red=db)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/run_listener', methods=['POST'])
def run_listener():
    from listener import run
    name = ""
    code = 0
    code, name, art, lang, lyric, ca = run()
    db_check([name, art, lang, lyric, ca])
    return redirect(url_for('detected', code=code, name=name, artist=art, lang=lang, lyric=lyric, ca=ca))

from flask import Flask, jsonify, render_template, url_for, redirect, request, session
import requests
import trans
import redis
import os

# redis_url = os.getenv('REDIS_URL')
key = os.getenv('SHAZ_API_KEY')
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
# redis db
# r = redis.Redis(host='redis', port=6379)
# r = redis.from_url(redis_url)


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/detected')
def detected():
    code = int(request.args.get('code'))
    songName = request.args.get('name')
    artistName = request.args.get('artist')
    songLang = request.args.get('lang')
    songLyric = request.args.get('lyric')
    albumCover = request.args.get('ca')
    
    session['songName'] = songName
    session['artistName'] = artistName
    session['songLyric'] = songLyric
    session['songLang'] = songLang
    session['albumCover'] = albumCover
    return render_template('detected.html',code=code, songName=songName, artistName=artistName, songLang=songLang, songLyric=songLyric, albumCover=albumCover)

@app.route('/translation')
def translations():
    name = session.get('songName')
    art = session.get('artistName')
    lyric = session.get('songLyric')
    lang = session.get('songLang')
    ca = session.get('albumCover')
    # name = request.args.get('songName')
    # art =  request.args.get('artistName')
    # lyric =  request.args.get('songLyric')
    # lang =  request.args.get('songLang')
    # ca =  request.args.get('albumCover')
    if lyric != "" and lyric != None and lang != "Made up Language/gibberish" and lang != "" and lang != None:
        return render_template('translation.html', name=name, art=art, lang=lang, lyric=lyric, ca=ca, ldict=trans.languages_dict)
    else:
        return redirect('/')
    
@app.route('/translations', methods=['GET'])
def from_history():
    name = request.args.get('songName')
    art =  request.args.get('artistName')
    lyric =  request.args.get('songLyric')
    lang =  request.args.get('songLang')
    ca =  request.args.get('albumCover')
    return render_template('translation.html', name=name, art=art, lang=lang, lyric=lyric, ca=ca, ldict=trans.languages_dict)


@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    lang = data.get('lang')

    translated_text = trans.translate(text=text, lang=lang) 

    return jsonify({'translatedText': translated_text})

@app.route('/history', methods=['get'])
def history():
    return render_template('history.html', red=db)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/lyrics')
def lyrics():
    songName = request.args.get('songName')
    artistName = request.args.get('artistName')
    songLang = request.args.get('songLang')
    songLyric = request.args.get('songLyric')
    albumCover = request.args.get('albumCover')
    return render_template('lyrics.html', songName=songName, artistName=artistName, songLang=songLang, songLyric=songLyric, albumCover=albumCover)

@app.route('/run_listener', methods=['POST'])
def run_listener():
    from listener import run
    name = ""
    code = 0
    code, name, art, lang, lyric, ca = run()
    db_check(code, [name, art, lang, lyric, ca])
    
    return redirect(url_for('detected', code=code, name=name, artist=art, lang=lang, lyric=lyric, ca=ca))

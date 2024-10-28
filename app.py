from flask import Flask, render_template, url_for, redirect, request
import requests
import redis
import os


key = os.getenv('SHAZ_API_KEY')

redis_url = os.getenv('REDIS_URL')

redis_client = redis.Redis.from_url(redis_url)

app = Flask(__name__)

db = []
def db_check(val):
    if db.__contains__(val):
        x = db.pop(db.index(val))
        db.append(x)
    else:
        db.append(val)

@app.route('/redistest')
def redis_test():
    message = redis_client.get('my_message')
    message = message.decode('utf-8') if message else "No message found."
    return render_template('redistest.html', message=message)

#store a message for testing purposes
@app.route('/store_message')
def store_message():
    redis_client.flushall()
    message = "Hello, this is a CAM!"
    redis_client.set('my_message', message)
    return "Message stored in Redis!"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translation', methods=['get'])
def translations():
    name = request.args.get('name')
    art = request.args.get('artist')
    lang = request.args.get('lang')
    lyric = request.args.get('lyric')
    ca = request.args.get('ca')
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
    if code == 0:
        return redirect('/')
    else:
        db_check([name, art, lang, lyric, ca])
        return redirect(url_for('detected', name=name, artist=art, lang=lang, lyric=lyric, ca=ca))

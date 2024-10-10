from flask import Flask, render_template, request, redirect, url_for
import subprocess
import pathlib
import os
import redis
# from apis import testme

spot_api = os.getenv('shaz_api')

# song_obs = []
##song obs will have 4 things
#song name
#genius id (if any)
#artist
#lyrics (html, if any)
#native_lang (if any)

app = Flask(__name__)

r = redis.Redis(host='redis', port=6379)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/history', methods=['get'])
def history():
    return render_template('history.html')

@app.route('/run_listener', methods=['POST'])
def run_listener():
    try:
        subprocess.run(['py', 'listener.py'], check=True)
        return redirect(url_for('index'))  # Redirect back to the home page after the script is executed
    except Exception as e:
        return redirect(url_for('hello_world'))
    



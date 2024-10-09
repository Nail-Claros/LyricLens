from flask import Flask, render_template, url_for, redirect
import requests
import redis
import os

redis_url = os.getenv('REDIS_URL')


app = Flask(__name__)

#redis db
#r = redis.Redis(host='redis', port=6379)
r = redis.from_url(redis_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translation', methods=['get'])
def translations():
    return render_template('translation.html')

@app.route('/history', methods=['get'])
def history():
    return render_template('history.html')

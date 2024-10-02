from flask import Flask, render_template
import requests
import redis
import os

redis_url = os.getenv('REDIS_URL')


app = Flask(__name__)

#redis db
#r = redis.Redis(host='redis', port=6379)
r = redis.from_url(redis_url)

@app.route('/')
def hello_world():
    r.set('message', 'Hello, Team 14!') #store value in db

    message = r.get('message').decode('utf-8')
    return render_template('index.html', message=message)


from flask import Flask, render_template
import requests
import redis


app = Flask(__name__)

#redis db
r = redis.Redis(host='redis', port=6379)

@app.route('/')
def hello_world():
    r.set('message', 'Hello, Redis!') #store value in db

    message = r.get('message').decode('utf-8')
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)

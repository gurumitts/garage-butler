from flask import Flask
from flask import render_template, Response
from datastore import DataStore
import json
import logging
import os

app = Flask(__name__)

logs_location = '/var/log/garage'


@app.route('/')
def index(name=None):
    return render_template('index1.html')


@app.route('/status')
def status(name=None):
    db = DataStore()
    status = db.get_status()
    return json.dumps(status)


@app.route('/events')
def events(name=None):
    db = DataStore()
    events = db.get_events()
    return json.dumps(events)


@app.route('/logs/')
def logs(log=None):
    logs = []
    if log is None:
        for log in os.listdir(logs_location):
            logs.append(log)
    return render_template('logs.html', logs=logs)


@app.route('/logs/<log>')
def view_log(log=None):
    fo = open('%s/%s' %(logs_location, log), 'r')
    contents = fo.read()
    return Response(contents, mimetype='text/plain')


def start():
    # app.debug = True
    app.run(host='0.0.0.0')
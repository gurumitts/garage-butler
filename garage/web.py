from flask import Flask
from flask import render_template, Response, request
from datastore import DataStore
from babel.dates import format_timedelta
import datetime
import json
import logging
import os

app = Flask(__name__)

logs_location = '/var/log/garage'


@app.route('/')
def index(name=None):
    db = DataStore()
    status = db.get_status()
    events = db.get_events()
    return render_template('index.html', events=events, status=status)


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


@app.route('/toggle', methods=['POST'])
def toggle():
    if request.method == 'POST':
        logging.getLogger('garage').info('toggle switch web')
        if butler is not None:
            butler.toggle_switch()
            return 'ok'
        else:
            return 'no butler'
    return 'ko'


@app.route('/logs/<log>')
def view_log(log=None):
    fo = open('%s/%s' %(logs_location, log), 'r')
    contents = fo.read()
    return Response(contents, mimetype='text/plain')


@app.template_filter('time_delta')
def datatime_delta(dt):
    now = datetime.datetime.now()
    delta = now - dt
    return format_timedelta(delta, locale='en_US')


def start(_butler):
    global butler
    butler = _butler
    # app.debug = True
    app.run(host='0.0.0.0')



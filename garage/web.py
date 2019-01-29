from flask import Flask
from flask import render_template, Response, request, abort
from datastore import DataStore
from babel.dates import format_timedelta
import datetime
import json
import logging
import os


app = Flask(__name__)

logs_location = '/var/log/garage'
images_location = 'camera_images'


@app.route('/')
def index():
    db = DataStore()
    status = db.get_status()
    events = db.get_events()
    return render_template('index.html', events=events, status=status)


@app.route('/status')
def status():
    db = DataStore()
    status = db.get_status()
    return json.dumps(status)


@app.route('/events')
def events():
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
    fo = open('%s/%s' % (logs_location, log), 'r')
    contents = fo.read()
    fo.close()
    return Response(contents, mimetype='text/plain')


@app.route('/image/')
def image():
    return get_image()


def get_image():
    for pic in os.listdir(images_location):
        print(pic)
        if pic.endswith('.jpg'):
            fo = open('%s/%s' % (images_location, pic), 'r')
            contents = fo.read()
            fo.close()
            return Response(contents, mimetype='image/jpeg')
            pass
    abort(404)


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


@app.template_filter('time_delta')
def datetime_delta(dt):
    now = datetime.datetime.now()
    date = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    delta = now - date
    return format_timedelta(delta, locale='en_US')


def start(_butler):
    global butler
    butler = _butler
    # app.debug = True
    app.run(host='0.0.0.0', threaded=True)


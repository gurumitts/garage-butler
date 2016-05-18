import RPi.GPIO as GPIO
import time
from datastore import DataStore
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import boto
import boto.sns
import os

scheduler = BackgroundScheduler()

# gpio pin for door sensor and relay
button_pin = 19
relay_pin = 16

#set up gpio
print GPIO.VERSION
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, 1)

# minutes before sending warning
WARNING_OPEN_MINS = 5

# aws vars
REGION = 'us-east-1'
TOPIC = os.environ['SNS_TOPIC_ARN']



def get_db():
    db = DataStore()
    return db


class Butler:

    def __init__(self):
        logging.getLogger('garage').info('Butler is starting...')
        logging.getLogger('garage').info('AWS: region=%s, topic=%s' % (REGION, TOPIC))
        GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=self.door_check, bouncetime=1000)
        scheduler.start()
        scheduler.add_job(self.status_check, 'interval', minutes=2)

    def door_check(self, channel):
        status = GPIO.input(button_pin)
        db = get_db()
        if status == 1:
            db.record_door_closed()
            logging.getLogger('garage').info('Door closed')
        else:
            db.record_door_opened()
            logging.getLogger('garage').info('Door opened')
        db.shutdown()

    def status_check(self):
        logging.getLogger('garage').info('checking status')
        db = get_db()
        status = db.get_status()
        logging.getLogger('garage').info('status is %s' % status)
        if status['event'] == 'door opened' and status['elapsed_minutes'] > WARNING_OPEN_MINS:
            logging.getLogger('garage').info('sending notification')
            self._notify(status)
        else:
            logging.getLogger('garage').info('nothing to do')

    def toggle_switch(self):
        logging.getLogger('garage').info('toggle switch')
        GPIO.output(relay_pin, 0)
        time.sleep(.25)
        GPIO.output(relay_pin, 1)

    def _notify(self, status):
        msg = 'Door has been open for %s mins' % status['elapsed_minutes']
        conn = boto.sns.connect_to_region(REGION)
        pub = conn.publish(topic=TOPIC, message=msg)

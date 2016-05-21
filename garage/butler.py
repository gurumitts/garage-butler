import RPi.GPIO as GPIO
import time
from datastore import DataStore
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import boto
import boto.sns
import os
import datetime
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
        self.last_notification = datetime.datetime.now()
        self.last_status = GPIO.input(button_pin)

    def door_check(self, channel):
        time.sleep(2)
        status = GPIO.input(button_pin)
        db = get_db()
        logging.getLogger('garage').info('status = %s, last status = %s' % (status, self.last_status))
        if status == 1:
            if status != self.last_status:
                db.record_door_closed()
                logging.getLogger('garage').info('Door closed')
            else:
                logging.getLogger('garage').info('Door closed again')
        else:
            if status != self.last_status:
                db.record_door_opened()
                logging.getLogger('garage').info('Door opened')
            else:
                logging.getLogger('garage').info('Door opened again')
        self.last_status = status
        db.shutdown()

    def status_check(self):
        logging.getLogger('garage').info('checking status')
        db = get_db()
        status = db.get_status()
        settings = db.get_settings()
        db.shutdown()
        logging.getLogger('garage').info('status is %s' % status)
        if status['event'] == 'door opened' and status['elapsed_minutes'] > settings['warning_threshold_mins']:
            logging.getLogger('garage').info('sending notification')
            self._notify(status, settings)
        else:
            logging.getLogger('garage').info('nothing to do')

    def toggle_switch(self):
        logging.getLogger('garage').info('toggle switch')
        GPIO.output(relay_pin, 0)
        time.sleep(.25)
        GPIO.output(relay_pin, 1)

    def _notify(self, status, settings):
        notification_mins = self._mins_since_last_notification
        if notification_mins >= settings['notify_interval_mins']:
            msg = 'Door has been open for %s mins' % status['elapsed_minutes']
            conn = boto.sns.connect_to_region(REGION)
            pub = conn.publish(topic=TOPIC, message=msg)
            logging.getLogger('garage').info('SNS called successfully')
            self.last_notification = datetime.datetime.now()
        else:
            logging.getLogger('garage').info('Not sending notification. Interval: %s, '
                                             'Last notification was sent %s minuts ago' %
                                             (settings['notify_interval_mins'], notification_mins))

    def _mins_since_last_notification(self):
        delta = datetime.datetime.now() - self.last_notification
        return delta.total_seconds()/60
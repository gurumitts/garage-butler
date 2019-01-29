import RPi.GPIO as GPIO
import time
from datastore import DataStore
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from notify import Notify

scheduler = BackgroundScheduler()

# gpio pin for door sensor and relay
button_pin = 19
relay_pin = 16

# set up gpio
print GPIO.VERSION
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, 1)


def get_db():
    db = DataStore()
    return db


class Butler:

    def __init__(self):
        logging.getLogger('garage').info('Butler is starting...')
        self.notify = Notify(self)
        GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=self.door_check, bouncetime=1000)
        scheduler.start()
        scheduler.add_job(self.status_check, 'interval', minutes=1)
        self.last_notification = datetime.datetime.strptime('Jun 1 2005  1:00PM', '%b %d %Y %I:%M%p')
        self.last_status = GPIO.input(button_pin)

    def door_check(self, channel):
        time.sleep(3)
        status = GPIO.input(button_pin)
        db = get_db()
        # logging.getLogger('garage').info('status = %s, last status = %s' % (status, self.last_status))
        if status == 1:
            if status != self.last_status:
                db.record_door_closed()
                logging.getLogger('garage').info('Door closed')
                self.notify.notify()
            else:
                pass
                # logging.getLogger('garage').info('Door closed again')
        else:
            if status != self.last_status:
                db.record_door_opened()
                logging.getLogger('garage').info('Door opened')
                self.notify.notify()
            else:
                pass
                # logging.getLogger('garage').info('Door opened again')
        db.shutdown()
        self.last_status = status

    def status_check(self):
        logging.getLogger('garage').info('checking status')
        db = get_db()
        status = db.get_status()
        settings = db.get_settings()
        db.shutdown()
        logging.getLogger('garage').info('status is %s' % status)
        logging.getLogger('garage').info('setting are %s' % settings)
        self.notify.notify()

    def toggle_switch(self):
        logging.getLogger('garage').info('toggle switch')
        GPIO.output(relay_pin, 0)
        time.sleep(.25)
        GPIO.output(relay_pin, 1)

    def _notify(self, status, settings):
        pass

    def _mins_since_last_notification(self):
        delta = datetime.datetime.now() - self.last_notification
        return delta.total_seconds()/60

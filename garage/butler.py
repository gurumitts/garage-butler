import RPi.GPIO as GPIO
import time
from datastore import DataStore
import logging
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# gpio pin for door sensor
button_pin = 19

#set up gpio
print GPIO.VERSION
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def get_db():
    db = DataStore()
    return db


class Butler:

    def __init__(self):
        logging.getLogger('garage').info('Butler is starting...')
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
import RPi.GPIO as GPIO
import time
from datastore import DataStore
import logging


button_pin = 19

print GPIO.VERSION
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def get_db():
    db = DataStore()
    return db


class Butler:

    def __init__(self):
        logging.getLogger('garage').info('Control is starting...')
        GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=self.door_check, bouncetime=1000)

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

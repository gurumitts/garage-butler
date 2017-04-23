import ConfigParser
import json

import os
import logging
import time

import paho.mqtt.client as mqtt

from garage import DataStore


_LOG = logging.getLogger('garage')

MQ_HA_NOTIFY_TOPIC = 'home/notification'
MQ_STATUS_TOPIC = 'home/garage/door1/status'
MQ_COMMAND_TOPIC = 'home/garage/door1/cmd'


def get_db():
    db = DataStore()
    return db


class Notify:

    def __init__(self, butler):
        config = ConfigParser.ConfigParser()
        config_file = os.path.realpath(os.path.join(os.getcwd(), 'conf/app.conf'))
        _LOG.debug(config_file)
        config.read(config_file)
        self.butler = butler
        self.broker = config.get('mqtt', 'broker')
        self.mq_client = mqtt.Client()
        self.mq_connected = False
        self._mq_reconnect(force=True)

    def on_mq_message(self, client, userdata, msg):
        """Perform the requested action.
        Send updates if HA was restarted."""
        payload = msg.payload.decode("utf-8")
        if msg.topic == MQ_HA_NOTIFY_TOPIC and payload == 'HA_STARTED':
            _LOG.info("Homeassistant restarted. Sending current state")
            self._mq_reconnect(force=True)
            self.notify()
        elif msg.topic == MQ_COMMAND_TOPIC:
            _LOG.info("command recieved {0}".format(payload))
            self.butler.toggle_switch()

    def notify(self):
        self._mq_reconnect()
        db = get_db()
        status = db.get_status()
        msg = json.dumps(status)
        db.shutdown()
        _LOG.debug("sending message to: {0} "
                   "payload: {1}".format(MQ_STATUS_TOPIC, msg))
        self.mq_client.publish(MQ_STATUS_TOPIC, msg)

    def _mq_reconnect(self, force=False):
        if force:
            self.mq_connected = False
        while not self.mq_connected:
            try:
                self.mq_client = mqtt.Client()
                self.mq_client.connect(host=self.broker)
                self.mq_client.subscribe(MQ_COMMAND_TOPIC)
                self.mq_client.subscribe(MQ_HA_NOTIFY_TOPIC)
                self.mq_client.on_message = self.on_mq_message
                self.mq_client.loop_start()
                self.mq_connected = True
                _LOG.info("Connected to MQ!")
            except Exception as ex:
                _LOG.error("Could not connect to MQ: {0}".format(ex))
                _LOG.warning("Trying again in 5 seconds...")
                time.sleep(5)

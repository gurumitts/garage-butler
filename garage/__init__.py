import logging
from logging.config import fileConfig

def start():
    fileConfig('conf/log.conf')
    logging.getLogger('garage').log(logging.DEBUG, 'log setup complete')

import logging
from logging.config import fileConfig
import web
from butler import Butler

def start():
    fileConfig('conf/log.conf')
    logging.getLogger('garage').log(logging.DEBUG, 'log setup complete')

    butler = Butler()

    web.start()



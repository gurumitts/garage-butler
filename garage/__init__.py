import logging
from logging.config import fileConfig
import web
from butler import Butler
from datastore import DataStore

def start():
    fileConfig('conf/log.conf')
    logging.getLogger('garage').log(logging.DEBUG, 'Log setup complete')

    logging.getLogger('garage').log(logging.DEBUG, 'Initializing datastore ')
    db = DataStore(setup='true')
    db.shutdown()
    logging.getLogger('garage').log(logging.DEBUG, 'Complete')

    # butler = None
    butler = Butler()

    web.start(butler)



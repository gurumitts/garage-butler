import ConfigParser
import os
import subprocess
import logging
import threading
import time


class Camera:

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config_file = os.path.realpath(os.path.join(os.getcwd(), 'conf/app.conf'))
        logging.getLogger('garage').debug(config_file)
        config.read(config_file)
        self.camera_cmd = config.get('camera', 'camera_cmd')
        self.picture_delay = config.getfloat('camera', 'picture_delay_seconds')
        self.max_wait = config.getfloat('camera', 'max_wait_seconds')
        self.process = None

    def _take_picture(self):
        try:
            logging.getLogger('garage').debug('starting: %s' % self.camera_cmd.split(' '))
            self.process = subprocess.Popen(self.camera_cmd.split(' '))
            self.process.communicate()
            logging.getLogger('garage').debug('done')
        except Exception as e:
            logging.getLogger('garage').error('Taking picture failed: ')
            logging.getLogger('garage').error(e.message)

    def take_picture(self, skip_delay=False):
        if not skip_delay:
            logging.getLogger('garage').debug('waiting...')
            time.sleep(self.picture_delay)
        thread = threading.Thread(target=self._take_picture)
        thread.start()
        logging.getLogger('garage').debug('Waiting for camera process..')
        thread.join(self.max_wait)
        logging.getLogger('garage').debug('Waiting for camera process done')
        self.process.poll()
        if self.process.returncode != 0:
            logging.getLogger('garage').debug('Camera process is taking too long.. killing camera process')
            self.process.kill()
            return False
        else:
            return True


if __name__ == '__main__':
    camera = Camera()
    camera.take_picture()

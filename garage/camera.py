import ConfigParser
import os
import subprocess
import logging
import threading

class Camera:

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config_file = os.path.realpath(os.path.join(os.getcwd(), 'conf/app.conf'))
        logging.getLogger('garage').debug(config_file)
        config.read(config_file)
        self.camera_cmd = config.get('camera', 'camera_cmd')
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

    def take_picture(self):
        thread = threading.Thread(target=self._take_picture)
        thread.start()
        logging.getLogger('garage').debug('Waiting for camera process..')
        thread.join(10)
        logging.getLogger('garage').debug('waiting done')
        self.process.poll()
        if self.process.returncode != 0:
            logging.getLogger('garage').debug('killing camera process')
            self.process.kill()
            return False
        else:
            return True


if __name__ == '__main__':
    camera = Camera()
    camera.take_picture()

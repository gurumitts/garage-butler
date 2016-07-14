import ConfigParser
import os
import subprocess
import logging


class Camera:

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config_file = os.path.realpath(os.path.join(os.getcwd(), 'conf/app.conf'))
        logging.getLogger('garage').debug(config_file)
        config.read(config_file)
        self.camera_cmd = config.get('camera', 'camera_cmd')

    def take_picture(self):
        try:
            logging.getLogger('garage').debug('starting: %s' % self.camera_cmd.split(' '))
            subprocess.call(self.camera_cmd.split(' '))
            logging.getLogger('garage').debug('done')
        except Exception as e:
            logging.getLogger('garage').error('Taking picture failed: ')
            logging.getLogger('garage').error(e.message)


if __name__ == '__main__':
    camera = Camera()
    camera.take_picture()

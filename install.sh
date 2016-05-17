#!/bin/sh

GARAGE_HOME=/opt/garage-butler
GARAGE_BIN=${GARAGE_HOME}/bin
GARAGE_LOGS_DIR=/var/log/garage

if [ -d ${GARAGE_HOME} ]; then
    cd ${GARAGE_HOME}
    git pull
else
    cd /opt
    git https://github.com/gurumitts/garage-butler.git
    cd ${GARAGE_HOME}
    git pull
fi

if [ ! -d ${GARAGE_LOGS_DIR} ]; then
    mkdir ${GARAGE_LOGS_DIR}
fi

cp -f ${GARAGE_BIN}/garage /etc/init.d/

update-rc.d garage defaults




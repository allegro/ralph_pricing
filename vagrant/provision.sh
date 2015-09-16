#!/bin/bash
set -e
sudo apt-get update

## INSTALL dependencies
# Install MySQL Server in a Non-Interactive mode. NO PASSWORD for root
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git \
    libldap2-dev \
    libmysqlclient-dev \
    libmysqld-dev \
    libsasl2-dev \
    mysql-server-5.6 \
    python2.7 \
    python2.7-dev \
    python-virtualenv \
    redis-server

virtualenv --clear .
. bin/activate
cd src/scrooge/
make install

cat /home/vagrant/src/scrooge/vagrant/provisioning_scripts/profile_extensions >> /home/vagrant/.profile
source /home/vagrant/.profile

# create local settings file
SETTINGS_LOCAL_PATH=/home/vagrant/src/scrooge/src/ralph_scrooge/settings/local.py
if [ ! -f $SETTINGS_LOCAL_PATH ]; then
    echo "from ralph_scrooge.settings.dev import *  # noqa" > $SETTINGS_LOCAL_PATH
fi

# CREATE db
./vagrant/provisioning_scripts/init_mysql.sh

# final setups
# ./vagrant/provisioning_scripts/setup_js_env.sh

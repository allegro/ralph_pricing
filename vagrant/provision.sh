#!/bin/bash

set -e

apt-get update

DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python2.7 python-virtualenv python-dev build-essential \
    mysql-server redis-server libmysqlclient-dev libldap2-dev libsasl2-dev \
    vim-nox git

chown vagrant:vagrant /home/vagrant/sources

# We're handling this node-related stuff oustide of the `exec sudo ...` block below because of $HOME var,
# which has to be set to `/home/vagrant`, not `/root` (and no, `-H` switch doesn't affect $HOME in the
# aforementioned block).
sudo -H -u vagrant sh -c "wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.1/install.sh | bash"
sudo -H -u vagrant sh -c "NVM_DIR=/home/vagrant/.nvm \
                          . /home/vagrant/.nvm/nvm.sh && \
                          nvm install node && \
                          cd /home/vagrant/sources/ralph_scrooge && \
                          make install_ui"

exec sudo -u vagrant /bin/bash - <<EOF
set -e

echo "CREATE DATABASE scrooge DEFAULT CHARACTER SET 'utf8'" | mysql -u root
echo "GRANT ALL ON scrooge.* TO scrooge@'%' IDENTIFIED BY 'scrooge'; FLUSH PRIVILEGES" | mysql -u root

virtualenv --clear /home/vagrant/env
/home/vagrant/env/bin/pip install -U pip==1.5.6
/home/vagrant/env/bin/pip install -U setuptools==3.6
/home/vagrant/env/bin/pip install rq-dashboard  # not required (but useful), hence not present in requirements

source /home/vagrant/env/bin/activate
cd /home/vagrant/sources/ralph_scrooge
make install

dev_scrooge migrate
dev_scrooge generate_json_schema

mkdir -p /home/vagrant/.scrooge/log
cp src/ralph_scrooge/settings/local.py /home/vagrant/.scrooge/settings

dev_scrooge createsuperuser --noinput --user scrooge --email scrooge@scrooge.local
DJANGO_SETTINGS_MODULE='ralph_scrooge.settings.dev' \
python -c "import django; django.setup(); \
           from django.contrib.auth import get_user_model; \
           u = get_user_model().objects.get(username='scrooge'); \
           u.set_password('scrooge'); u.save()"

echo "source env/bin/activate && cd sources/ralph_scrooge" >> /home/vagrant/.profile
echo "VM provisioned successfully."

EOF

#!/bin/bash

# apply scrooge config
echo "
# set STRICT_TRANS_TABLES to allow only valid values for column type
# check https://dev.mysql.com/doc/refman/5.6/en/sql-mode.html#sqlmode_strict_trans_tables for details
[mysqld]
sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES
" | sudo tee --append /etc/mysql/conf.d/scrooge.cnf > /dev/null

sudo service mysql restart

echo "CREATE DATABASE scrooge DEFAULT CHARACTER SET 'utf8'" | mysql -u root
echo "GRANT ALL ON scrooge.* TO scrooge@'%' IDENTIFIED BY 'scrooge'; FLUSH PRIVILEGES" | mysql -u root

/home/vagrant/bin/scrooge syncdb --noinput

/home/vagrant/bin/scrooge createsuperuser --noinput --username scrooge --email scrooge@allegrogroup.com
/home/vagrant/bin/python vagrant/provisioning_scripts/createsuperuser.py

cd /home/vagrant/src/scrooge
make menu

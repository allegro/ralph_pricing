#!/bin/bash
(
    echo "DROP DATABASE IF EXISTS scrooge; CREATE DATABASE scrooge DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
    echo "USE scrooge; GRANT ALL PRIVILEGES ON scrooge TO 'scrooge'@'%' WITH GRANT OPTION;"
    echo "FLUSH PRIVILEGES;"
) | mysql -uroot

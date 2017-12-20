#!/bin/bash

mkdir -p /data/qding/db/
/usr/local/mongodb-linux-x86_64-rhel62-3.2.7/bin/mongod  --dbpath /data/qding/db --logpath /data/qding/db/acces.log --fork

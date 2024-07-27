#!/bin/bash

# start SSH service
sudo service ssh start

# start MongoDB service
sudo mkdir -p /data/db
sudo chown -R `id -u` /data/db
sudo mongod --fork --logpath /var/log/mongod.log

# wait for MongoDB
sleep 10

# import mongodb data
sudo mongorestore --db runtime-fuzz /home/ubuntu/ASTs-mongodb

# bash
exec /bin/bash

# 启动容器
# docker run -it wasmaker
# mysql: 

CREATE DATABASE 'converter';

GRANT ALL PRIVILEGES ON converter.* TO mysql@'10.128.0.8' IDENTIFIED BY 'mysql';

GRANT ALL PRIVILEGES ON converter.* TO mysql2@'10.128.0.11' IDENTIFIED BY 'mysql';

# RabbitMQ: 

#!/bin/sh

sudo apt-get install curl gnupg apt-transport-https -y

## Team RabbitMQ's main signing key
curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
## Community mirror of Cloudsmith: modern Erlang repository
curl -1sLf https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-erlang.E495BB49CC4BBE5B.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
## Community mirror of Cloudsmith: RabbitMQ repository
curl -1sLf https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-server.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/rabbitmq.9F4587F226208342.gpg > /dev/null

## Add apt repositories maintained by Team RabbitMQ
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
## Provides modern Erlang/OTP releases
##
deb [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu jammy main

# another mirror for redundancy
deb [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa2.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa2.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu jammy main

## Provides RabbitMQ
##
deb [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu jammy main

# another mirror for redundancy
deb [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa2.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa2.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu jammy main
EOF

## Update package indices
sudo apt-get update -y

## Install Erlang packages
sudo apt-get install -y erlang-base \
                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                        erlang-runtime-tools erlang-snmp erlang-ssl \
                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

## Install rabbitmq-server and its dependencies
sudo apt-get install rabbitmq-server -y --fix-missing

## Rabbit
sudo systemctl start rabbitmq-server

# nginx

sudo systemctl start nginx  

sudo nano /etc/nginx/nginx.conf

# events {
# }
# http {
#     client_max_body_size 100M;
#     server {
#         listen 80;
#         location /api/ {
#             proxy_pass http://127.0.0.1:5000/;
#         }
#         location /static/ {
#             root /var/converter_data/out/;
#             #  alias /var/converter_data/out;
#             autoindex off;
#         }
#     }
# }

# API: 

cd desarrollo-sw-nube-hfma/web
source ../venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 'api:create_app()'


# Worker
cd desarrollo-sw-nube-hfma/worker
source ../venv/bin/activate
flask run &

# NFS SERVER: 

sudo apt-get update

sudo apt install nfs-kernel-server

sudo mkdir /mnt/converter_data

sudo chown nobody:nogroup /mnt/converter_data #no-one is owner

sudo chmod 777 /mnt/converter_data #everyone can modify files

sudo nano /etc/exports # /mnt/converter_data 10.128.0.11(rw,sync,no_subtree_check) 10.128.0.8(rw,sync,no_subtree_check)

sudo exportfs -a 

sudo systemctl restart nfs-kernel-server


# NFS CLIENT: 

sudo apt install nfs-common

sudo mkdir /var/converter_data

sudo mount -t nfs 10.128.0.12:/mnt/converter_data /var/converter_data
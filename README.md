# desarrollo-sw-nube-hfma

## mysql 

docker run --name mysqldb -v mysqldbvol:/var/lib/mysql -p 3308:3306 -e MYSQL_USER=root -e MYSQL_PASSWORD=mysql -e MYSQL_DATABASE=converter -e MYSQL_ROOT_PASSWORD=Sup3rs3cr3t -d mysql/mysql-server:latest

## RabbitMQ

docker run -it --hostname my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management
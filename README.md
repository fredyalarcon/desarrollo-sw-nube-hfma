# desarrollo-sw-nube-hfma

## Autores

- Monica Muñoz
- Humberto Maury
- Andres Palma
- Fredy Alarcon


## Deployment usando Cloud Run 

### Deploy the image

Habilitamos los servicios para almacenar y construir nuestra imagen para posteriormente utilizar el servicio de cloud run

gcloud services enable artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com

Luego construimos la imagen

gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/imagen-web-api-converter:1.0

### Deploy the container to Cloud Run

gcloud run deploy api-converter --image gcr.io/${GOOGLE_CLOUD_PROJECT}/imagen-web-api-converter:1.0

### Verify deployment

gcloud run services list

## Deployment GCP usando Cloud compute instances

### Descripción 

Este código continene los 2 microservicios del web api y el worker, a continuación, se describen los pasos para desplegarlo en GCP:

### Pre requisitos
- Configurar el cloud Storage creando un bucket llamada bucket-web-converter
- Configurar Cloud SQL MySQL 8.0 con un usuario llamado ´mysql2´ y password ´mysql´ y conceder los permisos de lectura y escritura desde cualquier host.
- Configurar los servicios RabbitMQ y agregar el usuario ´rabbit´ con el password ´rabbit´

### Web - Api
1. Cree una isntancia nueva de tipo e2 small con ubuntu 23.04.
2. Inicie la máquina y establesca conexión ssh.
3. Dentro de la máquina clone el repositorio en la ruta /var/
4. ejecute los siguientes comandos
- sudo apt update
- sudo apt install python3-pip
- cd desarrollo-sw-nube-hfma
- sudo python3 -m venv venv
- source venv/bin/activate
- sudo pip install -r requirements.txt
5. Generar el archivo con GOOGLE_APPLICATION_CREDENTIALS en el bucket storage y reemplazarlo en la carpeta /var/desarrollo-sw-nube-hfma/web/api/static/
6. Creen una archivo llamado api-converter.sh en la siguiente ruta  /etc/init.d/ con el siguiente contenido reemplazando los valores de la BD y de RabbitMq por los correspondientes.
#!/bin/sh
export DB_HOST="<IP_DB_HOST_MYSQL>" &&
export RABBIT_HOST="<IP_RABBIT_HOST>" &&
cd /var/desarrollo-sw-nube-hfma &&
source venv/bin/activate &&
cd web/api &&
flask run
7. reiniciar la máquina, la aplicación debería iniciar el servicio de web-api al levantar el sistema operativo.

### Worker
1. Cree una isntancia nueva de tipo e2 small con ubuntu 23.04.
2. Inicie la máquina y establesca conexión ssh.
3. Dentro de la máquina clone el repositorio en la ruta /var/
4. ejecute los siguientes comandos
- sudo apt update
- sudo apt install python3-pip
- sudo apt-get -y update
- sudo apt-get -y upgrade
- sudo apt-get install -y ffmpeg
- cd desarrollo-sw-nube-hfma
- sudo python3 -m venv venv
- source venv/bin/activate
- sudo pip install -r requirements.txt
5. Generar el archivo con GOOGLE_APPLICATION_CREDENTIALS en el bucket storage y reemplazarlo en la carpeta /var/desarrollo-sw-nube-hfma/web/api/static/
6. Creen una archivo llamado api-converter.sh en la siguiente ruta  /etc/init.d/ con el siguiente contenido reemplazando los valores de la BD y de RabbitMq por los correspondientes.
#!/bin/sh
export DB_HOST="<IP_DB_HOST_MYSQL>" &&
export RABBIT_HOST="<IP_RABBIT_HOST>" &&
cd /var/desarrollo-sw-nube-hfma &&
source venv/bin/activate &&
cd worker &&
flask run
7. reiniciar la máquina, la aplicación debería iniciar el servicio de worker al levantar el sistema operativo.


## Deployment Local

Ejecute el siguiente comando en la terminar (debe tener instalado Docker y Docker-compose):

    `docker-compose -f docker-compose.yml up`

### Notas: 

- la instalación puede demorar varios minutos. verifique que no hayan errores durante la descarga, en caso de que esto suceda puede reintentar usando los siguiente comandos:

    `docker-compose -f docker-compose.yml down -v`

    `docker-compose -f docker-compose.yml up`

- Asegúrese de ejecutar los comandos con los privilegios de administrador. 

- Los puertos `80, 15672, 5672, 3306 y 5000` no debe estar en uso antes de ejecutar la aplicación.

- En el archivo docker-compose.yml se encuentran todas las instrucciones de creación de los contenedores, en caso de que después de ejecutar el comando anterior alguno de los contendores no haya iniciado correctamente se deben ejecutar los siguientes pasos: 

    1. validar la lista de contendores usando 
        
        `docker ps -a`
    2. iniciar los servicios detenidos usando 
    
        `docker start <container_id>`
        
    3. validar que todos los contendores esten activos.

- Para terminar la prueba y dar de baja a todos los recursos use el siguiente comando:
    
    `docker-compose -f docker-compose.yml down -v`

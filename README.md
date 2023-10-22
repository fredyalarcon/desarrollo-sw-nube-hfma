# desarrollo-sw-nube-hfma

## Autores

- Monica Muñoz
- Humberto Maury
- Andres Palma
- Fredy Alarcon

## Deployment 

Ejecute el siguiente comando en la terminar (debe tener instalado Docker y Docker-compose):

    `docker-compose -f docker-compose.yml up`

## Notas: 

- la instalacion puede demorar varios minutos. verifique que no hayan errorer durante la descarga, en caso de que esto suceda puede reintentar usando los siguiente comandos:

    `docker-compose -f docker-compose.yml down -v`

    `docker-compose -f docker-compose.yml up`

- Asegurese de ejecutar los comandos con los provilegios de admistrador. 

- Los puertos `80, 15672, 5672, 3306 y 5000` no debe estar en uso antes de ejecutar la aplicación.

- En el archivo docker-compose.yml se encuentran todas las instrucciones de creación de los contenedores, en caso que despues de ejecutar el comando anterio alguno de los contendores no haya iniciado correctamente se deben ejecutar los siguientes pasos:

    1. validar la lista de contendores usando 
        
        `docker ps -a`
    2. iniciar los servicios detenidos usando 
    
        `docker start <container_id>`
        
    3. validar que todos los contendores esten activos.

- Para terminar la prueba y dar de baja a todos los recursos use el siguiente comando: 
    
    `docker-compose -f docker-compose.yml down -v`

# MeLi Tech Assignment
## Configuración preliminar
### 1. Creación y activación del ambiente virtual
Una vez estés en la carpeta del proyecto, ejecuta los siguientes comandos en la terminal para crear el ambiente virtual:
```
python -m venv meli_tech_assignment
```
Para activar el ambiente en MAC/Linux
```
source meli_tech_assignment/bin/activate
```
Para activar el ambiente en Windows
```
meli_tech_assignment\Scripts\activate
```
Finalmente, instala las dependencias del proyecto
```
pip install -r requirements.txt
```
### 2. Subir el contenedor con la DB
Para ejecutar la base de datos, vamos a utilizar la imagen oficial de Postgres. Ejecuta el siguiente comando en la terminal para obtener la última versión desde el Dockerhub
```
docker pull postgres
```
A continuación, ejecuta el siguiente comando para iniciar la instancia de la base de datos
```
docker run --name my-postgres -e POSTGRES_PASSWORD=postgres -p 5001:5432 -d postgres
```
#### a. Inicializar la base de datos
Si es la primera vez que ejecutas el proyecto, o quieres reiniciar la base de datos, ejecuta el siguiente comando para inicializar las tablas de la base de datos como tablas vacías
```
flask --app test_app init-db
```
#### b. Visualizar las tablas
El contenedor expone la base de datos en el puerto 5001. Para conectarte al servidor de base de datos y visualizar las tablas, puedes usar una herramienta como [PgAdmin](https://www.pgadmin.org/docs/pgadmin4/8.4/server_dialog.html#) con las siguientes credenciales:

1. USER = postgres
2. PASSWORD = postgres
3. HOST = localhost

**Nota:** Estas son credenciales de prueba válidas únicamente para probar el proyecto en local.
### 3. Correr el servidor de flask
Para ejecutar la app de flask y que pueda comenzar a recibir peticiones, debemos ejecutar el siguiente comando
```
flask --app test_app run
```
## Probar el ejercicio
Una vez tenemos el servidor de prueba corriendo, tenemos varias opciones para probar la extracción de data.
### 1. Procesar el archivo de pruebas 'technical_challenge_data.csv'
Para procesar directamente el archivo de pruebas precargado en el servidor, puedes hacer una petición GET a http://localhost:5000/process_test_file. Este endpoint procesará el archivo, guardará la información en la base de datos, y retornará un JSON en el cual la llave "errors" contendrá la URL de descarga del archivo con los errores que se presentaron durante el procesamiento.
### 2. Subir y procesar un archivo propio
Para subir y procesar nuestro propio archivo podemos hacerlo enviando el archivo junto con una petición POST al endpoint http://localhost:5000/upload. Este endpoint subirá el archivo al servidor y retornará una respuesta 200 con un JSON que contiene la llave con la cual se guardó el archivo en el servidor. Al mismo tiempo, el servidor comenzará a procesar el archivo en segundo plano. Los archivos soportados son TXT, CSV y JSONL.

Ejemplo respuesta de http://localhost:5000/upload
```JSON
{"file_key":$file_key_value}
```

Para consultar el estado del procesamiento de nuestro archivo, podemos hacer una petición GET al endpoint  http://localhost:5000/status/$file_key_value donde *$file_key_value* es el valor que nos retornó el endpoint anterior cuando cargamos el archivo. En el caso en que el archivo aún se esté procesando, el endpoint retornará un status 102. En caso de que el archivo ya haya terminado de procesarse, el endpoint retornará un status 200, así como un JSON que tendrá la URL de descarga del archivo de errores JSONL. 

Ejemplo de respuesta de http://localhost:5000/status/$file_key_value cuando el procesacimento dela rchivo terminó.
```JSON
{"status":"completed","errors":"/download/$errors_file_key"}
```
Si seguimos el enlace de descarga, podremos obtener el archivo JSONL de errores. Este archivo tendrá las filas del archivo original que no pudieron procesarse y almacenarse en la base de datos, así como los errores asociados a cada una. 

En el script [endpoint_test.py](endpoint_test.py) podrás encontrar un ejemplo de cómo realizar estos llamados secuenciales utilizando Python. También puedes usar el script para subir tu propio archivo modificando la constante *FILE_PATH* por la ruta de tu archivo. Para correr el script, ejecuta el siguiente comando en una terminal diferente a la del servidor:
```
python endpoint_test.py
````
El archivo de errores quedará guardado en la carpeta [downloaded_files](downloaded_files) con el nombre errors.jsonl
## ¿Cómo configurar la lectura del archivo? (encoding y delimiter)
La configuración de la lectura del archivo se puede realizar tanto desde el cliente como desde el servidor.
### 1. Configuración desde el cliente
En el llamado al endpoint http://localhost:5000/upload, además de enviar el archivo, también podemos enviar data adicional para configurar:
1. encoding: El encoding que se va a utilizar para procesar el archivo.
2. delimiter: El delimitador que separa los valores en el caso de archivos TXT o CSV.
3. update: El comportamiento que va a tener el programa al encontrarse con registros de item ids que ya se encuentran en la base de datos. Especificamente, True para extraer de nuevo la información y actualizar los registros, o False para no procesar esos items que ya están en la base de datos.

Ejemplo de la data que se enviará al endpoint. Cualquiera de estos valores es opcional, por lo que la ejecución funcionará con los valores por defecto si no se envía alguno o ninguno.
``` JSON
{"encoding":"utf-8","delimiter":";","update":"True"}
```
el script [endpoint_test.py](endpoint_test.py) también muestra cómo utilizar Python para enviar estos parámetros en la petición desde el lado del Cliente.
### 2. Configuración desde el servidor
Desde el servidor podemos modificar el comportamiento por defecto que tiene el programa al interpretar los archivos que le son enviados. Para ello podemos ir al archivo [settings.py](test_app/settings.py), donde podremos modificar las constantes *DEFAULT_ENCODING*, *DEFAULT_DELIMITER* y *DEFAULT_UPDATE_REGISTERS*.
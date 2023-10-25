# Desing Document: API REST CONTACTOS

## 1. Descripcion
API para gradear pokemon del juego Pokemon Sleep

## 2. Objetivo
Realizar una API REST sobre el juego Pokemon Sleep para gradear los Pokemon 

## 3. Diseño del Endpoint
Diseño del endpoint

### 3.1 Gradear Pokemon
Endpoint para gradear Pokemon

|No.|Propiedad|Detalle|
|--|--|--|
|1|Description|Endpoint para procesar el texto de una captura del juego pokemon sleep y con la informacion generada valorar el pokemon de la captura|
|2|Summary|Endpoint Gradear Pokemon|
|3|Method|POST|
|4|Endpoint|http://localhost:8000/procesar-imagen-y-valorar-pokemon/|
|5|Query Params|NA|
|6|Path Param|NA|
|7|Data|NA|
|8|Version|v1|
|9|Status Code|200|
|10|Response type|application/json|
|11|Response|[{"id_pokemon": int, "nombre": string, "grado": string}]|
|12|Curl|curl -X 'POST' \'http://localhost:8000/procesar-imagen-y-valorar-pokemon/' \-H 'accept: application/json' \-H 'Content-Type: multipart/form-data' \-F 'file=@imagen_pokemon.jpeg;type=image/jpeg'|
|13|Status Code (error)|429|
|14|Response Type (error)|application/json|
|15|Response (error)|{"message":"No hay registros"}|

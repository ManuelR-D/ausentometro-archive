# Ausentómetro

Este repositorio contiene el código que se usó para obtener los datos de [ausent.ar](https://ausent.ar)

* scrapper.py: Obtiene las actas de las votaciones a partir de la página del Senado
* parserActas.py: Parsea los html obtenidos por scrapper.py y genera un json
* sqliteIngestor.py: Parsea el json y lo introduce en una base de datos SQLite.
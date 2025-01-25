import requests
import json
from bs4 import BeautifulSoup

import xml.etree.ElementTree as ET

# URL of the web service
url = "https://parlamentaria.legislatura.gob.ar/webservices/Json.asmx/GetDiputadosHistorico"

# Make the GET request
response = requests.get(url)
diputados_list = []
# Check if the request was successful
if response.status_code == 200:
    # Parse the XML response
    root = ET.fromstring(response.content)
    
    # Namespace dictionary to handle the default namespace
    ns = {'ns': 'http://tempuri.org/'}
    
    # Extract and print the data
    for diputado in root.findall('ns:Listado/ns:diputadosHistorico', ns):
        nombre = diputado.find('ns:nombre', ns).text
        apellido = diputado.find('ns:apellido', ns).text
        id = diputado.find('ns:id_legislador', ns).text
        print(nombre)
        print(id)
        url_legislador = diputado.find('ns:url_legislador', ns).text
        # Get the img tag from the legislator's page assuming that it is in a img tag with alt text equal to name
        info_legislador = requests.get('https://legislatura.gob.ar/' + url_legislador)
        if info_legislador.status_code == 200:
            soup = BeautifulSoup(info_legislador.content, 'html.parser')
            img = soup.find('img', alt=f'{apellido}, {nombre}')
            if img is not None:
                img_url = img.get('src')
            else:
                print(f'No image found for {nombre} {apellido}')
                img_url = "No image found"

        diputado_data = {
            "id_legislador": diputado.find('ns:id_legislador', ns).text,
            "apellido": diputado.find('ns:apellido', ns).text,
            "nombre": diputado.find('ns:nombre', ns).text,
            "url_legislador": diputado.find('ns:url_legislador', ns).text,
            "id_autor": diputado.find('ns:id_autor', ns).text,
            "cantidad_exptes_autor": diputado.find('ns:cantidad_exptes_autor', ns).text,
            "cantidad_exptes_coautor": diputado.find('ns:cantidad_exptes_coautor', ns).text,
            "cantidad_mandatos": diputado.find('ns:cantidad_mandatos', ns).text,
            "img_url": img_url 
        }
        diputados_list.append(diputado_data)


with open('diputados.json', 'w') as f:
    json.dump(diputados_list, f, indent=4)
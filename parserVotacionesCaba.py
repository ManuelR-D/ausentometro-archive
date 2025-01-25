import requests
import xml.etree.ElementTree as ET
import json

HOST="https://parlamentaria.legislatura.gob.ar/webservices/json.asmx/GetVotacionesExpediente?IdExpediente="

def parseUrl(id):
    url = HOST + str(id)
    
    # Make the GET request
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the XML response
    root = ET.fromstring(response.content)

    # Namespace dictionary to handle the default namespace
    ns = {'ns': 'http://tempuri.org/'}

    # Extract VotacionExpediente data
    votacion_expediente = root.find('.//ns:VotacionExpediente', ns)

    if votacion_expediente is not None:
        votacion_data = {
            'afirmativos': votacion_expediente.find('ns:afirmativos', ns).text,
            'negativos': votacion_expediente.find('ns:negativos', ns).text,
            'abstenciones': votacion_expediente.find('ns:abstenciones', ns).text,
            'sin_votar': votacion_expediente.find('ns:sin_votar', ns).text,
            'id_votacion': votacion_expediente.find('ns:id_votacion', ns).text,
            'asunto': votacion_expediente.find('ns:asunto', ns).text,
            'id_sesion': votacion_expediente.find('ns:id_sesion', ns).text,
            'fch_sesion': votacion_expediente.find('ns:fch_sesion', ns).text,
            'tipo_sesion': votacion_expediente.find('ns:tipo_sesion', ns).text,
            'desc_sesion': votacion_expediente.find('ns:desc_sesion', ns).text,
            'presidente_sesion': votacion_expediente.find('ns:presidente_sesion', ns).text,
            'secretarios_sesion': votacion_expediente.find('ns:secretarios_sesion', ns).text,
            'id_expediente': id
        }

        # Extract votes
        votes = []
        for legislador in votacion_expediente.findall('.//ns:VotoLegislador', ns):
            vote = {
                'id_legislador': legislador.find('ns:id_legilador', ns).text,
                'apellido': legislador.find('ns:apellido', ns).text,
                'nombre': legislador.find('ns:nombre', ns).text,
                'id_bloque': legislador.find('ns:id_bloque', ns).text,
                'bloque': legislador.find('ns:bloque', ns).text,
                'presencia': legislador.find('ns:presencia', ns).text,
                'voto': legislador.find('ns:voto', ns).text
            }
            votes.append(vote)

        # Combine VotacionExpediente data and votes
        output_data = {
            'votacion_expediente': votacion_data,
            'votes': votes
        }

        # Dump combined data to a JSON file
        with open(f'votes{i}.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)

        print("Votes and VotacionExpediente data have been successfully written to votes.json of " + url)
    else:
        print("No VotacionExpediente data found, ignoring response of " + url)

for i in range(129544, 200000):
    parseUrl(i)
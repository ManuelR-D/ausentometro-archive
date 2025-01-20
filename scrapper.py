import requests
host_url = "https://www.senado.gob.ar/votaciones/detalleActa/"

for i in range(1, 2523):
    url = host_url + str(i)
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Acta {i} encontrada")
        
        with open(f"./detalleActas/acta_{i}.html", "w") as file:
            file.write(response.text)
    else:
        print(f"Acta {i} no encontrada")
        break
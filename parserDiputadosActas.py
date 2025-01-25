import bs4
import os
import json

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if content == "Acta no encontrada":
        print(f"Acta not found in {file_path}")
        return []
    
    if content.__contains__("<title>403 Forbidden</title>"):
        print(f"403 Forbidden in {file_path}")
        return []

    if content.__contains__('<h2>The server returned a "500 Internal Server Error".</h2>'):
        print(f"500 Internal Server Error in {file_path}")
        return []
    
    if content == "interv":
        print(f"interv Error in {file_path}")
        return []

    soup = bs4.BeautifulSoup(content, 'html.parser')
    
    # Extract the subject of the vote
    subject = ""
    date = ""
    subject_h4 = soup.find('h4', class_='black-opacity')
    if subject_h4:
        subject = subject_h4.get_text(strip=True)
        date_h5 = subject_h4.find_next('h5', class_='text-muted m-t-0')
        if date_h5:
            date = date_h5.get_text(strip=True)[:10]

    if subject == "":
        subject = "NO SE ESPECIFICA"
        print(f"Subject not found in {file_path}")

    if date == "":
        date = "NO SE ESPECIFICA"
        print(f"Date not found in {file_path}")

    rows = soup.find_all('tr')

    diputados = []
    img_cache = {}

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5:
            img_url = cells[0].find('img')['src']  # Get the src attribute of the img tag
            full_img_url = img_url
            name = cells[1].get_text(strip=True)
            party = cells[2].get_text(strip=True)
            province = cells[3].get_text(strip=True)
            try: 
                vote = cells[4].find('span', class_='label').get_text(strip=True)
            except:
                vote = "AUSENTE"
            try: 
                info_url = cells[0].find('a')['href']
            except:
                info_url = ""

            diputados.append({
                'name': name,
                'party': party,
                'province': province,
                'vote': vote,
                'subject': subject,
                'date': date,
                'img_url': full_img_url,
                'info_url': info_url
            })

    return diputados

if __name__ == "__main__":
    directory = './diputadosActas'
    all_diputados = []

    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            try: 
                diputados = parse_html(file_path)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                continue
            all_diputados.extend(diputados)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = f'diputados_{timestamp}.json'

    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(all_diputados, json_file, ensure_ascii=False, indent=4)
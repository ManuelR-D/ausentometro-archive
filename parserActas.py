import bs4
import os
import json

def parse_html(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        content = file.read()
    
    soup = bs4.BeautifulSoup(content, 'html.parser')
    
    subject = ""
    date = ""
    subject_div = soup.find('div', style=lambda value: value and 'background-color:#E8EEF8' in value)
    if subject_div:
        subject_p = subject_div.find_all('p')
        if len(subject_p) > 1:
            subject = subject_p[1].get_text(strip=True)
            date_span = subject_p[1].find_next('span', style=lambda value: value and 'font-size: 15px' in value)
            if date_span:
                date = date_span.get_text(strip=True)[:10]

    if subject == "":
        subject = "NO SE ESPECIFICA"
        print(f"Subject not found in {file_path}")

    if date == "":
        subject = "NO SE ESPECIFICA"
        print(f"Date not found in {file_path}")

    rows = soup.find_all('tr')

    senators = []
    img_cache = {}

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5:
            img_url = cells[0].find('img')['src']  
            full_img_url = "https://www.senado.gob.ar/" + img_url
            name = cells[1].get_text(strip=True)
            party = cells[2].get_text(strip=True)
            province = cells[3].get_text(strip=True)
            try: 
                vote = cells[4].find('div').get_text(strip=True)
            except:
                vote = "AUSENTE"
            try: 
                info_url = cells[0].find('a')['href']
            except:
                info_url = ""

            senators.append({
                'name': name,
                'party': party,
                'province': province,
                'vote': vote,
                'subject': subject,
                'date': date,
                'img_url': full_img_url,
                'info_url': info_url
            })

    return senators

if __name__ == "__main__":
    directory = './detalleActas'
    all_senators = []

    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            try: 
                senators = parse_html(file_path)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                continue
            all_senators.extend(senators)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = f'senators_{timestamp}.json'

    with open(json_filename, 'w', encoding='latin-1') as json_file:
        json.dump(all_senators, json_file, ensure_ascii=False, indent=4)
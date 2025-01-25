import json
import requests
import wikipedia
import requests
import json

WIKI_REQUEST = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='

def get_wiki_image(search_term):
    try:
        result = wikipedia.search(search_term, results = 1)
        wikipedia.set_lang('es')
        wkpage = wikipedia.WikipediaPage(title = result[0])
        title = wkpage.title
        response  = requests.get(WIKI_REQUEST+title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
        return img_link        
    except:
        return 0
    
def read_names_from_json(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as file:
        data = json.load(file)
    return data


def main():
    names = read_names_from_json('senators_20250120_004148.json', "latin-1")
    names += read_names_from_json('diputados_20250120_033600.json')
    already_pull = {} #read_names_from_json('results2.json')
    results = {}
    for name in names:
        if name["name"] in already_pull:
            results[name["name"]] = already_pull[name["name"]]
            continue
        if name["name"] in results:
            continue
        print(f'Searching for {name["name"]}')
        image_url = get_wiki_image(name["name"])
        if image_url:
            results[name["name"]] = image_url
        else:
            results[name["name"]] = ''

    with open('results2.json', 'w', encoding='latin-1') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()
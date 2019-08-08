import requests
from datetime import datetime
from urllib.parse import unquote, urlencode
from bs4 import BeautifulSoup
from models import Annonce

"""Module qui récupère les annonces de LeBonCoin"""


def search(parameters):
    # Préparation des paramètres de la requête
    payload = {
        "limit": 35,
        "limit_alu": 3,
        "filters": {
            "enums": {
                "ad_type": [
                    "offer"
                ]
            },
            "category": {
                "id": "10"
            },
            "location": {
                "locations": [
                ]
            },
            "ranges": {
                "square": {
                    "min": parameters['surface'][0],
                    "max": parameters['surface'][1]
                },
                "price": {
                    "min": parameters['price'][0],
                    "max": parameters['price'][1]
                }
            },
            "keywords": {}
        }
    }

    for cp in parameters['cities']:
        payload['filters']['location']['locations'].append({'zipcode': str(cp[1])})

    header = {
        'api_key': 'ba0c2dad52b3ec'
    }

    request = requests.post("https://api.leboncoin.fr/finder/search", json=payload, headers=header)

    data = request.json()

    for ad in data['ads']:

        try:
            annonce = Annonce.get(
                id = 'lbc-' + str(ad['list_id'])
            )

        except:

            _request = requests.get("https://api.leboncoin.fr/finder/classified/" + str(ad['list_id']), headers=header)

            _data = _request.json()

            rooms, surface = 0, 0

            for param in _data.get('attributes'):
                if param['key'] == 'rooms':
                    rooms = param['value']
                if param['key'] == 'square':
                    surface = param['value'].replace(" m²", "")

            annonce, created = Annonce.get_or_create(
                id='lbc-' + str(_data.get('list_id')),
                defaults={
                    'site': "Leboncoin Pro" if ad['owner']['no_salesmen'] == False else "Leboncoin Particulier",
                    'created': datetime.strptime(_data.get('first_publication_date'), "%Y-%m-%d %H:%M:%S"),
                    'title': BeautifulSoup(_data.get('subject'), "lxml").text,
                    'description': BeautifulSoup(_data.get('body').replace("<br />", "\n"), "lxml").text,
                    'telephone': _data.get("phone"),
                    'price': _data.get('price')[0],
                    'surface': surface if surface.replace('.','',1).isdigit() else 0,
                    'rooms': rooms,
                    'city': _data.get('zipcode') if _data.get('zipcode') is not None else '',
                    'link': "https://www.leboncoin.fr/locations/%s.htm?ca=12_s" % _data.get('list_id'),
                    'picture': _data['images']['urls_large'] if 'urls_large' in _data['images'] else []
                }
            )

            if created:
                annonce.save()


def surface_value(surface):
    if surface == 0:
        return 0
    elif surface <= 20:
        return 1
    elif surface <= 25:
        return 2
    elif surface <= 30:
        return 3
    elif surface <= 35:
        return 4
    elif surface <= 40:
        return 5
    elif surface <= 50:
        return 6
    elif surface <= 60:
        return 7
    elif surface <= 70:
        return 8
    elif surface <= 80:
        return 9
    elif surface <= 90:
        return 10
    elif surface <= 100:
        return 11
    elif surface <= 110:
        return 12
    elif surface <= 120:
        return 13
    elif surface <= 150:
        return 14
    elif surface <= 300:
        return 15
    else:
        return 16

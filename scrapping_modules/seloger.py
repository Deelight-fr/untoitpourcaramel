import requests
import xml.etree.ElementTree as ET
from models import Annonce
from datetime import datetime
'''Module qui récupère les annonces de SeLoger.com'''


def search(parameters):
    # Préparation des paramètres de la requête
    payload = {
        'px_loyermin': parameters['price'][0],
        'px_loyermax': parameters['price'][1],
        'surfacemin': parameters['surface'][0],
        'surfacemax': parameters['surface'][1],
        # Si parameters['rooms'] = (2, 4) => "2,3,4"
        'nbpieces': list(range(parameters['rooms'][0], parameters['rooms'][1] + 1)),
        # Si parameters['bedrooms'] = (2, 4) => "2,3,4"
        'nb_chambres': list(range(parameters['bedrooms'][0], parameters['bedrooms'][1] + 1)),
        'ci': [int(cp[2]) for cp in parameters['cities']]
    }
    # Insertion des paramètres propres à LeBonCoin
    payload.update(parameters['seloger'])

    headers = {'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; D5803 Build/MOB30M.Z1)'}

    request = requests.get("http://ws-seloger.svc.groupe-seloger.com/search_4.0.xml", params=payload, headers=headers)

    xml_root = ET.fromstring(request.text)

    for annonceNode in xml_root.findall('annonces/annonce'):
        # Seconde requête pour obtenir la description de l'annonce
        # TODO: seulement si id absent de la base (limite les requetes api)

        try:
            annonce = Annonce.get(
                id = 'seloger-' + annonceNode.find('idAnnonce').text
            )

        except:
            _payload = {'noAudiotel': 1, 'idAnnonce': annonceNode.findtext('idAnnonce')}
            _request = requests.get("http://ws-seloger.svc.groupe-seloger.com/annonceDetail_4.0.xml", params=_payload, headers=headers)

            photos = list()
            for photo in annonceNode.find("photos"):
                photos.append(photo.findtext("stdUrl"))
                # Une seule photo, la première
                # break

            annonce, created = Annonce.get_or_create(
                id = 'seloger-' + annonceNode.find('idAnnonce').text,
                site = 'SeLoger',
                defaults = {
                    # SeLoger peut ne pas fournir de titre pour une annonce T_T
                    'title': "Appartement " + annonceNode.findtext('nbPiece') + " pièces" if annonceNode.findtext('titre') is None else annonceNode.findtext('titre'),
                    'description': ET.fromstring(_request.text).findtext("descriptif"),
                    'telephone': ET.fromstring(_request.text).findtext("contact/telephone"),
                    'created': datetime.strptime(annonceNode.findtext('dtCreation'), '%Y-%m-%dT%H:%M:%S'),
                    'price': annonceNode.find('prix').text,
                    'charges': annonceNode.find('charges').text,
                    'surface': annonceNode.find('surface').text,
                    'rooms': annonceNode.find('nbPiece').text,
                    'bedrooms': annonceNode.find('nbChambre').text,
                    'city': annonceNode.findtext('ville'),
                    'link': annonceNode.findtext('permaLien'),
                    'picture': photos
                }
            )

            if created:
                annonce.save()

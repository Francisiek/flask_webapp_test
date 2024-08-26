import requests
from flask_babel import _
from urllib3 import request

from webapp import app

def translate(text, source_language, destination_language):
    if app.config.get('TRANSLATION_API_KEY', None) is None:
        return _('Error: the translation service is not configuted.')

    auth = {
        'api_key': app.config['TRANSLATION_API_KEY'],
        'region': 'mideu'
    }

    api_request = requests.post(
        f'https://api.translate.com/translate?from={source_language}&to={destination_language}',
        headers=auth, json=[{'Text': text}]
    )

    if api_request.status_code != 200:
        return _('Error: the translation service failed.')

    return api_request.json()[0]['translations'][0]['text']
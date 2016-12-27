import requests

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Setlistfm(object):

    def __init__(self, bot):
        self.bot = bot

    def get_from_setlistfm(self, call, payload=None):
        baseurl = 'http://api.setlist.fm/rest/0.1/'
        url = baseurl + call
        headers = {'content-type': 'application/json',
                   'accept': 'application/json'}
        if payload is not None:
            r = requests.get(url, headers=headers, params=payload)
        else:
            r = requests.get(url, headers=headers)
        if r.ok:
            return r.json()
        else:
            # If response code is not ok (200),
            # print the resulting http error code with description
            r.raise_for_status()

    def find_setlist(self, artist):
        payload = {'artistName': artist}
        result = self.get_from_setlistfm('search/setlists', payload)
        logger.debug(result['setlists']['setlist'][0])

        return result['setlists']['setlist'][0]['sets']['set'][0]['song'][0]['@name']

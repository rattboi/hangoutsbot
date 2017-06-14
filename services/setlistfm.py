import logging
import datetime
import string

from bs4 import BeautifulSoup, NavigableString, Comment
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def levenshtein(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n
    current = range(n+1)
    for i in range(1, m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1, n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]


def find_ratio(a, b):
    a_filtered = cleanup(a)
    b_filtered = cleanup(b)
    distance = levenshtein(a_filtered, b_filtered)
    ratio = (distance / max(len(a_filtered), len(b_filtered), 1))
    return ratio


def similarity(artist_a, artist_b):
    artist_ratio = find_ratio(artist_a, artist_b)
    return artist_ratio


def cleanup(s):
    exclude = set(string.punctuation)
    extra_words_filter = ''.join(
             s.lower()
              .replace('the', '', -1)
              .replace('deluxe', '', -1)
              .replace('expanded', '', -1)
              .replace('edition', '', -1)
              .replace('remastered', '', -1)
              .replace('reissue', '', -1)
              .replace('version', '', -1)
              .replace('bonus', '', -1)
              .replace('tracks', '', -1)
              .replace('track', '', -1)
              .split())
    punc_filter = ''.join(ch for ch in extra_words_filter if ch not in exclude)
    return punc_filter


class Setlistfm(object):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_from_setlistfm(url):
        """ Fetches from setlist.fm """
        req = requests.get(url)
        if req.ok:
            return req
        else:
            # If response code is not ok (200),
            # print the resulting http error code with description
            req.raise_for_status()

    @staticmethod
    def get_from_setlistfm_api(call, payload=None):
        """ Fetches from setlist.fm api """
        baseurl = 'http://api.setlist.fm/rest/0.1/'
        url = baseurl + call
        headers = {'content-type': 'application/json',
                   'accept': 'application/json'}
        if payload is not None:
            req = requests.get(url, headers=headers, params=payload)
        else:
            req = requests.get(url, headers=headers)
        if req.ok:
            return req.json()
        else:
            # If response code is not ok (200),
            # print the resulting http error code with description
            req.raise_for_status()

    @staticmethod
    def get_lower_name(s):
        return s.get('artist').get('@sortName').lower()

    @staticmethod
    def filter_setlists_by_artist(artist, setlists):
        return [s for s in setlists
                if Setlistfm.get_lower_name(s) == artist.lower()]

    @staticmethod
    def filter_empty_sets(setlists):
        return [s for s in setlists if s.get('sets') != '']

    @staticmethod
    def get_songs_from_set(band_set):
#        if is_instance(band_set, list):
        songs = [(i+1, s['@name']) for i, s in enumerate(band_set['song'])]
        return songs

    def find_setlist_debug(self, artist):
        """ Finds playlist based on artist name """
        payload = {'artistName': artist}
        result = Setlistfm.get_from_setlistfm_api('search/setlists', payload)
        setlists = result.get('setlists').get('setlist')
        setlists = Setlistfm.filter_setlists_by_artist(artist, setlists)
        setlists = Setlistfm.filter_empty_sets(setlists)
        sets = [s['sets']['set'] for s in setlists]
        return sets

    def find_setlist(self, artist):
        """ Finds playlist based on artist name """
        payload = {'artistName': artist}
        result = Setlistfm.get_from_setlistfm_api('search/setlists', payload)
        logger.debug(result['setlists']['setlist'][0])
        return result['setlists']['setlist'][0]['sets']['set'][0]['song'][0]['@name']

    @staticmethod
    def filter_closest_artist_match(artist, artists):
        similarities = [(similarity(a['@name'], artist), a)
                        for a in artists]
        sorted_artists = sorted(similarities, key=lambda k: k[0])
        return sorted_artists

    @staticmethod
    def find_most_sets(artists):
        best_match = None
        most_sets = 0
        for artist_tuple in artists:
            (sim, artist) = artist_tuple
            try:
                artist_search = "artist/{}/setlists".format(artist['@mbid'])
                result = Setlistfm.get_from_setlistfm_api(artist_search)
                set_count = int(result['setlists']['@total'])
                if set_count > most_sets:
                    most_sets = set_count
                    best_match = artist
            except requests.exceptions.HTTPError as exc: # NOQA
                pass
        return best_match

    def find_artist(self, artist):
        full_artists = []
        payload = {'artistName': artist,
                   'p': 1}
        while True:
            try:
                result = Setlistfm.get_from_setlistfm_api('search/artists', payload)
                artists = result.get('artists').get('artist')
                if not isinstance(artists, list):
                    artists = [artists]
                full_artists = full_artists + artists
                payload['p'] = payload['p'] + 1
            except requests.exceptions.HTTPError as exc: # NOQA:
                break
        artists = Setlistfm.filter_closest_artist_match(artist, full_artists)
        if len(artists) > 3:
            artists = artists[:3]
        artist = Setlistfm.find_most_sets(artists)
        return artist

    def get_artist_postfix_code(self, artist):
        url = artist.get('url')
        postfix_slash_index = url.rfind('/')
        postfix_unnormalized = url[postfix_slash_index+1:]
        postfix_dot_index = postfix_unnormalized.rfind('.')
        postfix_normalized = postfix_unnormalized[:postfix_dot_index]
        return postfix_normalized

    def get_stats_url(self, artist):
        stats_url = "http://www.setlist.fm/stats/average-setlist/{}.html"
        postfix_code = self.get_artist_postfix_code(artist)
        return stats_url.format(postfix_code)

    def get_stats(self, artist):
        if artist is None:
            return []
        url = self.get_stats_url(artist)
        year = datetime.datetime.now().year

        response = None

        times = 5
        while times > 0:
            url_with_year = "{}?year={}".format(url, year)
            response = self.get_from_setlistfm(url_with_year)

            soup = BeautifulSoup(response.content, "html.parser")
            setlist_list = soup.select("div.setlistList")
            if setlist_list != []:
                songs = setlist_list[0].select("a.songLabel")
                if songs != []:
                    break

            year = year - 1
            times = times - 1

        if setlist_list == []:
            logger.debug("Couldn't find setlist")

        return setlist_list

    def get_songs_from_stats(self, stats_soup):
        songs = stats_soup.select("a.songLabel")
        return [item.text for item in songs]

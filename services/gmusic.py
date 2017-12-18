""" Service to manage Google Music """
import logging
import string
import datetime

from gmusicapi import Mobileclient
from bs4 import BeautifulSoup, NavigableString, Comment
import requests
import re

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

def similarity(artist_a, artist_b, title_a, title_b):
    artist_ratio = find_ratio(artist_a, artist_b)
    title_ratio = find_ratio(title_a, title_b)
    ratio = artist_ratio + title_ratio
    return ratio

def cleanup(s):
    exclude = set(string.punctuation)
    extra_words_filter = ''.join(
             s.lower()
              .replace('the','',-1)
              .replace('deluxe','',-1)
              .replace('expanded','',-1)
              .replace('edition','',-1)
              .replace('remastered','',-1)
              .replace('reissue','',-1)
              .replace('version','',-1)
              .replace('bonus','',-1)
              .replace('tracks','',-1)
              .replace('track','',-1)
              .split())
    punc_filter = ''.join(ch for ch in extra_words_filter if ch not in exclude)
    return punc_filter


class Gmusic(object):
    """Class to handle Google Music-related functionality"""

    def __init__(self, bot):
        """ init """
        self.bot = bot
        self.mob = Mobileclient()

    def login(self, username, password, android_id=Mobileclient.FROM_MAC_ADDRESS):
        """ login method """
        self.mob.login(username, password, android_id)
        return self.mob.is_authenticated()

    def search(self, searchterms):
        """ search for stuff """
        hits = self.mob.search("{0}".format(searchterms))
        return hits

    def create_playlist(self, name, song_ids, public=True):
        """
        create new playlist named 'name', containing songs with 'song_id'
        """
        playlist_id = self.mob.create_playlist(name,
                                               description="Bot Playlist",
                                               public=public)
        self.mob.add_songs_to_playlist(playlist_id, song_ids)
        return playlist_id

    def _make_playlist_share_link(self, share_token):
        base_share_url = "https://play.google.com/music/playlist"
        return "{}/{}".format(base_share_url, share_token)

    def share_playlist(self, playlist_id):
        try:
            [share_token] = [plist['shareToken']
                             for plist in self.mob.get_all_playlists()
                             if plist['id'] == playlist_id]
            return self._make_playlist_share_link(share_token)
        except ValueError:
            return "Cannot find playlist"

    def get_best_song_match(self, artist, title):
        hits = self.search("{0} {1}".format(artist, title))
        tracks = self.filter_to_song_minimum_info(self.get_songs(hits))
        similarities = [(similarity(track['artist'], artist,
                                    track['title'], title), track)
                        for track in tracks]

        sorted_tracks = sorted(similarities, key=lambda k: k[0])

        best_track = None
        if len(sorted_tracks) > 0:
            best_track = sorted_tracks[0][1]
        return best_track

    def get_best_album_match(self, artist, album):
        hits = self.search("{0} {1}".format(artist, album))
        albums = self.get_albums(hits)
        similarities = [(similarity(a['artist'], artist,
                                    a['album'], album), a)
                        for a in albums]

        sorted_albums = sorted(similarities, key=lambda k: k[0])

        if len(sorted_albums) == 0:
            return None

        best_album = sorted_albums[0][1]
        album_info = self.mob.get_album_info(best_album['albumId'])
        store_ids = [t['storeId'] for t in album_info['tracks']]
        print("Store ids in best_album_match: {0}".format(store_ids))
        return store_ids

    def format_best_match(self, artist, title):
        track = self.get_best_song_match(artist, title)
        share_base_url = 'https://play.google.com/music/m/'

        return "{0} {1} {2} - {3}{4}".format(track['artist'],
                                             track['album'],
                                             track['title'],
                                             share_base_url,
                                             track['storeId'])

    def get_albums(self, results):
        albums = [album.get('album', None) for album in results['album_hits']]
        album_details = [{'artist': a['artist'],
                          'album': a['name'],
                          'albumId': a['albumId']} for a in albums]
        return album_details

    def get_songs(self, results):
        return [song.get('track', None) for song in results['song_hits']]

    def filter_to_song_minimum_info(self, results):
        return [{'artist':  song.get('artist', None),
                 'album':   song.get('album', None),
                 'title':   song.get('title', None),
                 'storeId': song.get('storeId', None)} for song in results]

    def convert_spotify_embed_to_gmusic(self, url):
        s_list = SpotifyPlaylist(url)
        title = s_list.title
        best_matches = [self.get_best_song_match(i.artist, i.track)
                        for i in s_list.items]
        filtered_matches = [i for i in best_matches if i is not None]
        store_ids = [i.get('storeId') for i in filtered_matches]
        new_plist = self.create_playlist(title, store_ids)
        return self.share_playlist(new_plist)

    def convert_hbih_to_gmusic(self, url):
        hbih_list = HBIHPlaylist(url)
        title = hbih_list.title
        store_ids = []
        for item in hbih_list.items:
            album_store_ids = self.get_best_album_match(item[0], item[1])
            print("Adding store ids: {0}".format(album_store_ids))
            store_ids.extend(album_store_ids)

        print("All store ids: {0}".format(store_ids))
        new_plist = self.create_playlist(title, store_ids)
        return self.share_playlist(new_plist)

    def create_playlist_from_song_names(self, artist, songs):
        year = datetime.datetime.now().year
        title = "{} setlist ({})".format(artist, year)
        best_matches = [self.get_best_song_match(artist, s)
                        for s in songs]
        filtered_matches = [i for i in best_matches if i is not None]
        store_ids = [i.get('storeId') for i in filtered_matches]
        new_plist = self.create_playlist(title, store_ids)
        return self.share_playlist(new_plist)

    def get_newest_playlists(self, count=5):
        """ return 'count' newest playlists """
        all_plists = self.mob.get_all_playlists()
        sorted_plists = sorted(all_plists,
                               key=lambda k: k['lastModifiedTimestamp'],
                               reverse=True)
        if count > 0:
            newest_plists = sorted_plists[:count]
        else:
            newest_plists = sorted_plists
        info = [{'name': p['name'],
                 'share': self._make_playlist_share_link(p['shareToken'])}
                for p in newest_plists]
        return info

    def get_all_playlists(self):
        """ return all playlists """
        return self.get_newest_playlists(0)  # 0 = return everything

    def find_playlists(self, searchterm):
        """ find all playlists that have a name containing 'searchterm' """
        all_plists = self.get_all_playlists()
        matches = [p for p in all_plists
                   if p['name'].lower().find(searchterm.lower()) != -1]
        return matches


class SpotifyPlaylist(object):
    def __init__(self, url):
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
            self.title = self._get_title(soup)
            self.items = self._get_items(soup)
        else:
            raise Exception

    def _get_title(self, soup):
        title = soup.select("div.context-name")
        return title[0].text.strip()

    def _get_items(self, soup):
        tracks = soup.select("li.track-row")
        return [SpotifyTrack(item) for item in tracks]


class SpotifyTrack(object):
    """ Holds info about a Spotify Embed Track """
    def __init__(self, bs_item):
        self.artist = self._get_artist(bs_item)
        self.track = self._get_track(bs_item)

    def _get_artist(self, item):
        artist = self._strip_first(item.select("div.track-artist"))
        return artist

    def _get_track(self, item):
        for hit in item.findAll(attrs={'class': 'track-row-info'}):
            track = ''.join(child for child in hit.children
                            if isinstance(child, NavigableString) and not isinstance(child, Comment))
            return track.strip()

    @staticmethod
    def _strip_first(item):
        """ Return stripped first item from list """
        try:
            return item[0].text.strip()
        except (IndexError, AttributeError):
            return ""


class HBIHPlaylist(object):
    def __init__(self, url):
        res = requests.get(url)

        if res.status_code == 200:
            soup = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
            self.title = self._get_title(soup)
            self.items = self._get_items(soup)
        else:
            raise Exception

    def _get_title(self, soup):
        return soup.title.text

    def _get_items(self, soup):
        matcher = re.compile(r"{}".format("^\d{1,2}\. (.*) – (.*)"))
        matches = [matcher.match(i.text)
                   for i in soup.select('h2')
                   if matcher.match(i.text)]
        return [(i.group(1), i.group(2)) for i in matches]

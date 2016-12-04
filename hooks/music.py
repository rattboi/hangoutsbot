import asyncio
import settings
import bs4
import re
import logging

from requests import get, post, exceptions

from models.recommendation import Recommendation

from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MusicHook(object):

    def __init__(self, name, regex):
        self.name = name
        self.regex = regex

    def get_short_url(self, url):
        try:
            r = post("https://www.googleapis.com/urlshortener/v1/url",
                     params={"key": settings.GOOGLE_API_KEY}, json=({"longUrl": url}), headers={'Content-Type': 'application/json'})
            return r.json()["id"]
        except exceptions.MissingSchema:
            self.get_short_url("http://" + url)
        except KeyError:
            return url

    def find_recommendation(self, user, url):
        matching_urls = Recommendation.filter(Recommendation.url == url)
        results = matching_urls.select().where(Recommendation.user == user)
        return len(results) > 0

    def get_artist_and_album(self, url):
        matcher = re.compile(r"{}".format(".*\?t=([^ ]+).*"))
        album_artist = ""
        if matcher.match(url):
            album_artist = matcher.match(url).group(1)
        (album, artist) = album_artist.split('_-_')
        artist = artist.replace('_',' ')
        album = album.replace('_',' ')
        return (artist, album)
        
    def save_recommendation(self, user, url):
        short_url = self.get_short_url(url)
        if not self.find_recommendation(user, short_url):
            (artist, album) = self.get_artist_and_album(url)
            recommendation = Recommendation.create(user=user, artist=artist, album=album, url=short_url, time=datetime.now())

    @asyncio.coroutine
    def run(self, bot, conversation, user, text):
        matcher = re.compile(r"{}".format(self.regex))
        urls = []
        for word in text.split():
            if matcher.match(word):
                urls.append(matcher.match(word).group(1))
        for url in urls:
            self.save_recommendation(user, url)

hook = MusicHook("music", ".*(http[s]?://play.google.com/music/m/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+).*")

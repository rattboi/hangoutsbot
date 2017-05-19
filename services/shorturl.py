from requests import post, exceptions
import settings

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ShortUrl(object):

    def __init__(self, bot):
        self.bot = bot

    def get_short_url(self, url):
        try:
            r = post("https://www.googleapis.com/urlshortener/v1/url",
                     params={"key": settings.GOOGLE_API_KEY}, json=({"longUrl": url}), headers={'Content-Type': 'application/json'})
            return r.json()["id"]
        except exceptions.MissingSchema:
            self.get_short_url("http://" + url)
        except KeyError:
            return url

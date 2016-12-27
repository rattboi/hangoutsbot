""" Service to manage Google Music """
import logging

from gmusicapi import Mobileclient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Gmusic(object):
    """Class to handle Google Music-related functionality"""

    def __init__(self, bot):
        """ init """
        self.bot = bot
        self.mob = Mobileclient()

    def login(self, username, password):
        """ login method """
        self.mob.login(username, password, Mobileclient.FROM_MAC_ADDRESS)
        return self.mob.is_authenticated()

    def search(self, searchterms):
        """ search for stuff """
        hits = self.mob.search("{0}".format(searchterms))
        return len(hits)

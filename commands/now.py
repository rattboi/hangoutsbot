from models.command import BaseCommand
from models.lastuser import LastUser
from utils.parser import parser

from settings import secret

import pylast

from pylast import User

import re

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Now(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Now, self).__init__(name, parser, admin_required)
        self.network = pylast.LastFMNetwork(api_key=secret.LAST_API_KEY,
                                            api_secret=secret.LAST_API_SECRET,
                                            username=secret.LAST_USER,
                                            password_hash=secret.LAST_PASS_HASH)

    def get_lastfm_user(self, id):
        try:
            user = LastUser.get(LastUser.user_id == id)
            return user.lastfm_user
        except:
            return None

    def get_recent_track(self, user):
        last_user = User(user, self.network)
        now = last_user.get_now_playing()
        reply = ""
        if now is not None:
            reply = "now playing"
        else:
            now = last_user.get_recent_tracks(limit=1)[0].track
            reply = "last played"
        (track, artist, album) = self.get_now_info(now)
        return "{}: {} - {} - {}".format(reply, artist, album, track)

    def get_now_info(self, now):
        """ gets the current artist and track from last """
        track = now.get_name()
        artist = now.get_artist().get_name()
        album = ""
        try:
            album = now.get_album().get_name()
        except:
            album = "(no album)"
        return (track, artist, album)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        message = ""
        lastfm_user = self.get_lastfm_user(user.id)
        if lastfm_user is not None:
            message = self.get_recent_track(lastfm_user)
        else:
            message = "** must set username first (!reglast)**"
        yield from bot.send_message(conversation, message)


command = Now("now", parser, False)

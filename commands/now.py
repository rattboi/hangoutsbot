from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Now(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Now, self).__init__(name, parser, admin_required)
        self.add_to_parser()

    def add_to_parser(self):
        self.parser.add_argument("--all", action='store_true')

    def format_message(self, bot, user, status, artist, album, title):
        last_message = bot.lastfm.format_message(user, status, artist, album, title)

        track = bot.gmusic.get_best_song_match(artist, title)
        share_base_url = 'https://play.google.com/music/m/'

        track_url = "{0}{1}".format(share_base_url, track['storeId'])
        short_url = bot.shorturl.get_short_url(track_url)

        return "{0}\t({1})".format(last_message, short_url)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        list_all = parsed[0].all

        message = ""
        if list_all:
            users = bot.lastfm.get_all_users()
            recent_tracks = [(user[0], bot.lastfm.get_recent_track(user[1])) for user in users]
            messages = []
            for info in recent_tracks:
                user = info[0]
                (status, artist, album, title) = info[1]
                messages.append(self.format_message(bot, user, status, artist, album, title))
            message = "\n".join(messages)
        else:
            lastfm_user = bot.lastfm.get_user(user.id)
            if lastfm_user is not None:
                (status, artist, album, title) = bot.lastfm.get_recent_track(lastfm_user)
                message = self.format_message(bot, None, status, artist, album, title)
            else:
                message = "** must set username first (!reglast)**"
        yield from bot.send_message(conversation, message)


command = Now("now", parser, False)

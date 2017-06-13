from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Setlist(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Setlist, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        message = "** no results **"
        if len(parsed[1]) > 0:
            artist_name = " ".join(parsed[1])
            artist = self.setlistfm.find_artist(artist_name)
            stats = self.setlistfm.get_stats(artist)
            songs = self.setlistfm.get_songs_from_stats(stats[0])
            songs_message = "\n\t".join(songs)
            message = "**{}**\n\t{}".format(artist_name, songs_message)
        yield from bot.send_message(conversation, message)


command = Setlist("setlist", parser, False)

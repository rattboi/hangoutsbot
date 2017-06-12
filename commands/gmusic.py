from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Gmusic(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Gmusic, self).__init__(name, parser, admin_required)

    def format_best_match(self, bot, artist, title):
        track = bot.gmusic.get_best_song_match(artist, title)
        share_base_url = 'https://play.google.com/music/m/'

        return "{0} {1} {2} - {3}{4}".format(track['artist'],
                                             track['album'],
                                             track['title'],
                                             share_base_url,
                                             track['storeId'])

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        artist = parsed[1][0]
        track = "".join(parsed[1][1:])
        message = self.format_best_match(bot, artist, track)
        yield from bot.send_message(conversation, message)


command = Gmusic("gmusic", parser, False)

from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Convert(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Convert, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        message = "** no results **"
        if len(parsed[1]) > 0:
            url = " ".join(parsed[1])
            full_url= bot.gmusic.convert_spotify_embed_to_gmusic(url)
            message = "Converted: {}".format(bot.shorturl.get_short_url(full_url))
        yield from bot.send_message(conversation, message)


command = Convert("convert", parser, False)

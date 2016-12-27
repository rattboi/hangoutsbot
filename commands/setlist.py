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
        artist = " ".join(parsed[1])
        message = bot.setlistfm.find_setlist(artist)
        yield from bot.send_message(conversation, message)


command = Setlist("setlist", parser, False)

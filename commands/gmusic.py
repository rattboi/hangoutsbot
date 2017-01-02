from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Gmusic(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Gmusic, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        searchterms = " ".join(parsed[1])
        message = bot.gmusic.format_best_match('Nirvana', 'Come as you are')
        yield from bot.send_message(conversation, message)


command = Gmusic("gmusic", parser, False)

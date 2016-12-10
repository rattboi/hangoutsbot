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
        message = ""
        results = bot.gmusic.search("Nirvana")
        if results is not None:
            message = results
        else:
            message = "**no results**"
        yield from bot.send_message(conversation, message)


command = Gmusic("gmusic", parser, False)

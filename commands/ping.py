from models.command import BaseCommand
from utils.parser import parser
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Ping(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Ping, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        if len(parsed[1]) == 0:
            parsed[1].append("pong")
        message = " ".join(parsed[1])
        logger.debug(parsed)
        yield from bot.send_message(conversation, message, filter_to_use=parsed[0].filter)


command = Ping("ping", parser, False)

from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

import pylast

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Reglast(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Reglast, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        message = ''
        yield from bot.send_message(conversation, message)


command = Reglast("reglast", parser, False)

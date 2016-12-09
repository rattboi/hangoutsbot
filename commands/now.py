from models.command import BaseCommand
from models.lastuser import LastUser
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Now(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Now, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        message = ""
        lastfm_user = self.bot.get_lastfm_user(user.id)
        if lastfm_user is not None:
            message = self.bot.get_recent_track(lastfm_user)
        else:
            message = "** must set username first (!reglast)**"
        yield from bot.send_message(conversation, message)


command = Now("now", parser, False)

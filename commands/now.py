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
                messages.append(bot.lastfm.format_message(info[0], info[1][0], info[1][1], info[1][2], info[1][3]))
            message = "\n".join(messages)
        else:
            lastfm_user = bot.lastfm.get_user(user.id)
            if lastfm_user is not None:
                info = bot.lastfm.get_recent_track(lastfm_user)
                logger.debug(info)
                message = bot.lastfm.format_message(None, info[0], info[1], info[2], info[3])
            else:
                message = "** must set username first (!reglast)**"
        yield from bot.send_message(conversation, message)


command = Now("now", parser, False)

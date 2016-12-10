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

        list_all = False
        if parsed[0].all is not None:
            list_all = True

        message = ""
        if list_all:
            users = bot.lastfm.get_all_lastfm_users()
            recent_tracks = [bot.lastfm.get_recent_track(user) for user in users]
            message = "\n".join(recent_tracks)
        else:
            lastfm_user = bot.lastfm.get_lastfm_user(user.id)
            if lastfm_user is not None:
                message = bot.lastfm.get_recent_track(lastfm_user)
            else:
                message = "** must set username first (!reglast)**"
        yield from bot.send_message(conversation, message)


command = Now("now", parser, False)

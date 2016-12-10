from models.command import BaseCommand
from models.lastuser import LastUser
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Reglast(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Reglast, self).__init__(name, parser, admin_required)

    def set_lastfm_user(self, id, username):
        try:
            LastUser.get(LastUser.user_id == id)
            q = LastUser.update(lastfm_user=username).where(LastUser.user_id == id)
            q.execute()
        except:
            LastUser.get_or_create(user_id=id, lastfm_user=username)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        message = ""
        if len(parsed[1]) == 0:
            message = "**must specify username**"
        else:
            proposed_user = parsed[1][0]
            if bot.lastfm.is_valid_user(proposed_user):
                self.set_lastfm_user(user.id, proposed_user)
                message = "{}'s last.fm username set to **{}**".format(user.first_name, parsed[1][0])
            else:
                message = "User _{}_ is not a valid Last.fm user"
        yield from bot.send_message(conversation, message)


command = Reglast("reglast", parser, False)

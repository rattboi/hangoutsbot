from models.command import BaseCommand
from models.user import User
from utils.parser import parser
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Admin(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Admin, self).__init__(name, parser, admin_required)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        message = ''
        if len(parsed[1]) != 2:
          message = "Must specify first and last name"
        else:
          try:
            user_to_admin = User.get(first_name=parsed[1][0], last_name=parsed[1][1])
            user_to_admin.is_admin = True
            user_to_admin.save()
            message = 'user is now admin'
          except User.DoesNotExist:
            message = 'unable to find user'
        logger.debug(parsed)
        yield from bot.send_message(conversation, message, filter_to_use=parsed[0].filter)

command = Admin("admin", parser, True)

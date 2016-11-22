from database import BaseModel
from peewee import CharField, BooleanField
import sys
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Command(BaseModel):
    name = CharField()
    admin_required = BooleanField()

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        if "commands.{}".format(self.name) not in sys.modules:
            raise KeyError("Command with name {} not imported!".format(self.name))
        if self.admin_required and not user.is_admin:
            yield from bot.send_message(conversation, "You're not an admin!")
        else:
            yield from sys.modules["commands.{}".format(self.name)].command.run(bot, conversation, user, args)

    def __str__(self):
        return self.name


class BaseCommand(object):

    def __init__(self, name, parser=None, admin_required=False):
        self.name = name
        self.parser = parser
        self.admin_required = admin_required

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        raise NotImplementedError("The `run` method must be implemented.")

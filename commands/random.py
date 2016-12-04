from models.command import BaseCommand
from models.recommendation import Recommendation
from utils.parser import parser

from peewee import fn

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Random(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Random, self).__init__(name, parser, admin_required)

    def random_recommendations(self):
        recs = []
        recs = Recommendation.select().order_by(fn.Random()).limit(1)

        return [r.full_recommendation for r in recs]

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        recommendations = self.random_recommendations()
        message = ""
        if len(recommendations) > 0:
            message = "\n".join(recommendations)
        else:
            message = "-- no results --"
        yield from bot.send_message(conversation, message)


command = Random("random", parser, False)

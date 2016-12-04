from models.command import BaseCommand
from models.recommendation import Recommendation
from models.user import User
from utils.parser import parser
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Recent(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Recent, self).__init__(name, parser, admin_required)
        self.add_to_parser()

    def add_to_parser(self):
        self.parser.add_argument("--user")
        self.parser.add_argument("--count")

    def recent_recommendations(self, filter_user, filter_limit):
        recs = []
#        if filter_user is not None:
#            recs = Recommendation.select().where(Recommendation.user.first_name == filter_user).order_by(Recommendation.time).limit(filter_limit)
#        else:
        recs = Recommendation.select().order_by(Recommendation.time.desc()).limit(filter_limit)

        return [r.full_recommendation for r in recs]

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)

        filter_user = None
        if parsed[0].user is not None:
            filter_user = parsed[0].user

        filter_limit = 5
        if parsed[0].count is not None:
            filter_limit = int(parsed[0].count)

        logger.debug(filter_user)
        logger.debug(filter_limit)

        recommendations = self.recent_recommendations(filter_user, filter_limit)
        messages = ""
        if len(recommendations) > 0: 
            message = "\n".join(recommendations)
        else:
            message = "-- no results --"
        yield from bot.send_message(conversation, message)

command = Recent("recent", parser, False)

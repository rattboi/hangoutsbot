from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Playlist(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Playlist, self).__init__(name, parser, admin_required)
        self.commands = {'convert': self.convert,
                         'search': self.search,
                         'recent': self.recent}

    def convert(self, bot, args):
        url = " ".join(args)
        full_url = bot.gmusic.convert_spotify_embed_to_gmusic(url)
        return "Converted: {}".format(bot.shorturl.get_short_url(full_url))

    def format_playlists(self, bot, plists):
        links = ["{}\n {}".format(p['name'],
                                  bot.shorturl.get_short_url(p['share']))
                 for p in plists]
        if len(links) > 0:
            message = "\n".join(links)
        else:
            message = "-- no results --"
        return message

    def search(self, bot, args):
        """ Find playlists that match 'searchterm' """
        term = " ".join(args)
        if term.strip() != '':
            plists = bot.gmusic.find_playlists(term)
            return self.format_playlists(bot, plists)
        else:
            return "Error: '!playlist search <searchterm>'"

    def recent(self, bot, args):
        """ Gets all bot playlists, and lists them with their shortlinks """
        plists = bot.gmusic.get_newest_playlists()
        return self.format_playlists(bot, plists)

    def is_ok_command(self, command):
        l_command = command.lower().strip()
        return (l_command in self.commands)

    @asyncio.coroutine
    def run(self, bot, conversation, user, args):
        parsed = self.parser.parse_known_args(args)
        message = "** unknown command **"
        if len(parsed[1]) > 0:
            command = parsed[1][0]
            if self.is_ok_command(command):
                cmd_func = self.commands[command]
                message = cmd_func(bot, parsed[1][1:])
        yield from bot.send_message(conversation, message)


command = Playlist("playlist", parser, False)

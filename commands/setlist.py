from models.command import BaseCommand
from utils.parser import parser

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Setlist(BaseCommand):

    def __init__(self, name, parser, admin_required):
        super(Setlist, self).__init__(name, parser, admin_required)
        self.commands = {'generate': self.generate,
                         'show': self.show,
                         'search': self.search}

    def _get_songs(self, bot, artist_name):
        artist = bot.setlistfm.find_artist(artist_name)
        if artist is None:
            return None
        stats = bot.setlistfm.get_stats(artist)
        if stats is None:
            return None
        songs = bot.setlistfm.get_songs_from_stats(stats[0])
        return songs

    def format_playlists(self, bot, plists):
        f_string = "**{}**\n\t({})"
        links = [f_string.format(p['name'],
                                 bot.shorturl.get_short_url(p['share']))
                 for p in plists]
        if len(links) > 0:
            message = "\n".join(links)
        else:
            message = "-- no results --"
        return message

    def search(self, bot, args):
        """ Find playlists that match 'searchterm' and are setlists"""
        term = " ".join(args)
        if term.strip() != '':
            plists = bot.gmusic.find_playlists(term)
            # only return playlists that contain the word setlist
            plists = [p for p in plists if 'setlist' in p['name']]
            # limit to 10 plists
            if len(plists) > 10:
                plists = plists[:10]
            return self.format_playlists(bot, plists)
        else:
            return "Error: '!setlist search <searchterm>'"

    def generate(self, bot, args):
        artist = " ".join(args).title()
        songs = self._get_songs(bot, artist)
        if songs is None:
            return "Couldn't generate setlist for '{}'".format(artist)
        full_url = bot.gmusic.create_playlist_from_song_names(artist, songs)
        f_string = "Generated playlist for {} setlist: {}"
        return f_string.format(artist, bot.shorturl.get_short_url(full_url))

    def show(self, bot, args):
        """ Gets all bot playlists, and lists them with their shortlinks """
        artist_name = " ".join(args).title()
        songs = self._get_songs(bot, artist_name)
        if songs is None:
            return "Couldn't find setlist for '{}'".format(artist_name)
        numbered_songs = enumerate(songs)
        songs_message = "\n\t".join("{:02d}. {}".format(i+1, j)
                                    for i, j in numbered_songs)
        message = "**{}**\n\t{}".format(artist_name, songs_message)
        return message

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


command = Setlist("setlist", parser, False)

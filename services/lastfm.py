from models.lastuser import LastUser

import pylast
from pylast import User

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Lastfm(object):

    def __init__(self, api_key, api_secret, username, password_hash):
        self.network = pylast.LastFMNetwork(api_key=api_key,
                                            api_secret=api_secret,
                                            username=username,
                                            password_hash=password_hash)

    def is_valid_user(self, last_username):
        last_user = User(last_username, self.network)
        try:
            return bool(last_user.get_playcount() > 0)
        except:
            return False

    def get_all_users(self):
        """ returns a user's last.fm user name """
        try:
            return [(luser.user.first_name, luser.lastfm_user) for luser in LastUser.select()]
        except:
            return []

    def get_user(self, user_id):
        """ returns a user's last.fm user name """
        try:
            user = LastUser.get(LastUser.user_id == user_id)
            return user.lastfm_user
        except:
            return None

    def get_recent_track(self, user):
        last_user = User(user, self.network)
        now = last_user.get_now_playing()
        reply = ""
        if now is not None:
            reply = "now playing"
        else:
            now = last_user.get_recent_tracks(limit=1)[0].track
            reply = "last played"
        (track, artist, album) = self.get_now_info(now)
        return (reply, artist, album, track)

    def get_now_info(self, now):
        """ gets the current artist and track from last """
        track = now.get_name()
        artist = now.get_artist().get_name()
        album = ""
        try:
            album = now.get_album().get_name()
        except:
            album = None
        return (track, artist, album)

    def format_message(self, user, status, artist, album, song):
        if user is None:
            if album is None:
                return "{}: {} - {}".format(status, artist, song)
            else:
                return "{}: {} - {} - {}".format(status, artist, album, song)
        else:
            if album is None:
                return "**{}** -> {}: {} - {}".format(user, status, artist, song)
            else:
                return "**{}** -> {}: {} - {} - {}".format(user, status, artist, album, song)

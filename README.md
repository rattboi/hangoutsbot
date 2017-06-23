# MusicBot (based on HangoutsBot)

This is a music-related bot made to interface with Google Hangouts. It uses the [`hangups`](https://github.com/tdryer/hangups) library to connect to hangouts. For more information about HangoutsBot, Go to [`ovkulkarni/hangouts`](https://github.com/ovkulkarni/hangouts)

# Initial Setup

**NOTE: This project requires `python3`**

Go to [`ovkulkarni/hangouts`](https://github.com/ovkulkarni/hangouts) for information about initial setup.

You also need to add a few secrets to settings/secret.py

```
LAST_API_KEY =
LAST_API_SECRET =
LAST_USER = 
LAST_PASS_HASH = 

GMUSIC_USER = 
GMUSIC_PASS = 
```

TODO: More details to come for where to get said information.

# Functionality

## Google Play Music Integration

MusicBot integrates with GPM to support many things. When GPM share links are dumped into a group chat, it is added as a recommendation. This is the only event that happens without any input from users. This lends itself to quick linking of things people like, and persistence to find them later.

### Commands

!random
 - Returns a random item from the recommendations list. Also lists who added it, and a shorturl link to the content on GPM.

!recent [--user] [--count]
 - Returns a list of the most recent recommendations. Adding '--user <FirstName>' will limit to results from a specific person (not working currently).  Adding '--count <num>' returns more/less results. Defaults to 5 items. 

!playlist [search <searchterm> | recent | convert <spotifylink>]
  - search <searchterm> - Finds any playlist hosted by the bot matching a search term.
  
  - recent - Returns the 5 most recent playlists hosted by the bot
  
  - convert <spotifylink> - Scrapes the contents of a spotify embedded playlist and creates a hosted public playlist on Google Play Music. 

## Last.fm Integration

MusicBot integrates with Last.fm to support showing what users are currently listening to.

### Commands

`!reglast`
  - Pairs a user's last.fm account to their hangouts user. This allows the bot to look up last.fm info on a user's behalf, for commands such as `!now`
  
`!now [--all]`
  - Shows what the current user is listening to, and attempts to find the current song on GPM, giving a shortlink to the song. Adding the `--all` flag shows what everyone in the channel (who has registered with last.fm).
  
## Setlist.fm Integration

### Commands

`!setlist [show <bandname> | search <searchterm> | generate <bandname>`
   - show <bandname> - Shows the most recent average setlist for a given band. This is basically a "dry run" of what `!setlist generate` would do.
  
   - search <searchterm> - Finds any GPM bot-hosted playlists that match searchterm and also contain the term "setlist".
   
   - generate <bandname> - Generates a GPM bot-hosted playlist of the most recent average setlist for a given band. These can later be found using `!setlist search` or `!playlist [search | recent]`.
  

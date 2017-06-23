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

## Last.fm Integration

## Setlist.fm Integration

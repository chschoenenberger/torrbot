# torrbot
Telegram bot that scrapes Piratebay and can add torrents to Transmission

## Setup
Create virtual environment and activate it. Run `pip install -r requirements.txt` to install all dependencies. Fill in Telegram bot token, transmission
username & password, as well as host and port in config_example.yaml and rename it to
config.yaml.

Then run torrbot.py to start up the bot using `python torrbot.py`.

## Bot commands
The bot knows the following commands:
* /help - Shows all available commands
* /piratesearch (n) query - Show first n results for query on Piratebay
* /more - Show 5 more results for Query
* /download idx - Download torrent with idx from previous piratesearch
* /listtorrents - List all torrents in Transmission
* /deletealltorrents - Delete all torrents in Transmission
* /deletetorrent idx - Delete torrent with idx from previous listtorrent

## Example Flow
This is an example to show how the bot works:
1. Type `/piratesearch 15 linux`. This will show the top 15 results from piratebay.
2. Type `/more` to show 5 more results.
3. Type `/download 17` to download the result at position 17 in the table returned by 
/pirateserach
4. Type `/listtorrents` to check if the torrent was properly added.
5. Type `/deletetorrent 31` to delete the torrent with index 31. The index is shown by 
/listtorrents.

## Torrent Complete Script
The torrbot_completedNotification.sh script sends a message to your telegram when a 
torrent is completed. To use the it there are several steps required.

1. Fill in the bots token and the chat ID to which the message will be sent.
2. Stop the transmission torrent by typing `sudo service transmission-daemon stop`
3. Allow the execution of the script `sudo chmod +rx torrbot_completedNotification.sh`
4. Open the transmission-daemon settings file by `sudo nano /etc/transmission-daemon/settings.json`
and change the following:<br>
`"script-torrent-done-enabled": true,`<br>
`"script-torrent-done-filename": "/path/to/torrbot_completedNotification.sh",`
5. Restart the transmission daemon with `sudo service transmission-daemon start`
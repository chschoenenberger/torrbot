#!/bin/bash
# Bot token
BOT_TOKEN="your_bot_token"

# Your chat id
CHAT_ID="your_chat_id"

# Notification message
# If you need a line break, use "%0A" instead of "\n".
HTML_MES="<b>Download%20Completed</b>:%0A${TR_TORRENT_NAME}"
HTML_MES="${HTML_MES// /%20}"

# Sends the notification to the telegram bot
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?chat_id=${CHAT_ID}&parse_mode=HTML&text=${HTML_MES}" >> /home/pi/logs/transmission_done.log 2>&1

echo -e "\\n https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?chat_id=${CHAT_ID}&parse_mode=HTML&text=${HTML_MES}" >> /home/pi/logs/transmission_done.log 2>&1
echo -e "\\n [${TR_TIME_LOCALTIME}]-[${TR_TORRENT_NAME}] Download completed. Telegram notification sent." >> /home/pi/logs/transmission_done.log 2>&1
echo -e "\\n ******************************************************************************************* \\n" >> /home/pi/logs/transmission_done.log 2>&1
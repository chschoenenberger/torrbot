# TODO Default n for downloads if first argument is not numeric
# TODO Possibility to cancel download

import yaml
import logging
import pandas as pd
from transmission_rpc import Client

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

from scraper import search_piratebay

# Load config file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    token = config['token']
    username = config['username']
    password = config['password']
    host = config['host']
    port = config['port']

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def pirate_search(update, context):
    """Usage /piratesearch n query"""

    # If first argument is a number use it as number of rows to return. Otherwise return 5 rows.
    if context.args[0].isnumeric():
        context.user_data['n'] = int(context.args[0])
        text = ' '.join(context.args[1:])
    else:
        context.user_data['n'] = 10
        text = ' '.join(context.args)
    n = context.user_data['n']

    # Scrape piratebay and return n results if there are results.
    results = search_piratebay(text)
    if len(results):
        context.user_data['query'] = results.to_json()

        results_str = result_to_string(results, n_to=n)
        context.bot.send_message(chat_id=update.effective_chat.id, text=results_str, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('No results found. Please try again.')


def more(update, context):
    """Usage: /more"""
    n = context.user_data['n']
    results = pd.read_json(context.user_data.get("query", None))

    if len(results) < n+5:
        n_to = len(results)
    else:
        n_to = n+5
    results_str = result_to_string(results, n_from=n, n_to=n_to)

    context.bot.send_message(chat_id=update.effective_chat.id, text=results_str, parse_mode=ParseMode.MARKDOWN)
    context.user_data['n'] += 5


def result_to_string(result, n_from=0, n_to=5):
    result_str = result[['Name', 'Size', 'Seeders']][n_from:n_to].to_string(justify='center', max_colwidth=30)
    result_str = '```' + result_str + '```'
    return result_str


def download(update, context):
    """Usage: /download idx"""
    idx = context.args[0]

    # Load value
    try:
        query_df = pd.read_json(context.user_data.get("query", None))

        if query_df is not None:
            link = query_df.loc[int(idx), 'Link']
            send_to_transmission(link)
            name = query_df.loc[int(idx), 'Name']
            update.message.reply_text(f'Starting download: {name}')

    except ValueError:
        update.message.reply_text('Please use /piratesearch before running the /download command!')


def send_to_transmission(link):
    """Sends a link to the transmission rpc client adding it to the downloads."""
    c = Client(host=host, port=port, username=username, password=password)
    c.add_torrent(link)


def cancel_torrent():
    # TODO
    pass


def main():
    """Start the bot."""
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('piratesearch', pirate_search))
    dp.add_handler(CommandHandler('download', download))
    dp.add_handler(CommandHandler('more', more))

    # Start the Bot
    updater.start_polling()

    # Run the bot
    updater.idle()


if __name__ == '__main__':
    main()

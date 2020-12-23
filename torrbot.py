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
    help_text = """/piratesearch (n) query - Show first n results for query on Piratebay
    /more - Show 5 more results for Query
    /download idx - Download torrent with idx from previous piratesearch
    /listtorrents - List all torrents in Transmission
    /deletealltorrents - Delete all torrents in Transmission
    /deletetorrent idx - Delete torrent with idx from previous listtorrent
    """
    update.message.reply_text(help_text.replace('    ', ''))


def pirate_search(update, context):
    """Usage /piratesearch n query
    Show first n results for query on Piratebay. Note that n is limited to 30, as only the first page is scraped.
    If no n is provided 10 rows are shown by default.
    """
    if not context.args:
        update.message.reply_text('Please provide a query')
        return

    # If first argument is a number use it as number of rows to return. Otherwise return 10 rows.
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
    """Usage: /more
    Show 5 more results for previous piratesearch.
    """
    if not context.user_data.get('n', False):
        update.message.reply_text('Please run /piratesearch with a query before running /more.')

    # Get n and previous query data
    n = context.user_data['n']
    results = pd.read_json(context.user_data.get("query", None))

    # Show 5 next rows and increment n
    n_to = n + 5
    results_str = result_to_string(results, n_from=n, n_to=n_to)

    context.bot.send_message(chat_id=update.effective_chat.id, text=results_str, parse_mode=ParseMode.MARKDOWN)
    context.user_data['n'] += 5


def result_to_string(result, n_from=0, n_to=5):
    """
    Convert a pandas dataframe containing name, size, link, and seeders to a readable markdown table that can
    be printed in a readable form.

    :param result: The query results in form of a pandas dataframe
    :param n_from: First row to show
    :param n_to: Last row to show + 1
    :return: Return a string of the table
    """
    if len(result[n_from:n_to]):
        result_str = result[['Name', 'Size', 'Seeders']][n_from:n_to].to_string(justify='center', max_colwidth=30)
        result_str = '```' + result_str + '```'
        return result_str
    else:
        return "There are no more results."


def download(update, context):
    """Usage: /download idx
    Download torrent with idx from previous piratesearch. If piratesearch was not called before, a message is shown.
    If a download is started the bot indicates the start with the name of the torrent.
    """
    if not context.args:
        update.message.reply_text('Please provide an index for the torrent to download')
        return

    # Read idx from arguments
    idx = context.args[0]

    try:
        # Get query results
        query_df = pd.read_json(context.user_data.get("query", None))

        if query_df is not None:
            # Send link of selected torrent to transmission and return the name
            link = query_df.loc[int(idx), 'Link']
            send_to_transmission(link)
            name = query_df.loc[int(idx), 'Name']
            update.message.reply_text(f'Starting download: {name}')

    except ValueError:
        update.message.reply_text('Please use /piratesearch before running the /download command!')
    except KeyError:
        update.message.reply_text('ID was not found. Please try again.')


def get_torrent_client():
    """
    Create a transmission client from the config file.
    :return: The transmission client
    """
    return Client(host=host, port=port, username=username, password=password)


def send_to_transmission(link):
    """
    Sends a link to the transmission rpc client adding it to the downloads.

    :param link: A magnet link in string form
    :return: None
    """
    c = get_torrent_client()
    c.add_torrent(link)


def list_torrents(update, context):
    """Usage: /listtorrents
    List all torrents in Transmission
    """
    torrents = get_torrent_client().get_torrents()
    if torrents:
        # For each torrent get id, name and progress. Convert the dataframe to a readable format and return it.
        torrents_pd = pd.DataFrame(list(zip(
            [torrent.id for torrent in torrents],
            [torrent.name for torrent in torrents],
            [torrent.progress for torrent in torrents],
        )), columns=['id', 'Name', 'Progress'])
        torrents_str = torrents_pd.to_string(index=False, justify='center', max_colwidth=30)
        torrents_str = '```' + torrents_str + '```'
        context.bot.send_message(chat_id=update.effective_chat.id, text=torrents_str, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('No torrents downloading...')


def delete_all_torrents(update, context):
    """Usage: /deletealltorrents
    Delete all torrents in Transmission
    """
    # Get ids and names for all torrents
    c = get_torrent_client()
    torrent_ids = [torrent.id for torrent in c.get_torrents()]
    torrent_names = [torrent.name for torrent in c.get_torrents()]

    if torrent_ids:
        # Check if there are torrents and remove all torrents if yes
        c.remove_torrent(torrent_ids, delete_data=True)
        update.message.reply_text(f'Removed torrents {torrent_names}')
    else:
        update.message.reply_text('No torrents downloading...')


def delete_torrent(update, context):
    """Usage: /deletetorrent idx
    Delete torrent with idx from previous listtorrent
    """
    if not context.args:
        update.message.reply_text('Please provide a torrent id from /listtorrents')
        return

    id_arg = int(context.args[0])
    c = get_torrent_client()
    torrent_ids = [torrent.id for torrent in c.get_torrents()]
    if id_arg in torrent_ids:
        # Check if the provided id is in the torrents and remove it if yes
        name = c.get_torrent(id_arg).name
        c.remove_torrent(id_arg, delete_data=True)
        update.message.reply_text(f'Removed torrent {name}')
    else:
        update.message.reply_text(f'Torrent with id {id_arg} not found.')


def main():
    """Start the bot."""
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('piratesearch', pirate_search))
    dp.add_handler(CommandHandler('more', more))
    dp.add_handler(CommandHandler('download', download))
    dp.add_handler(CommandHandler('listtorrents', list_torrents))
    dp.add_handler(CommandHandler('deletealltorrents', delete_all_torrents))
    dp.add_handler(CommandHandler('deletetorrent', delete_torrent))

    # Start the Bot
    updater.start_polling()

    # Run the bot
    updater.idle()


if __name__ == '__main__':
    main()

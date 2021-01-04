import os
import sys
from getpass import getpass
import yaml

def load_config():
    config_path = os.path.join(sys.path[0], 'config/config.yaml')
    if os.path.exists(config_path):
        with open(config_path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
            token = config['token']
            username = config['username']
            password = config['password']
            host = config['host']
            port = config['port']

    else:
        token = input('Please enter the Telegram Bot token:')
        username = input('Please enter the transmission user name:')
        password = getpass('Please enter the transmission password:')
        host = input('Please enter the transmission host:')
        port = input('Please enter the transmission port:')

        with open(config_path, "w+") as file:
            yaml.dump({
                'token': token,
                'username': username,
                'password': password,
                'host': host,
                'port': port
            }, file)

    return token, username, password, host, port

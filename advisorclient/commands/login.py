""" module for login command """
import json
from json import JSONDecodeError
import os
import sys

import requests

from advisorclient.commands.AdvisorCommand import AdvisorCommand


def save_token(token):
    """ to save the token locally after login"""

    _conf = {"api_token": token}
    home_dir = os.getenv("HOME")

    with open(os.path.join(home_dir, ".advisor_auth"), "w") as auth_file:
        auth_file.write(json.dumps(_conf))
    os.chmod(os.path.join(home_dir, ".advisor_auth"), 0o600)


class Command(AdvisorCommand):
    """report metric command
    to login to the api server and store the token locally
    """
    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.config_path = None
        self.file_name = None

    def run(self):
        conf = self._load_config()

        response = requests.post(
            url="http://{}:{}/api/user/login".format(
                conf["api_server"]["ip"],
                conf["api_server"]["port"]
            ),
            json={
                "username": self.username,
                "password": self.password
            }
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error)
            sys.exit(1)

        if response.json()["code"] != 0:
            print(response.json()["msg"])
            sys.exit(1)

        print("logged in successfully")
        save_token(response.json()["body"]["sessionid"])
        print("api token saved")

    def show_desc(self):
        return "login to Advisor"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument(
            "-u",
            "--username",
            help="input the username",
            required=True
        )
        parser.add_argument(
            "-p",
            "--password",
            help="input the password",
            required=True
        )
        parser.add_argument(
            "-c",
            "--config",
            help="specify the path of the configuration file"
        )
        parser.add_argument(
            "-f",
            "--file",
            help="specify the name of the config file",
            required=True
        )

    def process_args(self, args):
        self.username = args.username
        self.password = args.password
        if args.config:
            self.config_path = args.config
        else:
            self.config_path = os.getcwd()

        self.file_name = args.file
        if not os.path.isfile(os.path.join(self.config_path, self.file_name)):
            print("error: cannot find config file")
            sys.exit(1)

    def _load_config(self):
        with open(os.path.join(self.config_path, self.file_name)) as config_file:
            try:
                conf = json.loads(config_file.read())
                return conf
            except JSONDecodeError:
                print("error: the config file is not in valid json format")
                sys.exit(1)

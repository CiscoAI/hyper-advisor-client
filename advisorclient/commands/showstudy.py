"""module for showstudy command"""
import json
from json import JSONDecodeError
import os
import sys


import requests

from advisorclient.commands.AdvisorCommand import AdvisorCommand


def load_token():
    """function to load token from the auth config file"""
    home_dir = os.getenv("HOME")

    if not os.path.isfile(os.path.join(home_dir, ".advisor_auth")):
        print("error: can't find api token, please run 'advsor-client auth' first")
        sys.exit(0)
    with open(os.path.join(home_dir, ".advisor_auth"), 'r') as auth_file:
        token = json.loads(auth_file.read())["api_token"]

    return token


class Command(AdvisorCommand):
    """Class for showstudy command
    List all the studies available for a user
    """
    def __init__(self):
        super().__init__()
        self.config_path = None
        self.file_name = None

    def run(self):
        conf = self._load_config()
        token = load_token()
        cookies = {
            'sessionid': token
        }
        response = requests.get(
            "http://{}:{}/api/study".format(
                conf["api_server"]["ip"],
                conf["api_server"]["port"]
            ),
            cookies=cookies,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error)
            sys.exit(1)
            
        if response.json()["code"] != 0:
            print(response.json()["msg"])
            sys.exit(1)

        elif not response.json()["body"]:
            print("No study created")
            sys.exit(0)

        else:
            print("available studies are: ")
            print()
            for study in response.json()["body"]:
                print("id: %--5s %s" % (str(study["study_id"]), study["name"]))

    def show_desc(self):
        return "list all the studies created"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument(
            "-p",
            "--path",
            help="specify the path of the configuration file"
        )
        parser.add_argument(
            "-f",
            "--file",
            help="specify the name of the config file", required=True
        )

    def process_args(self, args):
        if args.path:
            self.config_path = args.path
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

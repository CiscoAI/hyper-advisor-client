""" module for get suggestion command """

import json
from json import JSONDecodeError
import os
import sys

import requests

from advisorclient.commands.AdvisorCommand import AdvisorCommand


def load_token():
    """ to load the token from the auth config file """

    home_dir = os.getenv("HOME")

    if not os.path.isfile(os.path.join(home_dir, ".advisor_auth")):
        print("error: can't find api token, please run 'advsor-client auth' first")
        sys.exit(0)
    with open(os.path.join(home_dir, ".advisor_auth"), 'r') as auth_file:
        token = json.loads(auth_file.read())["api_token"]

    return token


def print_trail(trail):
    """ to print the trail """

    trail = json.loads(trail)
    for param in trail:
        print("%-15s: " % param['name'], end="")
        print(param['value'])


class Command(AdvisorCommand):
    """ class for get suggestion command
    to get trail (suggestion) from the api server
    """
    def __init__(self):
        super().__init__()
        self.study_id = None
        self.config_path = None
        self.file_name = None

    def run(self):
        token = load_token()
        cookies = {"sessionid": token}
        conf = self._load_config()
        response = requests.get(
            url="http://{}:{}/api/study/{}/trail".format(
                conf["api_server"]["ip"],
                conf["api_server"]["port"],
                self.study_id
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

        if not response.json()["body"]["trail_list"]:
            print("no trail need to be evaluated now")
            print("please check whether the study is started and try again")
            sys.exit(0)

        trail_list = response.json()["body"]["trail_list"]
        for j in range(len(trail_list)):
            print("trail id: %d" % trail_list[j]["trail_id"])
            print_trail(trail_list[j]["trail"])
            print()

    def show_desc(self):
        return "get suggestion from HyperAdvisor"

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
            help="specify the configuration file name",
            required=True
        )
        parser.add_argument(
            "-i",
            "--id",
            help="specify the study id",
            required=True
        )

    def process_args(self, args):
        self.study_id = args.id

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

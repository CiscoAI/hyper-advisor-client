""" module for report metric command"""
import json
from json import JSONDecodeError
import os
import sys

import requests

from advisorclient.commands.AdvisorCommand import AdvisorCommand


def load_token():
    """ to load token from the auth config file"""
    home_dir = os.getenv("HOME")

    if not os.path.isfile(os.path.join(home_dir, ".advisor_auth")):
        print("error: can't find api token, please run 'advsor-client auth' first")
        sys.exit(0)
    with open(os.path.join(home_dir, ".advisor_auth"), 'r') as auth_file:
        token = json.loads(auth_file.read())["api_token"]

    return token


class Command(AdvisorCommand):
    """class for report metric command
    to report the metric back to the api server
    """

    def __init__(self):
        super().__init__()
        self.file_name = None
        self.trial_id = None
        self.metric = None
        self.config_path = None

    def run(self):
        token = load_token()
        conf = self._load_config()

        cookies = {"sessionid": token}
        metric = self._parse_metric()
        response = requests.put(
            url="http://{}:{}/api/trial/{}".format(
                conf["api_server"]["ip"],
                conf["api_server"]["port"],
                self.trial_id
            ),
            json={
                "metric": metric
            },
            cookies=cookies
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error)
            sys.exit(1)

        print(response.json()["msg"])

    def _parse_metric(self):
        return dict({
            "value": self.metric
        })

    def show_desc(self):
        return "report the metric of the trial to the system"

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
            required=True,
            help="specify the configuration file name"
        )
        parser.add_argument(
            "-i",
            "--id",
            required=True,
            help="specify the trial id"
        )
        parser.add_argument(
            "-m",
            "--metric",
            required=True,
            help="input the metric of the trial",
            type=float
        )

    def process_args(self, args):
        self.file_name = args.file
        self.trial_id = args.id
        self.metric = args.metric

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

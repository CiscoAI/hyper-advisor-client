import json
import os

import sys

import requests

from commands.AdvisorCommand import AdvisorCommand

conf = None

class Command(AdvisorCommand):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.trail_id = None
        self.metric = None
        self.config_path = None

    def run(self):
        token = self._load_token()
        self._load_config()

        cookies = {"sessionid": token}
        metric = self._parse_metric()
        r = requests.post(
            url="http://{}:{}/api/study/trail/response".format(conf["api_server"]["ip"],
                                                               conf["api_server"]["port"]),

            json={
                "trail_id": self.trail_id,
                "metric": metric
            },
            cookies=cookies
        )

        try:
            r.json()
            print(r.json()["msg"])
        except:
            print("error: internal server error")
            sys.exit(1)

    def _parse_metric(self):
        return dict({
            "value": self.metric
        })

    def show_desc(self):
        return "report the metric of the trail to the system"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument("-p", "--path", help="specify the path of the configuration file")
        parser.add_argument("-f", "--file", required=True, help="specify the configuration file name")
        parser.add_argument("-i", "--id", required=True, help="specify the trail id")
        parser.add_argument("-m", "--metric", required=True, help="input the metric of the trail")

    def process_args(self, args):
        self.file_name = args.file
        self.trail_id = args.id
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
        global conf
        with open(os.path.join(self.config_path, self.file_name)) as f:
            try:
                conf = json.loads(f.read())
            except:
                print("error: the config file is not in valid json format")
                sys.exit(1)

    def _load_token(self):
        home_dir = os.getenv("HOME")

        if not os.path.isfile(os.path.join(home_dir, ".advisor_auth")):
            print("error: can't find api token, please run 'advsor-client auth' first")
            sys.exit(0)
        with open(os.path.join(home_dir, ".advisor_auth"), 'r') as f:
            token = json.loads(f.read())["api_token"]

        return token
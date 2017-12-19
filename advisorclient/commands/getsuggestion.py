import json
import os

import sys

import requests

from advisorclient.commands.AdvisorCommand import AdvisorCommand

conf = None


class Command(AdvisorCommand):
    def __init__(self):
        super().__init__()
        self.study_id = None
        self.config_path = None
        self.file_name = None

    def run(self):
        token = self._load_token()
        cookies = {"sessionid": token}
        self._load_config()
        r = requests.get(
            url="http://{}:{}/api/study/{}/trail".format(conf["api_server"]["ip"],
                                                         conf["api_server"]["port"],
                                                         self.study_id),
            cookies=cookies,
        )
        try:
            r.json()

            if r.json()["code"] != 0:
                print(r.json()["msg"])
                sys.exit(1)

            if len(r.json()["body"]["trail_list"]) == 0:
                print("no trail need to be evaluated now")
                print("please check whether the study is started and try again")
                sys.exit(0)

            for j in range(len(r.json()["body"]["trail_list"])):
                print("trail id: %d" % r.json()["body"]["trail_list"][j]["trail_id"])
                self._print_trail(r.json()["body"]["trail_list"][j]["trail"])

        except:
            print("internal server error")
            sys.exit(1)

    def _print_trail(self, trail):
        trail = json.loads(trail)
        for param in trail:
            print("%-15s: " % param['name'], end="")
            print(param['value'])

    def show_desc(self):
        return "get suggestion from HyperAdvisor"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument("-p", "--path", help="specify the path of the configuration file")
        parser.add_argument("-f", "--file", help="specify the configuration file name", required=True)
        parser.add_argument("-i", "--id", help="specify the study id", required=True)

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

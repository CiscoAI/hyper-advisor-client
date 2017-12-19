import json
import os

import sys

import requests

from commands.AdvisorCommand import AdvisorCommand

conf = None


class Command(AdvisorCommand):
    def __init__(self):
        super().__init__()
        self.config_path = None
        self.file_name = None

    def run(self):
        self._load_config()
        token = self._load_token()
        cookies = {
            'sessionid': token
        }
        r = requests.get(
            "http://{}:{}/api/study".format(conf["api_server"]["ip"], conf["api_server"]["port"]),
            cookies=cookies,
        )
        if r.json()["code"] != 0:
            print(r.json()["msg"])
            sys.exit(1)

        elif len(r.json()["body"]) == 0:
            print("No study created")
            sys.exit(0)

        else:
            print("available studies are: ")
            studies = [[] for i in range(4)]
            messages = [
                "ready to run: ",
                "running: ",
                "finished: ",
                "paused: "
            ]
            for study in r.json()["body"]:
                studies[study["status"]].append(dict(
                    id=study["study_id"],
                    name=study["name"],
                ))
            for i in range(len(studies)):
                print(messages[i])
                for study in studies[i]:
                    print("%--5s %s" % (str(study["id"]), study["name"]))
                print()

    def show_desc(self):
        return "list all the studies created"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument("-p", "--path", help="specify the path of the configuration file")
        parser.add_argument("-f", "--file", help="specify the name of the config file", required=True)

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

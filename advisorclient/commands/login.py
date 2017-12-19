import json
import os

import sys

from commands.AdvisorCommand import AdvisorCommand

import requests

conf = None


class Command(AdvisorCommand):
    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.config_path = None
        self.file_name = None

    def run(self):
        self._load_config()

        r = requests.post(
            url="http://{}:{}/api/user/login".format(conf["api_server"]["ip"], conf["api_server"]["port"]),
            json={
                "username": self.username,
                "password": self.password
            }
        )
        print("logged in successfully")

        if r.json()["code"] != 0:
            print(r.json()["msg"])
            sys.exit(1)
        self._save_token(r.json()["body"]["sessionid"])

        print("api token saved")

    def show_desc(self):
        return "login to Advisor"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument("-u", "--username", help="input the username", required=True)
        parser.add_argument("-p", "--password", help="input the password", required=True)
        parser.add_argument("-c", "--config", help="specify the path of the configuration file")
        parser.add_argument("-f", "--file", help="specify the name of the config file", required=True)

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
        global conf
        with open(os.path.join(self.config_path, self.file_name)) as f:
            try:
                conf = json.loads(f.read())
            except:
                print("error: the config file is not in valid json format")
                sys.exit(1)

    def _save_token(self, token):
        _conf = {"api_token": token}
        home_dir = os.getenv("HOME")

        with open(os.path.join(home_dir, ".advisor_auth"), "w") as f:
            f.write(json.dumps(_conf))
        os.chmod(os.path.join(home_dir, ".advisor_auth"), 0o600)

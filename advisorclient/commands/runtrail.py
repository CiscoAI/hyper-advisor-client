import json
import os

import sys
import subprocess

import requests
import time

from advisorclient import run_trail
from advisorclient.commands.AdvisorCommand import AdvisorCommand

conf = None


class Command(AdvisorCommand):
    def __init__(self):
        super().__init__()
        self.config_path = None
        self.file_name = None
        self.study_id = None
        self.iteration_num = None

    def run(self):
        token = self._load_token()
        self._load_config()

        cookies = {"sessionid": token}
        for i in range(self.iteration_num):
            while True:
                r = requests.get(
                    url="http://{}:{}/api/study/{}/trail".format(conf["api_server"]["ip"],
                                                                 conf["api_server"]["port"],
                                                                 self.study_id),
                    cookies=cookies,
                )
                try:
                    r.json()
                except:
                    print("error: internal server error")
                    exit(1)

                if r.json()["code"] != 0:
                    print(r.json()["msg"])
                    sys.exit(1)
                elif len(r.json()["body"]['trail_list']) == 0:
                    print("no trail need to be evaluated now, trying again ...")
                    print("Please check whether the study is started")
                    time.sleep(5)

                else:
                    iteration = r.json()["body"]["iteration"]
                    break

            for j in range(len(r.json()["body"]["trail_list"])):
                trail_id, metric = run_trail.run(
                    conf_path=os.path.join(self.config_path, self.file_name),
                    trail_id=r.json()["body"]["trail_list"][j]["trail_id"],
                    trail=str(r.json()["body"]["trail_list"][j]["trail"]),
                )

                r = requests.put(
                    url="http://{}:{}/api/trail/{}".format(conf["api_server"]["ip"],
                                                           conf["api_server"]["port"],
                                                           trail_id),

                    json={
                        "metric": metric
                    },
                    cookies=cookies
                )

                try:
                    r.json()
                except:
                    print("Internal server error")
                    sys.exit(1)

                if r.json()["code"] != 0:
                    print(r.json()["msg"])
                    sys.exit(1)

            print("%d iterations are finished in total" % iteration)
            print("starting next iteration")
        print("Finished")

    def show_desc(self):
        return "run study"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument("-n", "--number", required=True, help="specify the number of iteration needed", type=int)
        parser.add_argument("-p", "--path", help="specify the path of the configuration file")
        parser.add_argument("-f", "--file", required=True, help="specify the name of the configuration file")
        parser.add_argument("-i", "--id", required=True, help="specify the study id")

    def process_args(self, args):
        self.study_id = args.id
        self.iteration_num = args.number

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

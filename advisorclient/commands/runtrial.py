"""module for run trial command"""
import json
from json import JSONDecodeError
import os
import sys
import time

import requests


from advisorclient import run_trial
from advisorclient.commands.AdvisorCommand import AdvisorCommand


def load_token():
    """function to load token from auth config file"""
    home_dir = os.getenv("HOME")

    if not os.path.isfile(os.path.join(home_dir, ".advisor_auth")):
        print("error: can't find api token, please run 'advsor-client auth' first")
        sys.exit(0)
    with open(os.path.join(home_dir, ".advisor_auth"), 'r') as auth_file:
        token = json.loads(auth_file.read())["api_token"]

    return token


class Command(AdvisorCommand):
    """class for run trial command
    evaluate the trial automatically
    """
    def __init__(self):
        super().__init__()
        self.config_path = None
        self.file_name = None
        self.study_id = None
        self.iteration_num = None

    def run(self):
        token = load_token()
        conf = self._load_config()

        cookies = {"sessionid": token}
        for i in range(self.iteration_num):
            while True:
                response = requests.get(
                    url="http://{}:{}/api/study/{}/trial".format(
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
                    exit(1)

                print(response.json()["code"])
                if response.json()["code"] == 2018:
                    print(response.json()["msg"])
                    time.sleep(5)
                    continue
                elif response.json()["code"] != 0:
                    print(response.json()["msg"])
                    sys.exit(1)
                elif not response.json()["body"]['trial_list']:
                    print("no trial need to be evaluated now, trying again ...")
                    print("Please check whether the study is started")
                    time.sleep(5)

                else:
                    iteration = response.json()["body"]["iteration"]
                    break

            for j in range(len(response.json()["body"]["trial_list"])):
                trial_id, metric = run_trial.run(
                    conf_path=os.path.join(self.config_path, self.file_name),
                    trial_id=response.json()["body"]["trial_list"][j]["trial_id"],
                    trial=str(response.json()["body"]["trial_list"][j]["trial"]),
                )

                report_response = requests.put(
                    url="http://{}:{}/api/trial/{}".format(
                        conf["api_server"]["ip"],
                        conf["api_server"]["port"],
                        trial_id
                    ),
                    json={
                        "metric": metric
                    },
                    cookies=cookies
                )

                try:
                    report_response.raise_for_status()
                except requests.exceptions.HTTPError as error:
                    print(error)
                    sys.exit(1)

                if report_response.json()["code"] != 0:
                    print(report_response.json()["msg"])
                    sys.exit(1)

            print("%d iterations are finished in total" % iteration)
            print("starting next iteration")
        print("Finished")

    def show_desc(self):
        return "run study"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument(
            "-n",
            "--number",
            required=True,
            help="specify the number of iteration needed", type=int
        )
        parser.add_argument(
            "-p",
            "--path",
            help="specify the path of the configuration file"
        )
        parser.add_argument(
            "-f",
            "--file",
            required=True,
            help="specify the name of the configuration file"
        )
        parser.add_argument(
            "-i",
            "--id",
            required=True, help="specify the study id"
        )

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
        with open(os.path.join(self.config_path, self.file_name)) as config_file:
            try:
                conf = json.loads(config_file.read())
                return conf
            except JSONDecodeError:
                print("error: the config file is not in valid json format")
                sys.exit(1)

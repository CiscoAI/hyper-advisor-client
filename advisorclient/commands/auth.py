""" module for auth command"""
import json
import os

from advisorclient.commands.AdvisorCommand import AdvisorCommand


class Command(AdvisorCommand):
    """class for auth command
    give the token and store it locally
    """
    def __init__(self):
        super().__init__()
        # todo: distinguish unix and non unix os
        # sys_type = platform.system()
        self.home_dir = os.getenv("HOME")
        self.token = None

    def show_desc(self):
        return "authentication of the api server"

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument(
            "-t",
            "--token",
            help="input the api token",
            required=True
        )

    def process_args(self, args):
        self.token = args.token

    def run(self):
        _conf = {"api_token": self.token}
        with open(os.path.join(self.home_dir, ".advisor_auth"), "w") as auth_file:
            auth_file.write(json.dumps(_conf))
        os.chmod(os.path.join(self.home_dir, ".advisor_auth"), 0o600)
        print("api_token saved")

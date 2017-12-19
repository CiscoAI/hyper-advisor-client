import json

import os

import sys

from advisorclient.commands.AdvisorCommand import AdvisorCommand


class Command(AdvisorCommand):
    def __init__(self):
        super().__init__()
        self.out_path = None
        self.file_name = None

    def run(self):
        _conf = {
            'api_server': {},
            'model': {},
        }
        print('Welcome to configuration guider!')
        _conf['api_server']['ip'] = input('Ip of the api server: ')
        _conf['api_server']['port'] = input('Port of the api server: ') or 8000
        _conf['model']['python-version'] = input('Python version needed for the model (default python3): ') or 'python3'
        _conf['model']['project-root'] = input('Project root path : ')
        _conf['model']['entry'] = input('Entry point of model (executive python script, based on project path): ')
        conf_str = json.dumps(_conf)
        with open(os.path.join(self.out_path, self.file_name), "w") as f:
            f.write(conf_str)
        print('Done, saved to %s ...' % self.out_path)

    def add_options(self, parser):
        parser.add_argument("command")
        parser.add_argument("-o", "--out", help="Specify output configuration file path")
        parser.add_argument("-f", "--file", help="Specify the name of the output configuration file", required=True)

    def show_desc(self):
        return "follow the interactive instruction to finish the configuration"

    def process_args(self, args):
        if args.out:
            if not os.path.isdir(args.out):
                print("error: invalid path")
                sys.exit(1)
            self.out_path = args.out
        else:
            self.out_path = os.getcwd()
        self.file_name = args.file


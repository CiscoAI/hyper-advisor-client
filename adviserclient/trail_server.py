import getopt
import subprocess
import time
import json
from concurrent import futures

import grpc
import sys

import os

from adviserclient import trail_pb2
from adviserclient import trail_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
conf = None
conf_abs_path = None
debugging = False

ex_conf = """
{
    "response_url": "http://10.155.156.131:8000/api/study/trail/response",
    "model": {
        "python-version": "python3",
        "project-root": "/home/user/model-example",
        "entry": "model.py"
    },
    "trail-server": {
        "host": "0.0.0.0",
        "port": 50052
    }
}
"""


def deprint(*args):
    if debugging:
        print(*args)


def load_conf(file_path):
    global conf, conf_abs_path
    try:
        with open(file_path) as f:
            conf = json.loads(f.read())
    except Exception as e:
        print(str(e))
        print('Not found %s, or configuration file not in JSON format' % file_path)
        sys.exit(1)
    conf_abs_path = os.path.abspath(file_path)
    deprint('get abs conf %s' % conf_abs_path)
    # print('conf', conf_abs_path)


class TrailServicer(trail_pb2_grpc.TrailServicer):
    def RunTrail(self, request, context):
        subprocess.Popen(['trail_exec', conf_abs_path, str(request.trail_id), request.data])
        return trail_pb2.ReplyMessage(message="evaluating trail")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trail_pb2_grpc.add_TrailServicer_to_server(TrailServicer(), server)
    server.add_insecure_port('%s:%s' % (conf['trail-server']['host'], conf['trail-server']['port']))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def usage():
    print('usage')
    print('-h:  Print help message')
    print('-e:  Print configuration example')
    print('-c:  Specify configuration file path')
    print('-g:  Complete configuration interactively with guider')
    print('-o:  Specify output configuration file path using guider')


def json_guider(o_path):
    _conf = {
        'response_url': '',
        'model': {},
        'trail-server': {},
    }
    print('Welcome to configuration guider!')
    _conf['response_url'] = input('Input response url of api server: ')
    _conf['model']['python-version'] = input('Input python version model needed (default python3): ') or 'python3'
    _conf['model']['project-root'] = input('Input project root path : ')
    _conf['model']['entry'] = input('Input entry of model (executive python script, based on project path): ')
    _conf['trail-server']['host'] = input('Input trail server host (default 0.0.0.0):') or '0.0.0.0'
    _conf['trail-server']['port'] = input('Input trail server port (default 50052): ') or '50052'
    conf_str = json.dumps(_conf)
    with open(o_path, "w") as f:
        f.write(conf_str)
    print('Done, saved to %s ...' % o_path)


def execute():
    global debugging
    argv = sys.argv
    o_path = 'model.conf.json'
    need_guide = False

    opts, args = getopt.getopt(argv[1:], 'c:ehgo:d')
    for o, v in opts:
        if o in ['-h']:
            usage()
            sys.exit(0)
        if o in ['-e']:
            print(ex_conf)
            sys.exit(0)
        if o in ['-c']:
            load_conf(v)
            # print('conf', conf_abs_path)
        if o in ['-o']:
            o_path = v
        if o in ['-g']:
            need_guide = True
        if o in ['-d']:
            debugging = True
    if need_guide:
        json_guider(o_path)
        sys.exit(0)
    if conf_abs_path is None:
        usage()
        sys.exit(1)

    deprint('end reading param')
    serve()


if __name__ == "__main__":
    execute()

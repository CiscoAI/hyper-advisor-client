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


def load_conf(file_path):
    try:
        with open(file_path) as f:
            conf = json.loads(f.read())
    except Exception as e:
        print(str(e))
        print('Not found %s, or configuration file not in JSON format' % file_path)
        sys.exit(1)
    conf_abs_path = os.path.dirname(file_path)
    print('conf', conf_abs_path)


class TrailServicer(trail_pb2_grpc.TrailServicer):
    def RunTrail(self, request, context):
        subprocess.Popen(['python3', 'run_trail.py', conf_abs_path, str(request.trail_id), request.data])
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


def execute():
    argv = sys.argv

    opts, args = getopt.getopt(argv[1:], 'c:eh')
    for o, v in opts:
        if o in ['-h']:
            usage()
            sys.exit(0)
        if o in ['-e']:
            with open('model.conf.json') as f:
                ex_conf = f.read()
            print(ex_conf)
            sys.exit(0)
        if o in ['-c']:
            load_conf(v)
            print('conf', conf_abs_path)
    serve()


if __name__ == "__main__":
    execute()

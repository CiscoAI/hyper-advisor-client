import sys

import subprocess

import requests
import json

conf = None


def load_conf(file_path):
    try:
        with open(file_path) as f:
            conf = json.loads(f.read())
    except Exception as e:
        print(str(e))
        print('Not found %s, or configuration file not in JSON format' % file_path)
        sys.exit(1)


def generate_command(trail):
    o_trail = json.loads(trail)
    cmd = []
    for param in o_trail:
        cmd.append('--%s=%s' % (param['name'], param['value']))
    return cmd


def parse_metric(metric):
    return dict({
        "value": metric
    })


def run():
    argv = sys.argv
    conf_path = argv[1]
    trail_id = argv[2]
    trail = argv[3]

    load_conf(conf_path)

    # call the objective function and get the output
    cmd = generate_command(trail)

    parameter_list = [conf['model']["python-version"], conf['model']["entry"]] + cmd
    # parameter_list = parameter_list + values
    proc = subprocess.Popen(parameter_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = str(proc.communicate()[0])

    # format the output
    start = 2
    end = len(output)-3
    metric = float(output[start:end])
    metric = parse_metric(metric)

    # print(metric)

    api_server = conf['api-server']
    r = requests.post(
        url='%s://%s:%s%s' % (api_server['protocol'], api_server['ip'], api_server['port'], api_server['url']),
        json={
            "trail_id": trail_id,
            "metric": metric
        }
    )
    # print(r.text)

if __name__ == "__main__":
    run()

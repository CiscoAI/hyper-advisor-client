""" module for run trials """
import sys

import subprocess

import os
import json


def load_conf(file_path):
    """ function to load the config file"""

    try:
        with open(file_path) as conf_file:
            conf = json.loads(conf_file.read())
            return conf
    except Exception as error:
        print(str(error))
        print('Not found %s, or configuration file not in JSON format' % file_path)
        sys.exit(1)


def generate_command(trial):
    """ function to generate command list in the proper format """

    o_trial = json.loads(trial)
    cmd = []
    for param in o_trial:
        cmd.append('--%s=%s' % (param['name'], param['value']))
    return cmd


def parse_metric(metric):
    """ function to parse the metric into dictionary """

    return dict({
        "value": metric
    })


def run(conf_path, trial_id, trial):
    """ function to run the model """

    conf = load_conf(conf_path)

    # call the objective function and get the output
    cmd = generate_command(trial)

    parameter_list = [conf['model']["python-version"], conf['model']["entry"]] + cmd

    os.chdir(conf['model']['project-root'])
    proc = subprocess.Popen(
        parameter_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output = str(proc.communicate()[0])

    # format the output
    start = 2
    end = len(output)-3
    metric = float(output[start:end])
    metric = parse_metric(metric)

    return trial_id, metric

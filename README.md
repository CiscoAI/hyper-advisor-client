# Advisor Client Tutorial

## 1. Set up

```
git clone https://github.com/CiscoAI/hyper-advisor-client.git
pip install -r requirements.txt
python setup.py install
```
## 2. Usage

```
advisor-client <command> [flag] [args]
```

### Available Commands:

- authtrial

Give the token and store it locally. This should be done first if you have not logged in.
To get the token, please login through the website first.

|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-t, --token|TOKEN|input the api token|Yes|

- config

Make the configuration of api server and the info of model. Follow the prompted instructions to complete the configuration

Note: the sample random forest model is included in this repository, which you can use.

|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-o, --out|PATH|Specify the absolute path to store the config file|No|
|-f, --file|FILE_NAME|Specify the name of the output configuration file|Yes|

- getsuggestion

Get the trial from the server

|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-p, --path|PATH|specify the path of the configuration file|No|
|-f, --file|FILE_NAME|Specify the name of the configuration file|Yes|
|-i, --id|STUDY_ID|specify the study id|Yes|

- login

Log in to the api server, and save the token locally

|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-c, --config|CONFIG|specify the path of the configuration file|No|
|-f, --file|FILE_NAME|Specify the name of the configuration file|Yes|
|-u, --username|USERNAME|input the username|Yes|
|-p, --password|PASSWORD|input the password|Yes|

- reportmetric

Report the metric (objective value) back to the api server

|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-i, --id|TRIAL_ID|specify the trial id|Yes|
|-f, --file|FILE_NAME|Specify the name of the configuration file|Yes|
|-m, --metric|METRIC|input the metric of the trial|Yes|
|-p, --path|PATH|specify the path of the configuration file|No|

- runtrial



|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-i, --id|STUDY_ID|specify the study id|Yes|
|-f, --file|FILE_NAME|Specify the name of the configuration file|Yes|
|-n, --number|NUMBER|specify the number of iteration needed|Yes|
|-p, --path|PATH|specify the path of the configuration file|No|

- showstudy

|Option Flag|Arguments|Description|Required|
|-----------|---------|-----------|--------|
|-h, --help|| desplay help messages|No|
|-f, --file|FILE_NAME|Specify the name of the configuration file|Yes|
|-p, --path|PATH|specify the path of the configuration file|No|


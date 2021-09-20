# sbcli-furlan

Azure Service Bus CLI - v0.0.6

[![Python application](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-publish.yml/badge.svg)](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-publish.yml)
[![codecov](https://codecov.io/gh/guionardo/py-servicebus-cli/branch/develop/graph/badge.svg?token=DGRoPKyAwW)](https://codecov.io/gh/guionardo/py-servicebus-cli)
[![CodeQL](https://github.com/guionardo/py-servicebus-cli/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/guionardo/py-servicebus-cli/actions/workflows/codeql-analysis.yml)

## Table of Contents

- [sbcli-furlan](#sbcli-furlan)
  - [Install](#install)
  - [Help](#help)
    - [LIST](#list)
    - [QUEUE](#queue)
    - [TOPIC](#topic)
    - [DOWNLOAD](#download)
    - [UPLOAD](#upload)
    - [PROFILE](#profile)
  - [ToDo](#todo)

## Install

``` bash
pip install sbcli-furlan
```

## Help

``` bash
$ sbcli --help
usage: sbcli [-h] [--version] [--connection CONNECTION | --profile PROFILE]
             [--no-logging] [--debug]
             {list,queue,topic,download,upload,profile} ...

Azure Service Bus CLI

positional arguments:
  {list,queue,topic,download,upload,profile}
    list                List entities
    queue               Queue management
    download            Download message
    upload              Upload message
    profile             Connection profiles

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --connection CONNECTION
                        Service bus connection string (env
                        SB_CONNECTION_STRING)
  --profile PROFILE     Connection profile
  --no-logging
  --debug               Set debug level to log

You are using a version ahead (v0.0.6) of pypi (v0.0.5). Log file:
/home/guionardo/.log/sbcli.log
```

### LIST

``` bash
$ sbcli list --help
usage: sbcli list [-h] (--queue QUEUE | --topic TOPIC)
                  [--type {text,csv,table}]

optional arguments:
  -h, --help            show this help message and exit
  --queue QUEUE         Queue name (allow mask * and ?)
  --topic TOPIC         Topic name (allow mask * and ?)
  --type {text,csv,table}
```

### QUEUE

``` bash
$ sbcli queue --help
usage: sbcli queue [-h] (--create queue_name | --clear-dead-letter queue_name)

optional arguments:
  -h, --help            show this help message and exit
  --create queue_name   Create queue
  --clear-dead-letter queue_name
                        Empty dead letter queue
```

### TOPIC

``` bash
$ sbcli topic --help
usage: sbcli topic [-h] [--create]

optional arguments:
  -h, --help  show this help message and exit
  --create
```

### DOWNLOAD

``` bash
$ sbcli download --help
usage: sbcli download [-h] [--output OUTPUT] [--file-prefix FILE_PREFIX]
                      [--dead-letter] [--timeout TIMEOUT] [--peek]
                      (--queue QUEUE | --topic TOPIC) [--max-count MAX_COUNT]

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output folder (default = queue/topic name)
  --file-prefix FILE_PREFIX
                        Fileprefix
  --dead-letter         Dead letter queue
  --timeout TIMEOUT     Timeout in seconds
  --peek                Peek (does not complete message in queue)
  --queue QUEUE         Queue name
  --topic TOPIC         Topic name
  --max-count MAX_COUNT
                        Maximum message count
```

### UPLOAD

``` bash
$ sbcli upload --help
usage: sbcli upload [-h] --source SOURCE [--max-count MAX_COUNT]
                    (--queue QUEUE | --topic TOPIC)
                    [--no-move-sent | --move-sent FOLDER]

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       Source files (you can use mask)
  --max-count MAX_COUNT
                        Maximum message count
  --queue QUEUE         Queue name
  --topic TOPIC         Topic name
  --no-move-sent        No move sent files to ./sent folder
  --move-sent FOLDER    Move to folder after sucessfull sending
```

### PROFILE

``` bash
$ sbcli profile --help
usage: sbcli profile [-h]
                     (--set PROFILE | --delete PROFILE | --list | --default PROFILE)
                     [--connection CONNECTION] [--output {text,csv,table}]

optional arguments:
  -h, --help            show this help message and exit
  --set PROFILE         Set profile and connection string (add --connection
                        argument)
  --delete PROFILE      Delete profile
  --list                List profiles
  --default PROFILE     Set default profile
  --connection CONNECTION
                        Connection string (used with --set)
  --output {text,csv,table}
```


## ToDo

```
./src/cli/tool_topic.py:14:    # TODO: Implementar tool topic
./src/cli/tool_queue.py:18:    # TODO: Implementar criação de fila
./src/cli/tool_queue.py:23:    # TODO: Implementar limpeza de DLQ
./src/cli/tools/download.py:151:    # TODO: Implementar download de tópicos
```

# sbcli-furlan

Azure Service Bus CLI - v0.0.3

[![Python application](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-publish.yml/badge.svg)](https://github.com/guionardo/py-servicebus-cli/actions/workflows/python-publish.yml)
[![codecov](https://codecov.io/gh/guionardo/py-servicebus-cli/branch/main/graph/badge.svg?token=DGRoPKyAwW)](https://codecov.io/gh/guionardo/py-servicebus-cli)
[![CodeQL](https://github.com/guionardo/py-servicebus-cli/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/guionardo/py-servicebus-cli/actions/workflows/codeql-analysis.yml)

## Table of Contents

- [sbcli-furlan](#sbcli-furlan)
  - [Install](#install)
  - [Help](#help)
    - [LIST](#list)
    - [QUEUE](#queue)
    - [DOWNLOAD](#download)
    - [UPLOAD](#upload)

## Install

``` bash
pip install sbcli-furlan
```

## Help

``` bash
$ sbcli --help
usage: sbcli [-h] [--version] [--connection CONNECTION] [--no-logging]
             [--debug]
             {list,queue,download,upload} ...

Azure Service Bus CLI

positional arguments:
  {list,queue,download,upload}
    list                List entities
    queue               Queue management
    download            Download message
    upload              Upload message

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --connection CONNECTION
                        Service bus connection string (env
                        SB_CONNECTION_STRING)
  --no-logging
  --debug               Set debug level to log

Log file: /home/guionardo/.log/sbcli.log
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
usage: sbcli queue [-h]
                   (--list {text,csv,table} | --create CREATE | --clear-dead-leter CLEAR_DEAD_LETER)
                   [--filter FILTER]

optional arguments:
  -h, --help            show this help message and exit
  --list {text,csv,table}
  --create CREATE       Create queue
  --clear-dead-leter CLEAR_DEAD_LETER
                        Empty dead letter queue
  --filter FILTER       Filter for select queue name. You can use * and ?
```

### DOWNLOAD

``` bash
$ sbcli download --help
usage: sbcli download [-h] [--output OUTPUT] [--file-prefix FILE_PREFIX]
                      [--dead-letter] [--timeout TIMEOUT]
                      (--queue QUEUE | --topic TOPIC)
                      [--max-count MAX_COUNT | --all]

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output folder (default = queue/topic name)
  --file-prefix FILE_PREFIX
                        Fileprefix
  --dead-letter         Dead letter queue
  --timeout TIMEOUT     Timeout in seconds
  --queue QUEUE         Queue name
  --topic TOPIC         Topic name
  --max-count MAX_COUNT
                        Maximum message count
  --all                 Download all messages
```

### UPLOAD

``` bash
$ sbcli upload --help
usage: sbcli upload [-h] --source SOURCE [--max-count MAX_COUNT]
                    (--queue QUEUE | --topic TOPIC)

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       Source files (you can use mask)
  --max-count MAX_COUNT
                        Maximum message count
  --queue QUEUE         Queue name
  --topic TOPIC         Topic name
```


# dnsrelay

## Environment

* Ubuntu 18.04
* Python 3.6

## Dependency

`pip install -r requirements.txt`

## Usage

```plain
usage: ./relay [-h] [--cache engine] [--host host] [--log-level level] [-p port]

DNS relay server

optional arguments:
  -h, --help            show this help message and exit
  --cache engine        cache engine to use, default redis
  --host host           address to listen, default 0.0.0.0
  --log-level level     logging level, default DEBUG
  -p port, --port port  port to listen, default 53
```

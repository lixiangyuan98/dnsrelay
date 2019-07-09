# dnsrelay

## Environment

* Ubuntu 18.04
* Python 3.6
* Redis

## Dependency

`pip install -r requirements.txt`

## Usage

```plain
usage: relay [-h] [--cache engine] [--host host] [--host-file filename]
             [--log-level level] [-p port] --remote-host host

DNS relay server

optional arguments:
  -h, --help            show this help message and exit
  --cache engine        cache engine to use, default redis
  --host host           address to listen, default 0.0.0.0
  --host-file filename  host filename, default host.txt
  --log-level level     logging level, default DEBUG
  -p port, --port port  port to listen, default 53
  --remote-host host    remote DNS server
```

"""Command line arguments parsing"""
import argparse
import sys

_parser = argparse.ArgumentParser(description='DNS relay server')

_parser.add_argument('--log-level', metavar='level', type=str, dest='log_level', help='logging level',
                     choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='DEBUG')
_parser.add_argument('--host', metavar='host', type=str, dest='host',
                     help='address to listen, default 0.0.0.0', default='0.0.0.0')
_parser.add_argument('-p', '--port', metavar='port', type=int,
                     dest='port', help='port to listen, default 53', default=53)

parsed_args = _parser.parse_args()

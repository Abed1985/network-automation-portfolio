import argparse
import os
from getpass import getpass

from jnpr.junos import Device


def add_connection_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", required=True, help="Junos device hostname or lab IP")
    parser.add_argument("--user", default=os.getenv("JUNOS_USER"), help="Junos username; defaults to JUNOS_USER")
    parser.add_argument("--port", type=int, default=830, help="NETCONF port")


def open_device(args):
    username = args.user or input("Username: ")
    password = os.getenv("JUNOS_PASSWORD") or getpass("Password: ")
    return Device(host=args.host, user=username, passwd=password, port=args.port)

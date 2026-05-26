import argparse

from common import add_connection_args, open_device


def parse_args():
    parser = argparse.ArgumentParser(description="Print Junos version and hostname facts.")
    add_connection_args(parser)
    return parser.parse_args()


def main():
    args = parse_args()
    with open_device(args) as device:
        facts = device.facts
        print(f"Hostname: {facts.get('hostname')}")
        print(f"Model: {facts.get('model')}")
        print(f"Junos version: {facts.get('version')}")


if __name__ == "__main__":
    main()

import argparse

from jnpr.junos.utils.sw import SW

from common import add_connection_args, open_device


def parse_args():
    parser = argparse.ArgumentParser(description="Reboot a Junos device, guarded by an explicit confirmation flag.")
    add_connection_args(parser)
    parser.add_argument("--at", help="Schedule reboot time, for example '+10' or '23:30'")
    parser.add_argument("--confirm", action="store_true", help="Actually request the reboot")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.confirm:
        print("Dry run only: add --confirm to request a reboot")
        return

    with open_device(args) as device:
        software = SW(device)
        response = software.reboot(at=args.at) if args.at else software.reboot()
        print(response)


if __name__ == "__main__":
    main()

import argparse

from jnpr.junos.utils.config import Config

from common import add_connection_args, open_device


def parse_args():
    parser = argparse.ArgumentParser(description="Save, reload, delete, or inspect Junos rescue configuration.")
    add_connection_args(parser)
    parser.add_argument("action", choices=["save", "reload", "delete", "get"], help="Rescue configuration action")
    parser.add_argument("--commit", action="store_true", help="Apply state-changing rescue actions")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.action in ["save", "reload", "delete"] and not args.commit:
        print(f"Dry run only: add --commit to perform rescue action '{args.action}'")
        return

    with open_device(args) as device:
        with Config(device, mode="exclusive") as config:
            result = config.rescue(action=args.action)
            if result is False:
                print("No rescue configuration exists")
                return
            if args.action == "reload":
                # Reloading rescue config creates a candidate; commit confirmed protects recovery.
                config.commit(confirm=5, comment="Reload rescue configuration via PyEZ automation")
                print("Rescue configuration loaded with commit confirmed for 5 minutes")
            elif args.action in ["save", "delete"]:
                print(f"Rescue configuration action completed: {args.action}")
            else:
                print(result)


if __name__ == "__main__":
    main()

import argparse

from jnpr.junos.utils.sw import SW

from common import add_connection_args, open_device


def parse_args():
    parser = argparse.ArgumentParser(description="Install Junos software with validation and optional reboot.")
    add_connection_args(parser)
    parser.add_argument("package", help="Local or remote Junos package path")
    parser.add_argument("--checksum", default="sha256", help="Checksum algorithm used by Junos")
    parser.add_argument("--no-validate", action="store_true", help="Skip Junos configuration validation")
    parser.add_argument("--reboot", action="store_true", help="Reboot after successful install")
    parser.add_argument("--commit", action="store_true", help="Actually perform the install; otherwise dry-run")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.commit:
        print(f"Dry run only: would install {args.package} on {args.host}")
        return

    with open_device(args) as device:
        software = SW(device)
        ok, message = software.install(
            package=args.package,
            validate=not args.no_validate,
            checksum_algorithm=args.checksum,
        )
        print(f"Install status: {ok}; message: {message}")
        if ok and args.reboot:
            print(software.reboot())


if __name__ == "__main__":
    main()

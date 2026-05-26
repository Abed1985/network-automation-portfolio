import argparse

from jnpr.junos.utils.config import Config

from common import add_connection_args, open_device


def parse_args():
    parser = argparse.ArgumentParser(description="Load, compare, commit-confirm, or rollback Junos configuration.")
    add_connection_args(parser)
    parser.add_argument("--config", help="Path to a Junos set/text config file")
    parser.add_argument("--format", default="set", choices=["set", "text", "xml", "json"], help="Candidate config format")
    parser.add_argument("--commit", action="store_true", help="Commit after showing the diff")
    parser.add_argument("--sync", action="store_true", help="Use synchronized commit on dual-routing-engine systems")
    parser.add_argument("--confirm-minutes", type=int, default=5, help="Use commit confirmed for this many minutes")
    parser.add_argument("--rollback", type=int, help="Rollback ID to load instead of a config file")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.config and args.rollback is None:
        raise SystemExit("Provide --config or --rollback")

    with open_device(args) as device:
        with Config(device, mode="exclusive") as config:
            if args.rollback is not None:
                print(f"Loading rollback {args.rollback}")
                config.rollback(rb_id=args.rollback)
            else:
                print(f"Loading candidate configuration from {args.config}")
                config.load(path=args.config, format=args.format, merge=True)

            print("Candidate diff:")
            config.pdiff()

            if args.commit:
                # Commit confirmed protects the device: if the change is not confirmed later,
                # Junos automatically rolls it back after the timer expires.
                config.commit(confirm=args.confirm_minutes, sync=args.sync)
                print(f"Commit confirmed for {args.confirm_minutes} minutes")
            else:
                config.rollback()
                print("Dry run only: candidate configuration rolled back")


if __name__ == "__main__":
    main()

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path


PASSKEY_PATTERN = re.compile(r"TACPLUS\s+global\s+passkey\s+(?P<passkey>\S+)", re.IGNORECASE)


def extract_running_passkey(show_tacacs_output):
    match = PASSKEY_PATTERN.search(show_tacacs_output)
    if not match:
        raise ValueError("Could not find TACPLUS global passkey in command output")
    return match.group("passkey")


def update_tacacs_json(config, passkey):
    updated = deepcopy(config)
    try:
        updated["TACPLUS"]["global"]["passkey"] = passkey
    except KeyError as error:
        raise KeyError("Expected TACPLUS.global.passkey in JSON config") from error
    return updated


def parse_args():
    parser = argparse.ArgumentParser(description="Synchronize SONiC tacacs.json passkey from sanitized show tacacs output.")
    parser.add_argument("--show-tacacs", required=True, help="File containing show tacacs output")
    parser.add_argument("--json", required=True, help="tacacs.json input file")
    parser.add_argument("--output", default="artifacts/tacacs_updated.json")
    return parser.parse_args()


def main():
    args = parse_args()
    passkey = extract_running_passkey(Path(args.show_tacacs).read_text(encoding="utf-8"))
    config = json.loads(Path(args.json).read_text(encoding="utf-8"))
    updated = update_tacacs_json(config, passkey)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote updated TACACS config to {output_path}")


if __name__ == "__main__":
    main()

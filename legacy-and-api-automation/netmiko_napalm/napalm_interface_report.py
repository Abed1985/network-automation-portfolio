import argparse
import csv
import os
from datetime import date
from getpass import getpass

from napalm import get_network_driver


def parse_args():
    parser = argparse.ArgumentParser(description="Collect interface status with NAPALM and export CSV.")
    parser.add_argument("--hosts", required=True, help="Comma-separated host list")
    parser.add_argument("--driver", default="ios", help="NAPALM driver name, for example ios, nxos, junos")
    parser.add_argument("--username", default=os.getenv("LAB_ANSIBLE_USER"))
    parser.add_argument("--output", default=f"artifacts/napalm-interfaces-{date.today().isoformat()}.csv")
    return parser.parse_args()


def main():
    args = parse_args()
    username = args.username or input("Username: ")
    password = os.getenv("LAB_ANSIBLE_PASSWORD") or getpass("Password: ")
    driver = get_network_driver(args.driver)
    rows = []

    for host in [item.strip() for item in args.hosts.split(",") if item.strip()]:
        device = driver(hostname=host, username=username, password=password)
        device.open()
        interfaces = device.get_interfaces()
        device.close()
        for interface, details in interfaces.items():
            rows.append({"host": host, "interface": interface, "is_up": details.get("is_up"), "is_enabled": details.get("is_enabled"), "description": details.get("description", "")})

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["host", "interface", "is_up", "is_enabled", "description"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

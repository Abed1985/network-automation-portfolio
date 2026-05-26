import argparse
import csv
import os
from datetime import date

import requests


MERAKI_BASE_URL = "https://api.meraki.com/api/v1"


def parse_args():
    parser = argparse.ArgumentParser(description="Export Meraki device uplink details to CSV files.")
    parser.add_argument("--org-id", default=os.getenv("MERAKI_ORG_ID"), help="Meraki organization ID")
    parser.add_argument("--api-key", default=os.getenv("MERAKI_API_KEY"), help="Meraki Dashboard API key")
    parser.add_argument("--output-prefix", default="meraki-demo", help="Output filename prefix")
    return parser.parse_args()


def meraki_get(session, path):
    response = session.get(f"{MERAKI_BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def network_name(networks, network_id):
    for network in networks:
        if network["id"] == network_id:
            return network["name"]
    return "unknown-network"


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    if not args.org_id or not args.api_key:
        raise SystemExit("Set MERAKI_ORG_ID and MERAKI_API_KEY or pass --org-id and --api-key")

    session = requests.Session()
    session.headers.update({"X-Cisco-Meraki-API-Key": args.api_key, "Content-Type": "application/json"})

    networks = meraki_get(session, f"/organizations/{args.org_id}/networks")
    inventory = meraki_get(session, f"/organizations/{args.org_id}/inventory/devices")

    appliance_rows = []
    access_rows = []
    for device in inventory:
        if not device.get("networkId"):
            continue
        uplinks = meraki_get(session, f"/devices/{device['serial']}/appliance/uplinks/statuses") if device.get("model", "")[:2] in ["MX", "Z1", "Z3"] else []
        row_base = {
            "network": network_name(networks, device["networkId"]),
            "device": device.get("name") or device.get("serial"),
            "serial": device.get("serial"),
            "model": device.get("model"),
        }
        if uplinks:
            for uplink in uplinks:
                appliance_rows.append({**row_base, **uplink})
        else:
            access_rows.append(row_base)

    today = date.today().isoformat()
    write_csv(f"{args.output_prefix}-appliance-uplinks-{today}.csv", appliance_rows, ["network", "device", "serial", "model", "interface", "status", "ip", "gateway", "publicIp"])
    write_csv(f"{args.output_prefix}-inventory-{today}.csv", access_rows, ["network", "device", "serial", "model"])
    print(f"Wrote Meraki reports with prefix {args.output_prefix}")


if __name__ == "__main__":
    main()

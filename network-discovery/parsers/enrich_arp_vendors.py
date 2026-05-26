import argparse
import csv
import os
import time
from pathlib import Path

import requests


def normalize_mac(mac_address):
    cleaned = "".join(character for character in mac_address if character in "0123456789abcdefABCDEF").lower()
    if len(cleaned) != 12:
        raise ValueError(f"Invalid MAC address: {mac_address}")
    return ":".join(cleaned[index : index + 2] for index in range(0, 12, 2))


def load_cache(path):
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as csv_file:
        return {row["oui"]: row["vendor"] for row in csv.DictReader(csv_file)}


def save_cache(path, cache):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["oui", "vendor"])
        writer.writeheader()
        for oui, vendor in sorted(cache.items()):
            writer.writerow({"oui": oui, "vendor": vendor})


def lookup_vendor(oui, cache, offline=False, delay=1.0):
    if oui in cache:
        return cache[oui]
    if offline:
        return "unknown"

    response = requests.get(f"https://api.macvendors.com/{oui}", timeout=10)
    vendor = response.text if response.ok else "unknown"
    cache[oui] = vendor
    time.sleep(delay)
    return vendor


def parse_args():
    parser = argparse.ArgumentParser(description="Enrich ARP CSV rows with MAC vendor/OUI data.")
    parser.add_argument("input_csv", help="CSV containing ip_address and mac_address columns")
    parser.add_argument("--output", default="artifacts/arp_enriched.csv")
    parser.add_argument("--cache", default="artifacts/oui_cache.csv")
    parser.add_argument("--offline", action="store_true", help="Use cache only and do not query external vendor API")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between vendor API calls")
    return parser.parse_args()


def main():
    args = parse_args()
    cache_path = Path(args.cache)
    cache = load_cache(cache_path)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(args.input_csv, newline="", encoding="utf-8") as input_file, output_path.open("w", newline="", encoding="utf-8") as output_file:
        reader = csv.DictReader(input_file)
        fieldnames = list(reader.fieldnames or []) + ["normalized_mac", "oui", "vendor"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            mac = row.get("mac_address", "")
            try:
                normalized = normalize_mac(mac)
            except ValueError:
                row.update({"normalized_mac": "", "oui": "", "vendor": "invalid-mac"})
                writer.writerow(row)
                continue
            oui = normalized[:8]
            row.update({
                "normalized_mac": normalized,
                "oui": oui,
                "vendor": lookup_vendor(oui, cache, offline=args.offline, delay=args.delay),
            })
            writer.writerow(row)

    if not args.offline:
        save_cache(cache_path, cache)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

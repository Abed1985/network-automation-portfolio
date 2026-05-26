import argparse
import csv
import os
import subprocess
from pathlib import Path


SYS_DESCR_OID = "1.3.6.1.2.1.1.1.0"


def snmpget(host, community, version="2c", timeout=2):
    command = ["snmpget", "-v", version, "-c", community, "-t", str(timeout), host, SYS_DESCR_OID]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip() or result.stderr.strip()


def parse_args():
    parser = argparse.ArgumentParser(description="Probe SNMP sysDescr for a list of devices using local snmpget.")
    parser.add_argument("devices_csv", help="CSV with name,host columns")
    parser.add_argument("--community", default=os.getenv("SNMP_COMMUNITY", "public"))
    parser.add_argument("--version", default="2c")
    parser.add_argument("--output", default="artifacts/snmp_sysdescr.csv")
    parser.add_argument("--dry-run", action="store_true", help="Print intended probes without running snmpget")
    return parser.parse_args()


def main():
    args = parse_args()
    rows = []
    with open(args.devices_csv, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            name = row.get("name") or row.get("device") or row["host"]
            host = row["host"]
            if args.dry_run:
                rows.append({"name": name, "host": host, "status": "dry-run", "sysdescr": ""})
                continue
            ok, output = snmpget(host, args.community, args.version)
            rows.append({"name": name, "host": host, "status": "ok" if ok else "failed", "sysdescr": output})

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["name", "host", "status", "sysdescr"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

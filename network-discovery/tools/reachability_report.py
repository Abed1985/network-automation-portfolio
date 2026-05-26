import argparse
import csv
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def ping(host, count=2, timeout=2):
    system = platform.system().lower()
    if system == "windows":
        command = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        command = ["ping", "-c", str(count), "-W", str(timeout), host]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def load_devices(path):
    with open(path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            yield {"name": row.get("name") or row.get("device") or row["host"], "host": row["host"]}


def parse_args():
    parser = argparse.ArgumentParser(description="Create a CSV reachability report for network devices.")
    parser.add_argument("devices_csv", help="CSV with name,host columns")
    parser.add_argument("--output", default="artifacts/reachability.csv")
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def main():
    args = parse_args()
    devices = list(load_devices(args.devices_csv))
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {executor.submit(ping, device["host"]): device for device in devices}
        for future in as_completed(future_map):
            device = future_map[future]
            reachable = future.result()
            rows.append({"name": device["name"], "host": device["host"], "status": "reachable" if reachable else "unreachable"})

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["name", "host", "status"])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["name"]))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

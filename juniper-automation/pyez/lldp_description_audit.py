import argparse
import csv
from pathlib import Path


def load_lldp(path):
    with open(path, newline="", encoding="utf-8") as csv_file:
        return {row["local_interface"]: row["neighbor"] for row in csv.DictReader(csv_file)}


def load_descriptions(path):
    with open(path, newline="", encoding="utf-8") as csv_file:
        return {row["interface"]: row.get("description", "") for row in csv.DictReader(csv_file)}


def parse_args():
    parser = argparse.ArgumentParser(description="Compare Junos LLDP neighbors with interface descriptions.")
    parser.add_argument("--lldp", required=True, help="CSV with local_interface,neighbor columns")
    parser.add_argument("--descriptions", required=True, help="CSV with interface,description columns")
    parser.add_argument("--output", default="artifacts/junos_lldp_description_audit.csv")
    return parser.parse_args()


def main():
    args = parse_args()
    lldp = load_lldp(args.lldp)
    descriptions = load_descriptions(args.descriptions)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["interface", "lldp_neighbor", "description", "match"])
        writer.writeheader()
        for interface, neighbor in sorted(lldp.items()):
            description = descriptions.get(interface, "")
            writer.writerow({
                "interface": interface,
                "lldp_neighbor": neighbor,
                "description": description,
                "match": str(neighbor.lower() in description.lower()),
            })
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

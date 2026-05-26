# FortiGate and FortiManager Automation

This section curates FortiGate/FortiManager work from the larger `net_aut/FORTIGATE` folder into public-safe examples.

The original folder contains useful automation patterns, but also raw threat feeds, product-specific ZTP assets, FortiManager environment details, generated files, logs, spreadsheets, binaries, and hardcoded credentials. This public version keeps the reusable engineering ideas and replaces environment-specific data with documentation-safe examples.

## What It Demonstrates

- FortiGate address object rendering from CSV with Jinja2.
- FortiGate configuration parsing/export to CSV for policy and address reviews.
- FortiGate operational health checks for VDOM, BGP, and IPsec status.
- FortiManager ADOM workspace and object-management patterns with Ansible.
- Generic SD-WAN/BGP overlay template rendering for ZTP-style workflows.

## Sections

| Section | Purpose |
| --- | --- |
| `object-generation` | Render FortiGate firewall address objects from CSV input. |
| `config-parsing` | Export FortiGate firewall address/policy blocks to CSV. |
| `operational-health` | Collect and parse BGP/IPsec health output. |
| `fortimanager-ztp` | Demonstrate FortiManager workspace, object, and SD-WAN template patterns. |

## Examples

Render FortiGate address objects:

```bash
cd fortigate-automation/object-generation
python render_address_objects.py --csv sample_addresses.csv
```

Parse FortiGate policy or address config blocks:

```bash
cd fortigate-automation/config-parsing
python fortigate_config_to_csv.py sample_fortigate.conf --type policy --output artifacts/policies.csv
python fortigate_config_to_csv.py sample_fortigate.conf --type address --output artifacts/addresses.csv
```

Parse saved BGP/IPsec command output:

```bash
cd fortigate-automation/operational-health
python parse_health_outputs.py sample_bgp_summary.txt --type bgp --output artifacts/bgp.csv
python parse_health_outputs.py sample_ipsec_summary.txt --type ipsec --output artifacts/ipsec.csv
```

Render a generic SD-WAN/BGP overlay template:

```bash
cd fortigate-automation/fortimanager-ztp
ansible-playbook playbooks/render_sdwan_template.yml
```

## Sanitization Notes

- No original FortiGate/FortiManager credentials are included.
- No raw threat-feed IP lists are included; sample inputs use documentation ranges.
- No customer spreadsheets, binaries, diagrams, Rundeck jobs, logs, or generated ZTP artifacts are included.
- FortiManager examples use environment-sourced credentials and minimal generic ADOM names.
- Device-touching examples default to dry-run or require normal Ansible execution against a local lab inventory.

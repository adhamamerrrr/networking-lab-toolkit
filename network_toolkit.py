"""Educational IP addressing and VLSM tools; no network configuration changes."""
import argparse
import csv
import ipaddress
import json


def describe_network(cidr):
    network = ipaddress.ip_network(cidr, strict=False)
    result = {
        "network": str(network),
        "version": network.version,
        "prefix_length": network.prefixlen,
        "netmask": str(network.netmask),
        "address_count": network.num_addresses,
    }
    if network.version == 4:
        usable = network.num_addresses if network.prefixlen >= 31 else network.num_addresses - 2
        first = network.network_address if network.prefixlen >= 31 else network.network_address + 1
        last = network.broadcast_address if network.prefixlen >= 31 else network.broadcast_address - 1
        result.update(broadcast=str(network.broadcast_address), usable_hosts=usable,
                      first_host=str(first), last_host=str(last),
                      wildcard_mask=str(network.hostmask))
    else:
        result["note"] = "IPv6 has no broadcast address. Address count is not a device capacity recommendation."
    return result


def plan_vlsm(cidr, host_requests):
    """Allocate conventional IPv4 LANs, largest first, reserving network/broadcast."""
    network = ipaddress.ip_network(cidr, strict=True)
    if network.version != 4:
        raise ValueError("VLSM planning supports IPv4 only.")
    if not host_requests or any(type(h) is not int or h <= 0 for h in host_requests):
        raise ValueError("Provide positive integer host requirements.")
    cursor = int(network.network_address)
    limit = int(network.broadcast_address)
    allocations = []
    for index, hosts in sorted(enumerate(host_requests), key=lambda item: (-item[1], item[0])):
        host_bits = max(2, (hosts + 1).bit_length())
        if host_bits > 32:
            raise ValueError("Host requirement exceeds the IPv4 address space.")
        block_size = 1 << host_bits
        aligned = ((cursor + block_size - 1) // block_size) * block_size
        if aligned + block_size - 1 > limit:
            raise ValueError("Requested subnets do not fit inside the parent network.")
        subnet = ipaddress.ip_network((aligned, 32 - host_bits))
        allocations.append({"request_index": index + 1, "requested_hosts": hosts,
                            **describe_network(str(subnet))})
        cursor = aligned + block_size
    return allocations



def read_host_requests(path):
    """Read positive host counts from a CSV with a 'hosts' header."""
    with open(path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or "hosts" not in reader.fieldnames:
            raise ValueError("Input CSV requires a hosts column.")
        values = []
        for line, row in enumerate(reader, 2):
            raw = (row.get("hosts") or "").strip()
            if not raw.isdecimal() or int(raw) < 1:
                raise ValueError(f"CSV line {line}: hosts must be positive integers.")
            values.append(int(raw))
    if not values:
        raise ValueError("Input CSV contains no host requests.")
    return values


def export_allocations(path, allocations):
    """Create a CSV export without overwriting an existing file."""
    fields = ("request_index", "requested_hosts", "network", "prefix_length",
              "netmask", "broadcast", "usable_hosts", "first_host", "last_host")
    with open(path, "x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(allocations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Describe an IPv4 or IPv6 network")
    inspect.add_argument("cidr")
    vlsm = commands.add_parser("vlsm", help="Allocate conventional IPv4 LAN subnets")
    vlsm.add_argument("cidr")
    vlsm.add_argument("hosts", nargs="*", type=int)
    vlsm.add_argument("--input-csv", help="CSV with a hosts column")
    vlsm.add_argument("--output-csv", help="Create CSV allocation report")
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            result = describe_network(args.cidr)
        else:
            if args.input_csv and args.hosts:
                raise ValueError("Use positional hosts or --input-csv, not both.")
            hosts = read_host_requests(args.input_csv) if args.input_csv else args.hosts
            result = plan_vlsm(args.cidr, hosts)
            if args.output_csv:
                export_allocations(args.output_csv, result)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

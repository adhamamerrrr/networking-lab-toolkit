"""Educational IP addressing and VLSM tools; no network configuration changes."""
import argparse
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Describe an IPv4 or IPv6 network")
    inspect.add_argument("cidr")
    vlsm = commands.add_parser("vlsm", help="Allocate conventional IPv4 LAN subnets")
    vlsm.add_argument("cidr")
    vlsm.add_argument("hosts", nargs="+", type=int)
    args = parser.parse_args()
    try:
        result = describe_network(args.cidr) if args.command == "inspect" else plan_vlsm(args.cidr, args.hosts)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

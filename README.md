# Networking Lab Toolkit

A small Python command-line toolkit for IP addressing, subnet inspection and IPv4 VLSM planning.

## Project provenance

This is a new educational portfolio implementation created in October 2026 to rebuild a lost-code portfolio. It demonstrates networking topics from my training; it is not recovered internship code, a production deployment, or evidence of a tool used at Xceed. The implementation was developed with AI assistance and should be reviewed, understood and extended before presenting it in an interview.

## Run locally

Requires Python 3.9 or later. No third-party packages are needed.

```bash
python network_toolkit.py inspect 192.168.10.45/24
python network_toolkit.py inspect 2001:db8::1/64
python network_toolkit.py vlsm 192.168.10.0/24 60 30 10
python -m unittest -v
printf 'hosts\n60\n30\n10\n' > hosts.csv
python network_toolkit.py vlsm 192.168.10.0/24 --input-csv hosts.csv --output-csv allocations.csv
```

The VLSM example allocates `192.168.10.0/26`, `192.168.10.64/27` and `192.168.10.96/28`, supporting 62, 30 and 14 conventional LAN hosts respectively. Results use JSON so they can be inspected or reused in other scripts. Allocations retain each request's original index and are generated largest first.

## Concepts demonstrated

- IPv4 and IPv6 CIDR notation and network masks.
- Network, broadcast, host range and IPv4 wildcard masks.
- VLSM allocation, prefix alignment and address-space limits.
- Input validation and automated checks for overlapping allocations.

The inspector treats IPv4 `/31` as a two-address point-to-point network and `/32` as one host. The planner deliberately reserves network and broadcast addresses and uses at least `/30` for conventional LAN allocations. It does not configure routers, DHCP servers, DNS servers, NAT or network interfaces.

## Interview walkthrough

1. Explain why 60 conventional LAN hosts need 64 addresses, producing `/26`.
2. Explain why larger requests are allocated first and why each block must be aligned.
3. Compare IPv4 broadcast with IPv6 addressing.
4. Explain how the tests prove capacity, containment and non-overlap.
5. Discuss what real deployment would additionally require: gateway selection, VLANs, DHCP scopes, routing and operational validation.

## Next improvements

- Add a graphical interface for reviewing CSV allocation reports.
- A small web interface for visual subnet planning.
- Separate Packet Tracer/GNS3 labs with authentic configuration files and screenshots.

No license has been selected yet.

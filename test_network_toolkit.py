import ipaddress
import unittest
from network_toolkit import describe_network, plan_vlsm


class NetworkingTests(unittest.TestCase):
    def test_ipv4_normalization(self):
        result = describe_network("192.168.10.45/24")
        self.assertEqual(result["network"], "192.168.10.0/24")
        self.assertEqual(result["usable_hosts"], 254)
        self.assertEqual(result["broadcast"], "192.168.10.255")

    def test_point_to_point_and_single_host(self):
        self.assertEqual(describe_network("192.0.2.0/31")["usable_hosts"], 2)
        self.assertEqual(describe_network("192.0.2.1/32")["first_host"], "192.0.2.1")

    def test_ipv6(self):
        result = describe_network("2001:db8::1/64")
        self.assertEqual(result["address_count"], 2**64)
        self.assertNotIn("broadcast", result)

    def test_known_vlsm_plan(self):
        result = plan_vlsm("192.168.10.0/24", [10, 60, 30])
        self.assertEqual([r["network"] for r in result],
                         ["192.168.10.0/26", "192.168.10.64/27", "192.168.10.96/28"])
        self.assertEqual([r["request_index"] for r in result], [2, 3, 1])

    def test_allocation_invariants(self):
        result = plan_vlsm("10.0.0.0/16", [1, 2, 3, 14, 15, 62, 63, 1000])
        parent = ipaddress.ip_network("10.0.0.0/16")
        for i, row in enumerate(result):
            subnet = ipaddress.ip_network(row["network"])
            self.assertTrue(subnet.subnet_of(parent))
            self.assertGreaterEqual(row["usable_hosts"], row["requested_hosts"])
            for earlier in result[:i]:
                self.assertFalse(subnet.overlaps(ipaddress.ip_network(earlier["network"])))

    def test_invalid_or_impossible_requests(self):
        for requests in ([], [0], [-1], [True], [255], [2**32]):
            with self.assertRaises(ValueError):
                plan_vlsm("192.168.10.0/24", requests)
        with self.assertRaises(ValueError):
            plan_vlsm("2001:db8::/64", [10])
        with self.assertRaises(ValueError):
            plan_vlsm("192.168.10.1/24", [10])


if __name__ == "__main__":
    unittest.main()

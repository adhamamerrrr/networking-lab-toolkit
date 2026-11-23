"""CSV import/export integration checks for VLSM planner."""
import csv
import tempfile
import unittest
from pathlib import Path

from network_toolkit import read_host_requests, export_allocations, plan_vlsm


class CsvWorkflowTests(unittest.TestCase):
    def test_import_and_export(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "requests.csv"
            source.write_text("hosts\n60\n30\n10\n", encoding="utf-8")
            allocations = plan_vlsm("192.168.10.0/24", read_host_requests(source))
            self.assertEqual([a["network"] for a in allocations],
                             ["192.168.10.0/26", "192.168.10.64/27", "192.168.10.96/28"])
            output = Path(folder) / "plan.csv"
            export_allocations(output, allocations)
            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["usable_hosts"], "62")
            with self.assertRaises(FileExistsError):
                export_allocations(output, allocations)

    def test_invalid_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "requests.csv"
            for value in ("", "abc", "-3", "0", "2.5"):
                source.write_text("hosts\n" + value + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_host_requests(source)


if __name__ == "__main__":
    unittest.main()

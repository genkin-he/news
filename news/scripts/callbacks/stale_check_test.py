import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

import stale_check

NOW = datetime(2026, 11, 19, 18, 0, 0)


class StaleCheckTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.root, "data")
        self.state_path = os.path.join(self.root, "stale_alert.json")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _write_source(self, name, pub_dates, wrap=True):
        os.makedirs(os.path.join(self.data_dir, name), exist_ok=True)
        items = [{"title": "t", "pub_date": d} for d in pub_dates]
        payload = {"data": items} if wrap else items
        with open(os.path.join(self.data_dir, name, "list.json"), "w") as f:
            json.dump(payload, f)

    def _hours_ago(self, hours):
        return (NOW - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    def test_reports_sources_without_recent_posts(self):
        self._write_source("fresh", [self._hours_ago(1)])
        self._write_source("stale", [self._hours_ago(100), self._hours_ago(200)])

        stale = stale_check.find_stale_sources(self.data_dir, NOW, frozenset())

        self.assertEqual([name for name, _ in stale], ["stale"])

    def test_uses_newest_post_regardless_of_order(self):
        self._write_source("mixed", [self._hours_ago(200), self._hours_ago(2)])

        self.assertEqual(stale_check.find_stale_sources(self.data_dir, NOW, frozenset()), [])

    def test_skips_ignored_and_undatable_sources(self):
        self._write_source("disabled", [self._hours_ago(500)])
        self._write_source("no_dates", [])
        self._write_source("bare_list", [self._hours_ago(500)], wrap=False)
        os.makedirs(os.path.join(self.data_dir, "broken"))
        with open(os.path.join(self.data_dir, "broken", "list.json"), "w") as f:
            f.write("{not json")

        stale = stale_check.find_stale_sources(
            self.data_dir, NOW, frozenset({"disabled"})
        )

        self.assertEqual([name for name, _ in stale], ["bare_list"])

    def test_report_is_rate_limited(self):
        self._write_source("stale", [self._hours_ago(100)])

        first = stale_check.build_report(self.data_dir, self.state_path, NOW)
        second = stale_check.build_report(
            self.data_dir, self.state_path, NOW + timedelta(hours=1)
        )
        later = stale_check.build_report(
            self.data_dir, self.state_path, NOW + timedelta(hours=25)
        )

        self.assertIn("stale", first)
        self.assertIsNone(second)
        self.assertIn("stale", later)

    def test_no_report_and_no_state_write_when_all_fresh(self):
        self._write_source("fresh", [self._hours_ago(1)])

        self.assertIsNone(stale_check.build_report(self.data_dir, self.state_path, NOW))
        self.assertFalse(os.path.exists(self.state_path))


if __name__ == "__main__":
    unittest.main()

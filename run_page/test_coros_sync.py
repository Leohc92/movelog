import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import coros_sync


class CorosSyncTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.output = Path(self.folder.name) / "activities.json"
        self.old = [{"coros_id": "old", "start_date": "2025-01-01T00:00:00Z"}]
        self.output.write_text(json.dumps(self.old))
        self.before = self.output.read_bytes()

    def test_empty_account_does_not_erase_published_activities(self):
        responses = [
            {"data": {"accessToken": "test-token"}},
            {"data": {"dataList": []}},
        ]
        with patch.object(coros_sync, "request_json", side_effect=responses):
            with self.assertRaises(RuntimeError):
                coros_sync.sync("test", "test", self.output)
        self.assertEqual(self.output.read_bytes(), self.before)

    def test_failed_download_keeps_existing_publication(self):
        responses = [
            {"data": {"accessToken": "test-token"}},
            {"data": {"dataList": [{"labelId": "new", "sportType": 902}]}},
            {"data": {"dataList": []}},
            {"data": {}},
        ]
        with patch.object(coros_sync, "request_json", side_effect=responses):
            with self.assertRaises(RuntimeError):
                coros_sync.sync("test", "test", self.output)
        self.assertEqual(self.output.read_bytes(), self.before)

    def test_zero_distance_workout_uses_its_own_sport_type(self):
        responses = [
            {"data": {"accessToken": "test-token"}},
            {"data": {"dataList": [{"labelId": "new", "sportType": 902}]}},
            {"data": {"dataList": []}},
            {"data": {"fileUrl": "https://oss.coros.com/test.fit"}},
        ]
        activity = {
            "coros_id": "new",
            "start_date": "2026-01-01T00:00:00Z",
            "type": "StairStepper",
            "distance": 0,
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"fixture"
        with patch.object(coros_sync, "request_json", side_effect=responses) as request:
            with patch.object(
                coros_sync.urllib.request, "urlopen", return_value=response
            ):
                with patch.object(
                    coros_sync, "read_activity", return_value=activity
                ) as parse:
                    coros_sync.sync("test", "test", self.output)
        self.assertIn("sportType=902", request.call_args_list[-1].args[0])
        self.assertEqual(parse.call_args.args[2], 902)
        self.assertEqual(json.loads(self.output.read_text()), [activity])

    def test_already_imported_activities_do_not_download_again(self):
        old = {
            "coros_id": "old",
            "coros_fit_imported": True,
            "start_date": "2025-01-01T00:00:00Z",
        }
        self.output.write_text(json.dumps([old]))
        responses = [
            {"data": {"accessToken": "test-token"}},
            {"data": {"dataList": [{"labelId": "old", "sportType": 100}]}},
            {"data": {"dataList": []}},
        ]
        with patch.object(coros_sync, "request_json", side_effect=responses):
            with patch.object(coros_sync.urllib.request, "urlopen") as download:
                coros_sync.sync("test", "test", self.output)
        download.assert_not_called()
        self.assertEqual(json.loads(self.output.read_text()), [old])


if __name__ == "__main__":
    unittest.main()

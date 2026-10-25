import unittest
from unittest.mock import Mock, patch

import requests

from integrations.github_releases import fetch_latest_release, parse_github_repo
from integrations.tibia_com import parse_tibia_datetime
from integrations.tibiadata import _get_json


class IntegrationTests(unittest.TestCase):
    def test_parse_github_repo(self):
        self.assertEqual(
            parse_github_repo("https://github.com/openai/example-repo"),
            ("openai", "example-repo"),
        )
        self.assertIsNone(parse_github_repo("https://example.com/nope"))

    @patch("integrations.github_releases.requests.get")
    def test_fetch_latest_release(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.text = "ok"
        response.json.return_value = {"tag_name": "v1.2.3", "html_url": "https://github.com/openai/example-repo/releases/tag/v1.2.3"}
        mock_get.return_value = response

        info = fetch_latest_release("openai", "example-repo")
        self.assertEqual(info.tag, "v1.2.3")
        self.assertIn("releases/tag", info.html_url)

    def test_parse_tibia_datetime(self):
        dt = parse_tibia_datetime("Jan 22 2026, 10:42:00 CET")
        self.assertIsNotNone(dt)
        self.assertEqual((dt.year, dt.month, dt.day), (2026, 1, 22))

    @patch("integrations.tibiadata.time.sleep")
    @patch("integrations.tibiadata.requests.get")
    def test_tibiadata_does_not_retry_missing_resources(self, mock_get, mock_sleep):
        response = Mock(status_code=404)
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        mock_get.return_value = response

        with self.assertRaises(requests.HTTPError):
            _get_json("https://api.tibiadata.com/v5/character/missing", timeout=1)

        mock_get.assert_called_once()
        mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()

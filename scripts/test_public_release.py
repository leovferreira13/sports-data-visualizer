"""Regression checks for release inspection; all responses are synthetic."""
import argparse
import unittest
from unittest.mock import patch

from check_public_release import Page, public_origin, run


class ReleaseInspectionTests(unittest.TestCase):
    def test_optimized_logo_is_recognized_without_accepting_an_unrelated_image(self):
        page = Page()
        page.feed('<img alt="Logo" src="/_next/image?url=%2Fbranding%2Fhudl-statsbomb-logo-reversed.png&amp;w=1920&amp;q=75">')
        self.assertTrue(page.logo)
        for html in ('<img src="/branding/hudl-statsbomb-logo-reversed.png">', '<img alt="Logo" src="/unrelated.png">'):
            page = Page()
            page.feed(html)
            self.assertFalse(page.logo)

    def test_public_target_rejects_credentials_and_paths(self):
        self.assertEqual(public_origin("https://portfolio.example/"), "https://portfolio.example")
        for value in ("http://portfolio.example", "https://user:secret@portfolio.example", "https://portfolio.example/en"):
            with self.assertRaises(argparse.ArgumentTypeError):
                public_origin(value)

    def test_a_failed_model_response_cannot_report_a_pass(self):
        with patch("check_public_release.request", return_value=(503, {}, b"unavailable")), patch("check_public_release.check_metadata"), patch.dict("os.environ", {"SITE_URL": "https://portfolio.example"}):
            report = run("https://portfolio.example")
        model = next(c for c in report["checks"] if c["name"] == "reviewed-model")
        self.assertEqual(model["status"], "FAIL")
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["release_complete"])


if __name__ == "__main__":
    unittest.main()

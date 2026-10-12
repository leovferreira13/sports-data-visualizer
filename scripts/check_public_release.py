#!/usr/bin/env python3
"""Check a public release without credentials or a private training runtime."""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen

from check_portfolio_metadata import check as check_metadata


ROUTES = {"en": "en", "br": "pt-BR", "nl": "nl", "es": "es", "de": "de"}


def public_origin(value):
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https" or not parsed.hostname or parsed.username
        or parsed.password or parsed.port not in (None, 443)
        or parsed.path not in ("", "/") or parsed.query or parsed.fragment
    ):
        raise argparse.ArgumentTypeError("Use an HTTPS origin without credentials, path, query, fragment or nonstandard port")
    return value.rstrip("/")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.language = None
        self.methodology = False
        self.logo = False
        self.source = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        self.methodology |= attrs.get("id") == "methodology"
        if tag == "a":
            self.source |= attrs.get("href") == "https://github.com/hudl/open-data"
        if tag == "img":
            source = attrs.get("src", "")
            parsed = urlsplit(source)
            if parsed.path == "/_next/image":
                source = parse_qs(parsed.query).get("url", [""])[0]
            self.logo |= source == "/branding/hudl-statsbomb-logo-reversed.png" and bool(attrs.get("alt"))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url, headers=None, redirect=True):
    req = Request(url, headers=headers or {})
    try:
        if redirect:
            response = urlopen(req, timeout=20)
        else:
            response = build_opener(NoRedirect()).open(req, timeout=20)
        with response:
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()


def run(origin):
    report = {
        "schema_version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "origin": origin,
        "checkout_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "deployed_revision": None,
        "deployment_id": None,
        "remote_build_id": None,
        "authentication_used": False,
        "checks": [],
        "model": None,
        "release_complete": False,
        "limits": [
            "HTTP checks do not prove browser interaction, source/build identity, repository visibility, history review or exact branding guidance.",
            "Run browser QA separately; record deployment identity from Railway.",
        ],
    }

    def verify(name, action):
        try:
            action()
            report["checks"].append({"name": name, "status": "PASS"})
        except Exception as error:
            report["checks"].append({"name": name, "status": "FAIL", "reason": f"{type(error).__name__}: {error}"})

    for route, locale in ROUTES.items():
        def page_check(route=route, locale=locale):
            status, _, body = request(f"{origin}/{route}")
            assert status == 200, f"/{route}: HTTP {status}"
            page = Page()
            page.feed(body.decode())
            assert page.language == locale, f"/{route}: incorrect document language"
            assert page.methodology and page.logo and page.source, f"/{route}: missing methodology/source/logo"
            status, headers, _ = request(f"{origin}/{route}/methodology", redirect=False)
            assert status == 307, f"/{route}/methodology: HTTP {status}"
            assert headers.get("Location") in (f"/{route}#methodology", f"{origin}/{route}#methodology"), f"/{route}: incorrect anchor redirect"
        verify(f"route:{route}", page_check)

    def preferences():
        cases = [
            ({"Accept-Language": "pt-BR"}, "br"),
            ({"Accept-Language": "nl-NL"}, "nl"),
            ({"Accept-Language": "es-MX"}, "es"),
            ({"Accept-Language": "de-DE"}, "de"),
            ({"Accept-Language": "fr-FR"}, "en"),
            ({"Accept-Language": "pt-BR", "Cookie": "football-visualized-locale=en"}, "en"),
        ]
        for headers, expected in cases:
            status, response_headers, _ = request(origin + "/", headers, redirect=False)
            assert status in (307, 308), f"root: HTTP {status}"
            assert response_headers.get("Location") in (f"/{expected}", f"{origin}/{expected}"), f"root: expected /{expected}"
        assert request(origin + "/fr")[0] == 404, "invalid locale must return 404"
    verify("locale-preferences-and-invalid-route", preferences)

    def model():
        status, headers, raw = request(origin + "/model/selected-model.json")
        assert status == 200, f"model: HTTP {status}"
        expected = json.loads(Path("docs/reports/xg-artifact-distribution-review.json").read_text())
        digest = hashlib.sha256(raw).hexdigest()
        report["model"] = {"bytes": len(raw), "sha256": digest, "content_type": headers.get("Content-Type")}
        assert digest == expected["file_sha256"], "served model checksum differs from reviewed envelope"
        envelope = json.loads(raw)
        assert envelope["artifact_id"] == expected["artifact_id"], "served artifact identity differs"
    verify("reviewed-model", model)

    def metadata():
        assert os.environ.get("SITE_URL", "").rstrip("/") == origin, "Set SITE_URL to the checked origin"
        check_metadata(origin, origin)
    verify("portfolio-metadata-image-robots-sitemap", metadata)
    report["status"] = "PASS" if all(x["status"] == "PASS" for x in report["checks"]) else "FAIL"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, type=public_origin)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.base_url)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)

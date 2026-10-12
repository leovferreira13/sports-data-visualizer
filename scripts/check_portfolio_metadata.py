#!/usr/bin/env python3
"""Inspect the actual production HTML/assets; SITE_URL must match the build."""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.links = []
        self.anchors = []
        self.title = ""
        self.in_title = False
        self.in_head = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property"))] = attrs.get("content")
        elif tag == "link":
            self.links.append(attrs)
        elif tag == "a":
            self.anchors.append(attrs.get("href"))
        elif tag == "title" and self.in_head:
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def check(base, origin):
    routes = {"en": "en", "br": "pt-BR", "nl": "nl", "es": "es", "de": "de"}
    expected = {locale: f"{origin}/{route}" for route, locale in routes.items()}
    expected["x-default"] = f"{origin}/en"
    for route, locale in routes.items():
        with urlopen(f"{base}/{route}", timeout=20) as response:
            html = response.read().decode()
        parsed = Head()
        parsed.feed(html)
        copy = json.loads(Path(f"locales/{locale}.json").read_text())["meta"]
        assert parsed.title == copy["title"], route
        assert parsed.meta["description"] == copy["description"], route
        assert parsed.meta["og:title"] == copy["title"], route
        assert parsed.meta["twitter:card"] == "summary_large_image", route
        assert "https://www.linkedin.com/in/leonardo-v-ferreira" in parsed.anchors, route
        assert "https://github.com/leovferreira13" in parsed.anchors, route
        assert "https://github.com/leovferreira13/sports-data-visualizer" in parsed.anchors, route
        assert "https://github.com/hudl/open-data" in parsed.anchors, route
        canonical = [link.get("href") for link in parsed.links if link.get("rel") == "canonical"]
        alternates = {link["hreflang"]: link["href"] for link in parsed.links if "hreflang" in link}
        if origin:
            assert canonical == [f"{origin}/{route}"], f"/{route}: expected canonical {origin}/{route}, got {canonical}"
            assert alternates == expected, route
            assert parsed.meta["og:url"] == f"{origin}/{route}", route
            assert parsed.meta["og:image"] == f"{origin}/portfolio/share.png", route
            assert parsed.meta["twitter:image"] == parsed.meta["og:image"], route
            assert parsed.meta["og:image:alt"] == copy["imageAlt"], route
            assert parsed.meta["twitter:image:alt"] == copy["imageAlt"], route
            assert parsed.meta["robots"] == "index, follow", route
        else:
            assert not canonical and not alternates, route
            assert "og:url" not in parsed.meta and "og:image" not in parsed.meta, route
            assert "twitter:image" not in parsed.meta, route
            assert parsed.meta["robots"] == "noindex, nofollow", route
        icons = [link["href"] for link in parsed.links if link.get("rel") == "icon"]
        assert icons, route
        with urlopen(base + icons[0], timeout=20) as response:
            assert response.status == 200
    with urlopen(f"{base}/robots.txt", timeout=20) as response:
        robots = response.read().decode()
    assert ("Allow: /" in robots and f"Sitemap: {origin}/sitemap.xml" in robots) if origin else ("Disallow: /" in robots and "Sitemap:" not in robots)
    with urlopen(f"{base}/sitemap.xml", timeout=20) as response:
        sitemap = ET.fromstring(response.read())
    urls = [node.text for node in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert sorted(urls) == sorted(f"{origin}/{route}" for route in routes) if origin else not urls
    with urlopen(f"{base}/portfolio/share.png", timeout=20) as response:
        content = response.read()
        assert content[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(content[16:20], "big") == 1200
        assert int.from_bytes(content[20:24], "big") == 630
    print(f"PASS: portfolio HTML, authorship, image/icon, robots and sitemap in five locales ({'configured' if origin else 'unconfigured'} origin)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    check(args.base_url.rstrip("/"), os.environ.get("SITE_URL", "").rstrip("/"))

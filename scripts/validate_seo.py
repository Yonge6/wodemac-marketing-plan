#!/usr/bin/env python3
"""Check the served-page SEO contract and local navigation/assets (no packages)."""
from __future__ import annotations

import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "partners.html", "faq.html", "materials.html", "cases.html", "materials-preview.html"]
NOINDEX = {"cases.html", "materials-preview.html"}
errors: list[str] = []


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.head = False
        self.tag_counts: dict[str, int] = {}
        self.metas: dict[str, list[str]] = {}
        self.canonicals: list[str] = []
        self.refs: list[str] = []
        self.ids: list[str] = []
        self.material_ids: list[str] = []
        self.faq_count = 0
        self.text: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "head":
            self.head = True
        if tag in ("head", "title", "h1"):
            self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        if self.head and tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas.setdefault(key, []).append(a.get("content") or "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href") or "")
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key] or "")
        if a.get("id"):
            self.ids.append(a["id"] or "")
        if a.get("data-asset-id"):
            self.material_ids.append(a["data-asset-id"] or "")
        if tag == "article" and "seo-faq" in (a.get("class") or "").split():
            self.faq_count += 1
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.head = False
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.text.append(data)


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


pages: dict[str, Page] = {}
for filename in PAGES:
    source = (ROOT / filename).read_text()
    page = Page()
    page.feed(source)
    pages[filename] = page
    for tag in ("head", "title", "h1"):
        check(page.tag_counts.get(tag) == 1, f"{filename}: expected one {tag}")
    for name in ("description", "robots", "og:title", "og:description", "og:url", "og:image"):
        check(len(page.metas.get(name, [])) == 1, f"{filename}: expected one {name} meta")
    check(len(page.canonicals) == 1, f"{filename}: expected one canonical")
    if page.canonicals:
        canonical = page.canonicals[0]
        expected_path = "/" if filename == "index.html" else "/" + filename
        check(urlparse(canonical).path == expected_path, f"{filename}: canonical points to a different page")
        check(page.metas.get("og:url") == [canonical], f"{filename}: og:url differs from canonical")
    noindex = "noindex" in ",".join(page.metas.get("robots", []))
    check(noindex == (filename in NOINDEX), f"{filename}: unexpected index/noindex state")
    check(len(page.ids) == len(set(page.ids)), f"{filename}: duplicate HTML IDs")
    check("fonts.googleapis.com" not in source and "fonts.gstatic.com" not in source, f"{filename}: external Google Font dependency")
    visible = " ".join(" ".join(page.text).split())
    faq_count = 0
    for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', source, re.S | re.I):
        try:
            data = json.loads(raw)
        except ValueError as error:
            errors.append(f"{filename}: invalid JSON-LD: {error}")
            continue
        for entity in data.get("@graph", [data]):
            if entity.get("@type") == "FAQPage":
                for question in entity.get("mainEntity", []):
                    faq_count += 1
                    for text in (question.get("name", ""), question.get("acceptedAnswer", {}).get("text", "")):
                        check(" ".join(text.split()) in visible, f"{filename}: FAQ schema text absent from visible HTML")
    check(faq_count == page.faq_count, f"{filename}: FAQ schema count {faq_count} differs from visible articles {page.faq_count}")

for filename, page in pages.items():
    for ref in page.refs:
        parsed = urlparse(ref)
        if parsed.scheme or parsed.netloc:
            continue
        target = (ROOT / unquote(parsed.path.lstrip("/"))) if parsed.path.startswith("/") else (ROOT / filename).parent / unquote(parsed.path)
        if not parsed.path:
            target = ROOT / filename
        check(target.resolve().is_relative_to(ROOT), f"{filename}: path leaves repository: {ref}")
        check(target.exists(), f"{filename}: missing local link or asset: {ref}")
        if parsed.fragment and target.suffix == ".html" and target.name in pages:
            allowed_groups: set[str] = set()
            if target.name in ("materials.html", "cases.html"):
                catalog = json.loads((ROOT / ("cases.json" if target.name == "cases.html" else "materials.json")).read_text())
                allowed_groups = {g["id"] for g in catalog["groups"]}
            check(unquote(parsed.fragment) in set(pages[target.name].ids) | allowed_groups, f"{filename}: missing target anchor: {ref}")

catalog = json.loads((ROOT / "materials.json").read_text())
check(len(catalog["items"]) == 53, "Expected the reviewed catalog of 52 posters plus one reference image")
check(set(pages["materials.html"].material_ids) == {item["id"] for item in catalog["items"]}, "Static material cards differ from materials.json")
check(len(pages["materials.html"].material_ids) == 53, "Static material cards must appear exactly once")

namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
tree = ET.parse(ROOT / "sitemap.xml")
urls = [node.text for node in tree.findall("sm:url/sm:loc", namespace)]
expected = {pages[name].canonicals[0] for name in PAGES if name not in NOINDEX}
check(set(urls) == expected and len(urls) == len(expected), "Sitemap must contain each indexable canonical exactly once and no empty case/preview pages")
check("Sitemap: " + pages["index.html"].canonicals[0] + "sitemap.xml" in (ROOT / "robots.txt").read_text(), "robots.txt must point to canonical sitemap")
check("Allow: /" in (ROOT / "robots.txt").read_text(), "Public crawling must remain allowed")
check("目标、漏斗和台数测算用于规划，不是已发生的销量或业绩" in (ROOT / "index.html").read_text(), "Marketing plan must distinguish targets from real outcomes")
check("案例待补充" in (ROOT / "cases.html").read_text(), "Empty cases page must retain its pending-evidence status")
for name in ("partners.html", "faq.html"):
    content = (ROOT / name).read_text()
    check("95 折" not in content and "93 折" not in content and "85 折" not in content, f"{name}: conflicting bulk discounts must not be republished")
    for path in ("/guides/", "/guides/mac-mini-rental.html", "/guides/claude-code-remote-mac.html", "/guides/teams-and-educators.html", "/guides/partners.html"):
        check("https://wodemac.com" + path in content, f"{name}: missing agreed official guide link {path}")

if errors:
    print("SEO validation failed:")
    for error in errors:
        print("- " + error)
    sys.exit(1)
print("PASS: six unique page heads, visible/schema FAQ parity, 53 static material cards, local links/assets, index policy, four canonical sitemap URLs and honest service/plan facts.")

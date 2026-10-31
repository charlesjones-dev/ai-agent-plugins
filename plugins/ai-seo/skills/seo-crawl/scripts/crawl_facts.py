#!/usr/bin/env python3
"""Read the responses that /seo-crawl saved with curl and print the facts it checks.

It never fetches anything. curl saves the files, and this script only reads them.
Standard library only. Run it with `python3 -I` so nothing in the current folder loads.

    crawl_facts.py page FILE [--url URL]
    crawl_facts.py robots FILE [--agent TOKEN[,FALLBACK...]]... [--path PATH]...
    crawl_facts.py sitemap FILE
    crawl_facts.py image FILE

page     Head tags, headings, text size, images, links, JSON-LD and mixed content of one
         HTML file, as JSON. --url is the page's final URL, for resolving links.
robots   Which group each crawler obeys under RFC 9309, and whether each path is allowed,
         with the rule that decides it. Also flags named groups that drop the `*` rules.
         --agent takes the crawler's product token, then fallbacks, most specific first,
         such as `Googlebot-Image,Googlebot`. Defaults: Googlebot, Bingbot and `*` for `/`.
sitemap  A urlset or sitemap index as JSON: every loc and lastmod, the hosts, lastmod
         spread, duplicates and non-HTML entries.
image    Format, pixel size and byte size of a PNG, JPEG, GIF, WebP, AVIF or SVG file.

Exit codes: 0 done, 1 the file couldn't be parsed, 2 bad arguments.
"""

import argparse
import json
import re
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

CAP = 25
SKIP_TEXT = {"script", "style", "noscript", "template", "svg", "title"}
HEAD_TAGS = {"html", "head", "title", "meta", "link", "script", "style", "base", "noscript", "template"}
LANDMARKS = ("header", "nav", "main", "article", "aside", "footer")
SHELL_IDS = {"app", "root", "__next", "__nuxt", "svelte", "___gatsby", "q-app"}
FORM_FIELDS = {"textarea", "select"}
INPUT_SKIP = {"hidden", "submit", "button", "reset", "checkbox", "radio", "image", "file", "range", "color"}
GENERIC_ANCHORS = {"click here", "here", "read more", "learn more", "more", "this", "link", "this link"}
SUBRESOURCE_ATTRS = {"img": "src", "script": "src", "iframe": "src", "source": "src", "video": "src",
                     "audio": "src", "embed": "src", "object": "data"}


def capped(items, cap=CAP):
    items = list(items)
    return items[:cap] + ([f"... and {len(items) - cap} more"] if len(items) > cap else [])


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


class PageParser(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.skip = 0
        self.svg = 0
        self.in_head = True
        self.order = 0
        self.title = None
        self.title_buf = None
        self.metas, self.links, self.headings, self.images = [], [], [], []
        self.anchors, self.scripts, self.ldjson, self.text = [], [], [], []
        self.heading = None
        self.anchor = None
        self.ld_buf = None
        self.landmarks = Counter()
        self.first = {}
        self.lang = None
        self.fields = 0
        self.shell_ids = []
        self.mixed = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v if v is not None else "") for k, v in attrs}
        self.order += 1
        if tag == "body" or (self.in_head and tag not in HEAD_TAGS):
            self.in_head = False
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "svg":
            self.svg += 1
        elif tag == "title" and not self.svg and self.title is None:
            self.title_buf = []
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            a["_head"] = self.in_head
            self.links.append(a)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and not self.svg:
            self.heading = [int(tag[1]), []]
        elif tag == "a":
            self.anchor = {"href": a.get("href"), "rel": a.get("rel", "").lower().split(),
                           "target": a.get("target", "").lower(), "text": []}
        elif tag == "img":
            self.images.append(a)
            if self.anchor is not None and a.get("alt"):
                self.anchor["text"].append(a["alt"])
        elif tag == "script":
            if a.get("type", "").lower() == "application/ld+json":
                self.ld_buf = []
            else:
                a["_head"] = self.in_head
                self.scripts.append(a)
        elif tag == "input" and a.get("type", "text").lower() not in INPUT_SKIP:
            self.fields += 1
        elif tag in FORM_FIELDS:
            self.fields += 1
        elif tag == "div" and a.get("id") in SHELL_IDS:
            self.shell_ids.append(a["id"])
        if tag in LANDMARKS:
            self.landmarks[tag] += 1
            self.first.setdefault(tag, self.order)
        attr = SUBRESOURCE_ATTRS.get(tag)
        if tag == "link" and set(a.get("rel", "").lower().split()) & {"stylesheet", "icon", "preload", "modulepreload"}:
            attr = "href"
        if attr and a.get(attr, "").lower().startswith("http://"):
            self.mixed.append(a[attr])
        if tag in SKIP_TEXT:
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in SKIP_TEXT:
            self.skip = max(0, self.skip - 1)
        if tag == "svg":
            self.svg = max(0, self.svg - 1)
        elif tag == "title" and self.title_buf is not None:
            self.title, self.title_buf = "", None

    def handle_endtag(self, tag):
        if tag in SKIP_TEXT:
            self.skip = max(0, self.skip - 1)
        if tag == "head":
            self.in_head = False
        elif tag == "svg":
            self.svg = max(0, self.svg - 1)
        elif tag == "title" and self.title_buf is not None:
            self.title = clean("".join(self.title_buf))
            self.title_buf = None
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.heading is not None:
            self.headings.append((self.heading[0], clean("".join(self.heading[1]))))
            self.heading = None
        elif tag == "a" and self.anchor is not None:
            self.anchor["text"] = clean(" ".join(self.anchor["text"]))
            self.anchors.append(self.anchor)
            self.anchor = None
        elif tag == "script" and self.ld_buf is not None:
            self.ldjson.append("".join(self.ld_buf))
            self.ld_buf = None

    def handle_data(self, data):
        if self.title_buf is not None:
            self.title_buf.append(data)
        if self.ld_buf is not None:
            self.ld_buf.append(data)
            return
        if self.skip:
            return
        if self.heading is not None:
            self.heading[1].append(data)
        if self.anchor is not None:
            self.anchor["text"].append(data)
        if not self.in_head:
            self.text.append(data)


def ld_types(node, counter):
    if isinstance(node, list):
        for item in node:
            ld_types(item, counter)
    elif isinstance(node, dict):
        kind = node.get("@type")
        for name in ([kind] if isinstance(kind, str) else kind if isinstance(kind, list) else []):
            counter[str(name)] += 1
        for key, value in node.items():
            if key != "@context":
                ld_types(value, counter)


def page_facts(html, url):
    p = PageParser(url)
    p.feed(html)
    p.close()
    base_host = urlsplit(url).netloc.lower() if url else ""

    def meta(attr, value):
        return [m.get("content", "") for m in p.metas if m.get(attr, "").lower() == value]

    def rels(name):
        return [link for link in p.links if name in link.get("rel", "").lower().split()]

    descriptions = meta("name", "description")
    text = clean(" ".join(p.text))
    words = len([w for w in text.split(" ") if re.search(r"\w", w)])

    skips = []
    for (prev, _), (level, heading) in zip(p.headings, p.headings[1:]):
        if level > prev + 1:
            skips.append(f"h{prev} -> h{level}: {heading[:80]}")

    internal, external, blank, generic = set(), set(), [], []
    for anchor in p.anchors:
        href = (anchor["href"] or "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        full = urljoin(url, href) if url else href
        parts = urlsplit(full)
        if parts.scheme in ("http", "https") and (not base_host or parts.netloc.lower() == base_host):
            internal.add((parts.path or "/") + (f"?{parts.query}" if parts.query else ""))
        elif parts.scheme in ("http", "https"):
            external.add(full.split("#", 1)[0])
        if anchor["target"] == "_blank" and not {"noopener", "noreferrer"} & set(anchor["rel"]):
            blank.append(href)
        if anchor["text"].lower().rstrip(".!→> ") in GENERIC_ANCHORS:
            generic.append(f"{anchor['text']} -> {href}")

    ld_errors, types, contexts = [], Counter(), set()
    for i, block in enumerate(p.ldjson, 1):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError as e:
            ld_errors.append(f"block {i}: {e.msg} (line {e.lineno}, column {e.colno})")
            continue
        for node in data if isinstance(data, list) else [data]:
            if isinstance(node, dict) and "@context" in node:
                contexts.add(json.dumps(node["@context"]) if not isinstance(node["@context"], str) else node["@context"])
        ld_types(data, types)

    og, twitter = {}, {}
    for m in p.metas:
        prop = (m.get("property") or m.get("name") or "").lower()
        if prop.startswith("og:"):
            og.setdefault(prop, []).append(m.get("content", ""))
        elif prop.startswith("twitter:"):
            twitter.setdefault(prop, []).append(m.get("content", ""))

    images = p.images
    head_css = [link.get("href") for link in rels("stylesheet")
                if link["_head"] and link.get("media", "all").lower() not in ("print", "none") and "disabled" not in link]
    sync_js = [s.get("src") for s in p.scripts if s["_head"] and s.get("src") and "async" not in s and "defer" not in s
               and s.get("type", "").lower() != "module"]

    return {
        "url": url,
        "lang": p.lang,
        "title": {"text": p.title, "length": len(p.title or "")},
        "description": {"text": descriptions[0] if descriptions else None,
                        "length": len(descriptions[0]) if descriptions else 0, "count": len(descriptions)},
        "canonical": [link.get("href") for link in rels("canonical")],
        "robots": {name: meta("name", name) for name in ("robots", "googlebot", "bingbot") if meta("name", name)},
        "meta_refresh": meta("http-equiv", "refresh"),
        "viewport": (meta("name", "viewport") or [None])[0],
        "charset": any("charset" in m for m in p.metas) or bool(meta("http-equiv", "content-type")),
        "hreflang": [{"lang": link.get("hreflang"), "href": link.get("href")} for link in rels("alternate") if link.get("hreflang")],
        "og": og,
        "twitter": twitter,
        "icons": [{"rel": link.get("rel"), "href": link.get("href"), "sizes": link.get("sizes")}
                  for link in p.links if set(link.get("rel", "").lower().split()) & {"icon", "apple-touch-icon", "mask-icon"}],
        "manifest": (rels("manifest") or [{}])[0].get("href"),
        "headings": [f"h{level}: {heading[:100]}" for level, heading in p.headings][:60],
        "h1_count": sum(1 for level, _ in p.headings if level == 1),
        "heading_skips": skips,
        "landmarks": dict(p.landmarks),
        "main_before_header": bool(p.first.get("main") and p.first.get("header") and p.first["main"] < p.first["header"]),
        "words": words,
        "text_chars": len(text),
        "shell_root_ids": p.shell_ids,
        "looks_like_js_shell": words < 40 and bool(p.shell_ids),
        "images": {
            "count": len(images),
            "missing_alt": capped(i.get("src") or i.get("data-src") for i in images if "alt" not in i),
            "empty_alt": sum(1 for i in images if i.get("alt") == ""),
            "missing_size": capped(i.get("src") or i.get("data-src") for i in images if not (i.get("width") and i.get("height"))),
            "lazy": sum(1 for i in images if i.get("loading", "").lower() == "lazy"),
            "first": {k: images[0].get(k) for k in ("src", "width", "height", "loading", "fetchpriority")} if images else None,
        },
        "links": {
            "internal": sorted(internal),
            "external": sorted(external),
            "blank_without_noopener": capped(blank),
            "generic_text": capped(generic),
        },
        "head": {
            "stylesheets": head_css,
            "sync_scripts": sync_js,
            "preloads": [{"href": link.get("href"), "as": link.get("as")} for link in p.links
                         if set(link.get("rel", "").lower().split()) & {"preload", "modulepreload"}],
            "preconnect": [link.get("href") for link in rels("preconnect")],
        },
        "json_ld": {"blocks": len(p.ldjson), "errors": ld_errors, "types": dict(types), "contexts": sorted(contexts)},
        "form_fields": p.fields,
        "mixed_content": capped(p.mixed) if url and url.startswith("https://") else [],
    }


# robots.txt, following RFC 9309 (https://www.rfc-editor.org/rfc/rfc9309)

UNSUPPORTED = {
    "noindex": "not supported by Google since 2019. Use a robots meta tag or an X-Robots-Tag header",
    "nofollow": "not a robots.txt rule. Use a robots meta tag or rel=nofollow",
    "crawl-delay": "Google ignores it. Bing and some other crawlers obey it",
    "host": "only Yandex used it. Google ignores it",
    "content-signal": "a content-signals line. Search engines don't treat it as a crawl rule",
}


def parse_robots(text):
    groups, sitemaps, warnings = [], [], []
    current, after_agent = None, False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            warnings.append(f"line {n}: no colon, so crawlers ignore it: {raw.strip()[:80]}")
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key in ("user-agent", "useragent", "user agent"):
            if key != "user-agent":
                warnings.append(f"line {n}: '{key}' is misspelled. Write 'User-agent'")
            if current is None or not after_agent:
                current = {"agents": [], "raw": [], "rules": [], "start": n, "end": n}
                groups.append(current)
            match = re.match(r"\*|[A-Za-z_-]+", value)
            current["agents"].append(match.group(0) if match else value)
            current["raw"].append(value)
            current["end"] = n
            after_agent = True
        elif key in ("allow", "disallow"):
            if current is None:
                warnings.append(f"line {n}: {key} comes before any User-agent line, so crawlers ignore it")
                continue
            current["end"], after_agent = n, False
            if value:
                if not value.startswith(("/", "*")):
                    warnings.append(f"line {n}: the path '{value}' should start with / or *")
                current["rules"].append((key, value, n))
        elif key == "sitemap":
            sitemaps.append(value)
            if not value.lower().startswith(("http://", "https://")):
                warnings.append(f"line {n}: the Sitemap URL must be absolute: {value}")
        else:
            if current is not None:
                current["end"], after_agent = n, False
            warnings.append(f"line {n}: {key}: {UNSUPPORTED.get(key, 'not part of RFC 9309, so Google ignores it')}")
    return groups, sitemaps, warnings


def pattern_matches(pattern, path):
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    rx = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
    return re.match(rx + ("$" if anchored else ""), path, re.DOTALL) is not None


def decide(rules, path):
    """Longest matching pattern wins. On a tie, Allow wins (RFC 9309 section 2.2.2)."""
    if path == "/robots.txt":
        return "allow", "robots.txt itself is always allowed"
    best = None
    for kind, pattern, n in rules:
        if pattern_matches(pattern, path):
            key = (len(pattern), kind == "allow")
            if best is None or key > best[0]:
                best = (key, kind, pattern, n)
    if best is None:
        return "allow", "no rule matches"
    return best[1], f"{best[1].capitalize()}: {best[2]} (line {best[3]})"


def select_groups(groups, chain):
    for token in chain:
        if token == "*":
            break
        hit = [g for g in groups if any(a != "*" and a.lower() == token.lower() for a in g["agents"])]
        if hit:
            return token, hit
    star = [g for g in groups if "*" in g["agents"]]
    return ("*", star) if star else (None, [])


def robots_report(text, size, chains, paths):
    groups, sitemaps, warnings = parse_robots(text)
    if size > 500 * 1024:
        warnings.append(f"the file is {size} bytes. Google reads only the first 500 KiB")

    star_disallow = {r[1] for g in groups if "*" in g["agents"] for r in g["rules"] if r[0] == "disallow"}
    named = {}
    for g in groups:
        if "*" in g["agents"]:
            continue
        for agent in g["agents"]:
            entry = named.setdefault(agent.lower(), {"name": agent, "rules": [], "lines": []})
            entry["rules"] += g["rules"]
            entry["lines"].append(f"{g['start']}-{g['end']}")
    dropped = {}
    for entry in named.values():
        own = {r[1] for r in entry["rules"] if r[0] == "disallow"}
        missing = tuple(sorted(star_disallow - own))
        if missing:
            dropped.setdefault(missing, []).append(f"{entry['name']} (lines {', '.join(entry['lines'])})")
    for missing, agents in dropped.items():
        shown = ", ".join(missing[:8]) + (f" and {len(missing) - 8} more" if len(missing) > 8 else "")
        who = "; ".join(agents[:6]) + (f"; and {len(agents) - 6} more" if len(agents) > 6 else "")
        warnings.append(f"{who} obey only their own group, so they skip {len(missing)} "
                        f"Disallow rule(s) of the * group: {shown}")

    out = [f"robots.txt: {len(groups)} group(s), {len(sitemaps)} sitemap line(s), {len(warnings)} warning(s)", "groups:"]
    for g in groups:
        allows = sum(1 for r in g["rules"] if r[0] == "allow")
        out.append(f"  lines {g['start']}-{g['end']}  User-agent: {', '.join(g['raw'])}  "
                   f"({allows} allow, {len(g['rules']) - allows} disallow)")
    out.append("sitemaps:")
    out += [f"  {s}" for s in sitemaps] or ["  none"]
    out.append("warnings:")
    out += [f"  {w}" for w in warnings] or ["  none"]
    for chain in chains:
        token, chosen = select_groups(groups, chain)
        label = ",".join(chain)
        if token is None:
            out.append(f"{label}: no group applies, so everything is allowed")
            rules = []
        else:
            spans = ", ".join(f"{g['start']}-{g['end']}" for g in chosen)
            out.append(f"{label}: obeys the group(s) at lines {spans} (User-agent: {token})")
            rules = [r for g in chosen for r in g["rules"]]
        for path in paths:
            verdict, why = decide(rules, path)
            out.append(f"  {verdict:<9} {path}  {why}")
    return "\n".join(out)


# Sitemaps

W3C_DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2}))?)?)?$")
NON_PAGE = {".txt", ".xml", ".json", ".md", ".csv", ".js", ".css", ".png", ".jpg", ".jpeg", ".gif",
            ".webp", ".avif", ".svg", ".ico", ".zip", ".gz", ".woff", ".woff2"}


def sitemap_facts(data):
    if re.search(rb"<!(DOCTYPE|ENTITY)", data, re.I):
        return {"error": "the file declares a DOCTYPE or ENTITY. Sitemaps never need one, so it wasn't parsed"}
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        return {"error": f"not well-formed XML: {e}"}

    def local(tag):
        return tag.rsplit("}", 1)[-1]

    kind = local(root.tag)
    child = {"urlset": "url", "sitemapindex": "sitemap"}.get(kind)
    if child is None:
        return {"error": f"the root element is <{kind}>. A sitemap needs <urlset> or <sitemapindex>"}
    entries, alternates, changefreq, priority = [], 0, 0, 0
    for element in root:
        if local(element.tag) != child:
            continue
        entry = {}
        for field in element:
            name = local(field.tag)
            if name in ("loc", "lastmod"):
                entry[name] = (field.text or "").strip()
            elif name == "link":
                alternates += 1
            changefreq += name == "changefreq"
            priority += name == "priority"
        entries.append(entry)

    locs = [e.get("loc", "") for e in entries]
    lastmods = [e["lastmod"] for e in entries if e.get("lastmod")]
    now = datetime.now(timezone.utc)
    future, invalid = [], []
    for value in lastmods:
        if not W3C_DATE.match(value):
            invalid.append(value)
            continue
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00")) if "T" in value else \
                datetime.strptime(value[:10], "%Y-%m-%d") if len(value) >= 10 else None
        except ValueError:
            continue
        if stamp is not None:
            stamp = stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
            if stamp > now:
                future.append(value)
    days = Counter(v[:10] for v in lastmods)
    hosts = Counter(f"{urlsplit(u).scheme}://{urlsplit(u).netloc}" for u in locs if u)
    non_page = [u for u in locs if Path(urlsplit(u).path).suffix.lower() in NON_PAGE]
    return {
        "kind": kind,
        "count": len(entries),
        "missing_loc": sum(1 for u in locs if not u),
        "relative_loc": capped(u for u in locs if u and not u.lower().startswith(("http://", "https://"))),
        "hosts": dict(hosts),
        "duplicates": capped(u for u, c in Counter(locs).items() if u and c > 1),
        "non_page": capped(non_page),
        "lastmod": {"present": len(lastmods), "distinct_days": len(days),
                    "most_common_day": list(days.most_common(1)[0]) if days else None,
                    "future": capped(future), "invalid": capped(invalid)},
        "hreflang_links": alternates,
        "changefreq_or_priority": changefreq + priority,
        "over_limit": len(entries) > 50000 or len(data) > 50 * 1024 * 1024,
        "entries": entries,
    }


# Images

SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def image_facts(data):
    def result(fmt, w, h):
        return {"format": fmt, "width": w, "height": h, "bytes": len(data)}

    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return result("png", *struct.unpack(">II", data[16:24]))
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return result("gif", *struct.unpack("<HH", data[6:10]))
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker == 0xFF:
                i += 1
            elif marker in (0x01, 0xD8) or 0xD0 <= marker <= 0xD7:
                i += 2
            elif marker in SOF:
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return result("jpeg", w, h)
            else:
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        return result("jpeg", None, None)
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8 " and len(data) >= 30:
            w, h = struct.unpack("<HH", data[26:30])
            return result("webp", w & 0x3FFF, h & 0x3FFF)
        if chunk == b"VP8L" and len(data) >= 25:
            bits = int.from_bytes(data[21:25], "little")
            return result("webp", (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        if chunk == b"VP8X" and len(data) >= 30:
            return result("webp", int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
        return result("webp", None, None)
    if data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis", b"mif1", b"heic"):
        j = data.find(b"ispe")
        if j != -1 and j + 16 <= len(data):
            return result("avif", *struct.unpack(">II", data[j + 8:j + 16]))
        return result("avif", None, None)
    head = data[:4096].decode("utf-8", "replace")
    tag = re.search(r"<svg\b[^>]*>", head, re.S)
    if tag:
        def attr(name):
            m = re.search(rf'\s{name}\s*=\s*["\']([^"\']*)["\']', tag.group(0))
            return m.group(1) if m else None
        out = result("svg", attr("width"), attr("height"))
        out["viewBox"] = attr("viewBox")
        return out
    return {"error": "not a PNG, JPEG, GIF, WebP, AVIF or SVG file", "bytes": len(data)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    page = sub.add_parser("page")
    page.add_argument("file")
    page.add_argument("--url", default="")
    robots = sub.add_parser("robots")
    robots.add_argument("file")
    robots.add_argument("--agent", action="append", default=[])
    robots.add_argument("--path", action="append", default=[])
    sub.add_parser("sitemap").add_argument("file")
    sub.add_parser("image").add_argument("file")
    args = parser.parse_args(argv)

    try:
        data = Path(args.file).read_bytes()
    except OSError as e:
        print(f"can't read {args.file}: {e}", file=sys.stderr)
        return 2

    if args.command == "page":
        print(json.dumps(page_facts(data.decode("utf-8", "replace"), args.url), indent=2, ensure_ascii=False))
        return 0
    if args.command == "robots":
        chains = [[t.strip() for t in a.split(",") if t.strip()] for a in args.agent] or [["Googlebot"], ["Bingbot"], ["*"]]
        paths = []
        for p in args.path or ["/"]:
            parts = urlsplit(p)
            paths.append((parts.path or "/") + (f"?{parts.query}" if parts.query else "") if parts.scheme else p)
        print(robots_report(data.decode("utf-8-sig", "replace"), len(data), chains, paths))
        return 0
    facts = sitemap_facts(data) if args.command == "sitemap" else image_facts(data)
    print(json.dumps(facts, indent=2, ensure_ascii=False))
    return 1 if "error" in facts else 0


if __name__ == "__main__":
    sys.exit(main())

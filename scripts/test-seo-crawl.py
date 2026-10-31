#!/usr/bin/env python3
"""Run ai-seo's crawl_facts.py against sample responses.

Run from the repository root:

    python3 scripts/test-seo-crawl.py

The script is plugins/ai-seo/skills/seo-crawl/scripts/crawl_facts.py. Each case writes
a sample file to a temporary folder, runs one subcommand on it with `python3 -I`, and
checks the output.

The cases cover robots.txt under RFC 9309 (a named group that drops the `*` rules,
longest match, Allow winning a tie, `*` and `$` patterns, fallback tokens, rules before
any User-agent line, unsupported lines), page facts (title, description, canonical,
headings, a JavaScript shell, images, links, broken JSON-LD, mixed content), sitemaps
(a urlset, a sitemap index, a DOCTYPE, malformed XML) and image sizes (PNG, GIF, JPEG,
WebP and SVG).

Exits 1 and lists every failure. Standard library only.
"""

import json
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "ai-seo" / "skills" / "seo-crawl" / "scripts" / "crawl_facts.py"

ROBOTS = """\
# Rules for every crawler
User-agent: *
Disallow: /home
Disallow: /orders
Disallow: /api/
Allow: /api/public
Disallow: /*.json$
Disallow: /drafts
Allow: /drafts

User-agent: Googlebot
User-agent: Bingbot
Allow: /

User-agent: GPTBot
Disallow: /home
Disallow: /orders
Disallow: /api/
Disallow: /*.json$
Disallow: /drafts
Crawl-delay: 10
Noindex: /secret

Sitemap: https://example.com/sitemap.xml
Sitemap: /relative.xml"""

PAGE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>  Example   Widgets | Example Co </title>
<meta name="description" content="Widgets for every desk.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://example.com/widgets">
<link rel="alternate" hreflang="de" href="https://example.com/de/widgets">
<link rel="stylesheet" href="/assets/app.css">
<link rel="stylesheet" href="/assets/print.css" media="print">
<link rel="icon" href="http://cdn.example.net/favicon.ico">
<script src="/assets/blocking.js"></script>
<script src="/assets/app.js" defer></script>
<meta property="og:title" content="Example Widgets">
<script type="application/ld+json">{"@context": "https://schema.org", "@graph": [
  {"@type": "Organization", "name": "Example Co"}, {"@type": "Organization", "name": "Example Co"},
  {"@type": ["Product", "Thing"], "name": "Widget"}]}</script>
<script type="application/ld+json">{"@context": "https://schema.org", "@type": "FAQPage",}</script>
</head>
<body>
<main>
<header><svg><title>logo</title></svg><nav><a href="/">Home</a></nav></header>
<h1>Widgets <svg><text>icon</text></svg></h1>
<p>Our widgets hold paper, pens and cables on any desk.</p>
<h2>Sizes</h2>
<h4>Small</h4>
<img src="/a.png" alt="A widget" width="10" height="10" loading="lazy">
<img src="/b.png">
<img src="/c.png" alt="">
<a href="/pricing?plan=pro#top">Read more →</a>
<a href="https://partner.example.org/x" target="_blank">Partner</a>
<a href="mailto:hi@example.com">Mail</a>
<input type="email"><input type="hidden"><textarea></textarea>
<img src="http://cdn.example.net/hero.jpg" alt="Hero">
<script>var words = "these words are not page text";</script>
</main>
<footer><h3>Company</h3></footer>
</body>
</html>"""

SHELL = """<!doctype html><html><head><title>App</title></head>
<body><div id="app"></div><script type="module" src="/assets/index.js"></script></body></html>"""

URLSET = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url><loc>https://example.com/</loc><lastmod>2026-10-23</lastmod><priority>1.0</priority></url>
  <url><loc>https://example.com/pricing</loc><lastmod>2026-10-23T08:00:00Z</lastmod>
    <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/pricing"/></url>
  <url><loc>https://example.com/pricing</loc><lastmod>2026-10-23</lastmod></url>
  <url><loc>https://www.example.com/llms.txt</loc><lastmod>2099-01-01</lastmod></url>
  <url><loc>/relative</loc><lastmod>last tuesday</lastmod></url>
</urlset>"""

INDEX = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example.com/sitemap-en.xml</loc></sitemap>
  <sitemap><loc>https://example.com/sitemap-de.xml</loc></sitemap>
</sitemapindex>"""

DOCTYPE = """<?xml version="1.0"?><!DOCTYPE lol [<!ENTITY a "aaaa">]><urlset><url><loc>&a;</loc></url></urlset>"""


def png(width, height):
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")


def jpeg(width, height):
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, height, width, 1) + b"\x01\x11\x00"
    return b"\xff\xd8" + app0 + sof + b"\xff\xd9"


def webp_lossless(width, height):
    bits = (width - 1) | ((height - 1) << 14)
    body = b"\x2f" + bits.to_bytes(4, "little") + b"\x00" * 8
    return b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WEBP" + b"VP8L" + struct.pack("<I", len(body)) + body


def run(tmp, name, content, *args):
    path = tmp / name
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), args[0], str(path), *args[1:]],
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    return result


def main():
    failures, total = [], 0

    def check(name, condition, detail=""):
        nonlocal total
        total += 1
        if not condition:
            failures.append(f"{name}{': ' + detail if detail else ''}")

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)

        # robots.txt
        r = run(tmp, "robots.txt", ROBOTS, "robots",
                "--agent", "Googlebot", "--agent", "GPTBot", "--agent", "Googlebot-Image,Googlebot",
                "--agent", "SomeBot", "--agent", "*",
                "--path", "/home", "--path", "/api/public/x", "--path", "/data.json",
                "--path", "/data.json?x=1", "--path", "/drafts", "--path", "https://example.com/orders?id=2",
                "--path", "/robots.txt")
        out = r.stdout
        check("robots: exit code", r.returncode == 0, r.stderr)
        sections, current = {}, None
        for line in out.splitlines():
            if not line.startswith(" ") and (": obeys" in line or ": no group" in line):
                current = line.split(":", 1)[0]
                sections[current] = []
            elif line.startswith("  ") and current is not None:
                sections[current].append(line.split())

        def verdict(agent, path):
            for parts in sections.get(agent, []):
                if parts[1] == path:
                    return parts[0]
            return None

        check("robots: 3 groups", "3 group(s)" in out, out.splitlines()[0] if out else "")
        check("robots: Googlebot uses its own group", "Googlebot: obeys the group(s) at lines 11-13" in out, out)
        check("robots: Googlebot may crawl /home", verdict("Googlebot", "/home") == "allow")
        check("robots: * group blocks /home", verdict("*", "/home") == "disallow")
        check("robots: longest match allows /api/public/x", verdict("*", "/api/public/x") == "allow")
        check("robots: $ pattern blocks /data.json", verdict("*", "/data.json") == "disallow")
        check("robots: $ pattern allows /data.json?x=1", verdict("*", "/data.json?x=1") == "allow")
        check("robots: Allow wins a tie on /drafts", verdict("*", "/drafts") == "allow")
        check("robots: full URL becomes path and query", verdict("*", "/orders?id=2") == "disallow")
        check("robots: robots.txt always allowed", verdict("GPTBot", "/robots.txt") == "allow")
        check("robots: GPTBot keeps its rules", verdict("GPTBot", "/home") == "disallow")
        check("robots: fallback token", "Googlebot-Image,Googlebot: obeys the group(s) at lines 11-13 (User-agent: Googlebot)" in out, out)
        check("robots: unknown bot falls back to *", "SomeBot: obeys the group(s) at lines 2-9 (User-agent: *)" in out, out)
        check("robots: dropped-rules warning names Googlebot and Bingbot",
              "Googlebot (lines 11-13); Bingbot (lines 11-13) obey only their own group, so they skip 5" in out, out)
        check("robots: GPTBot is not warned", "GPTBot (lines" not in out, out)
        check("robots: Crawl-delay warning", "crawl-delay: Google ignores it" in out)
        check("robots: Noindex warning", "noindex: not supported by Google since 2019" in out)
        check("robots: relative Sitemap warning", "the Sitemap URL must be absolute: /relative.xml" in out)

        r = run(tmp, "robots-early.txt", "Disallow: /x\nUser-agent: *\nDisallow: /y\n", "robots", "--path", "/x")
        check("robots: rule before User-agent is ignored", "before any User-agent line" in r.stdout and "allow     /x" in r.stdout, r.stdout)
        r = run(tmp, "robots-empty.txt", "", "robots")
        check("robots: empty file allows everything", "Googlebot: no group applies" in r.stdout and "allow     /" in r.stdout, r.stdout)

        # page
        r = run(tmp, "page.html", PAGE, "page", "--url", "https://example.com/widgets")
        check("page: exit code", r.returncode == 0, r.stderr)
        try:
            f = json.loads(r.stdout)
        except json.JSONDecodeError as e:
            failures.append(f"page: output is not JSON: {e}")
            f = None
        if f:
            check("page: title ignores svg title", f["title"] == {"text": "Example Widgets | Example Co", "length": 28}, str(f["title"]))
            check("page: description", f["description"]["length"] == 23 and f["description"]["count"] == 1)
            check("page: canonical", f["canonical"] == ["https://example.com/widgets"])
            check("page: robots", f["robots"] == {"robots": ["index, follow"]}, str(f["robots"]))
            check("page: hreflang", f["hreflang"] == [{"lang": "de", "href": "https://example.com/de/widgets"}])
            check("page: one h1 without svg text", f["h1_count"] == 1 and f["headings"][0] == "h1: Widgets", str(f["headings"]))
            check("page: heading skip", f["heading_skips"] == ["h2 -> h4: Small"], str(f["heading_skips"]))
            check("page: main before header", f["main_before_header"] is True)
            check("page: script text not counted", f["words"] < 40 and "these" not in json.dumps(f["headings"]), str(f["words"]))
            check("page: not a shell", f["looks_like_js_shell"] is False)
            check("page: images", f["images"]["count"] == 4 and f["images"]["missing_alt"] == ["/b.png"]
                  and f["images"]["empty_alt"] == 1 and f["images"]["lazy"] == 1, str(f["images"]))
            check("page: first image", f["images"]["first"]["src"] == "/a.png")
            check("page: internal links keep the query", f["links"]["internal"] == ["/", "/pricing?plan=pro"], str(f["links"]["internal"]))
            check("page: external links", f["links"]["external"] == ["https://partner.example.org/x"])
            check("page: target blank without noopener", f["links"]["blank_without_noopener"] == ["https://partner.example.org/x"])
            check("page: generic anchor text", f["links"]["generic_text"] == ["Read more → -> /pricing?plan=pro#top"], str(f["links"]["generic_text"]))
            check("page: render-blocking head resources", f["head"]["stylesheets"] == ["/assets/app.css"]
                  and f["head"]["sync_scripts"] == ["/assets/blocking.js"], str(f["head"]))
            check("page: JSON-LD error and types", f["json_ld"]["blocks"] == 2 and len(f["json_ld"]["errors"]) == 1
                  and f["json_ld"]["types"] == {"Organization": 2, "Product": 1, "Thing": 1}, str(f["json_ld"]))
            check("page: form fields", f["form_fields"] == 2, str(f["form_fields"]))
            check("page: mixed content", f["mixed_content"] == ["http://cdn.example.net/favicon.ico", "http://cdn.example.net/hero.jpg"],
                  str(f["mixed_content"]))
            check("page: og", f["og"] == {"og:title": ["Example Widgets"]})

        r = run(tmp, "shell.html", SHELL, "page", "--url", "https://example.com/missing")
        f = json.loads(r.stdout) if r.returncode == 0 else {}
        check("page: JavaScript shell", f.get("looks_like_js_shell") is True and f.get("shell_root_ids") == ["app"], r.stdout[:300])

        # sitemap
        r = run(tmp, "sitemap.xml", URLSET, "sitemap")
        f = json.loads(r.stdout) if r.returncode == 0 else {}
        check("sitemap: urlset", f.get("kind") == "urlset" and f.get("count") == 5, r.stdout[:300])
        if f:
            check("sitemap: hosts", f["hosts"] == {"https://example.com": 3, "https://www.example.com": 1, "://": 1}, str(f["hosts"]))
            check("sitemap: duplicates", f["duplicates"] == ["https://example.com/pricing"])
            check("sitemap: non-page entry", f["non_page"] == ["https://www.example.com/llms.txt"])
            check("sitemap: relative loc", f["relative_loc"] == ["/relative"])
            check("sitemap: lastmod spread", f["lastmod"]["most_common_day"] == ["2026-10-23", 3], str(f["lastmod"]))
            check("sitemap: future lastmod", f["lastmod"]["future"] == ["2099-01-01"])
            check("sitemap: invalid lastmod", f["lastmod"]["invalid"] == ["last tuesday"])
            check("sitemap: hreflang links and priority", f["hreflang_links"] == 1 and f["changefreq_or_priority"] == 1)
        r = run(tmp, "index.xml", INDEX, "sitemap")
        f = json.loads(r.stdout) if r.returncode == 0 else {}
        check("sitemap: index", f.get("kind") == "sitemapindex" and f.get("count") == 2, r.stdout[:300])
        r = run(tmp, "doctype.xml", DOCTYPE, "sitemap")
        check("sitemap: DOCTYPE refused", r.returncode == 1 and "DOCTYPE or ENTITY" in r.stdout, r.stdout)
        r = run(tmp, "broken.xml", "<urlset><url><loc>x</url>", "sitemap")
        check("sitemap: malformed XML", r.returncode == 1 and "not well-formed" in r.stdout, r.stdout)

        # images
        for name, data, expected in [
            ("a.png", png(750, 750), ("png", 750, 750)),
            ("a.gif", b"GIF89a" + struct.pack("<HH", 32, 16) + b"\x00" * 8, ("gif", 32, 16)),
            ("a.jpg", jpeg(1424, 906), ("jpeg", 1424, 906)),
            ("a.webp", webp_lossless(3093, 2247), ("webp", 3093, 2247)),
            ("a.svg", '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"></svg>',
             ("svg", "32", "32")),
        ]:
            r = run(tmp, name, data, "image")
            f = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}
            check(f"image: {name}", (f.get("format"), f.get("width"), f.get("height")) == expected, r.stdout)
        r = run(tmp, "a.bin", b"not an image", "image")
        check("image: unknown format", r.returncode == 1 and "error" in r.stdout, r.stdout)

    if failures:
        print(f"{len(failures)} of {total} checks failed:\n")
        for failure in failures:
            print(f"  {failure}")
        sys.exit(1)
    print(f"All {total} checks passed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""サイトの英語のプライバシーポリシーと利用規約から、アプリの中で表示する版の CSV を作る。

アプリ（v1.0 以降）は、SCcomponents の privacypolicy.json / termsofuse.json（Id・Headline・Body）を表示する。
その元の Excel に貼れるよう、同じ形の CSV（UTF-8 BOM 付き、改行は CRLF）を書き出す。
見出し（h2）ごとに 1 行。最初の見出しより前の文は、見出しが空の行にする。
最終更新日（p.updated）は、続く前文とつながって見えないよう、それだけで 1 行にする。
小見出し（h3）は本文の中の 1 行にし、2 つめからは前に空行を入れる。

使い方:
  python3 tools/export_app_csv.py <出力先のフォルダ>
"""
from __future__ import annotations

import csv
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {"privacypolicy": "privacy", "termsofuse": "terms"}


class Sections(HTMLParser):
    """h2 ごとに区切り、本文をアプリで読みやすい文字列にする"""

    def __init__(self):
        super().__init__()
        self.sections = [["", []]]   # [見出し, 本文の段落のリスト]
        self.buf, self.tag, self.href, self.cls = "", None, None, None

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "p", "li"):
            self.buf, self.tag, self.cls = "", tag, dict(attrs).get("class")
        elif tag == "a":
            self.href = dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag == "a":
            self.href = None
            return
        if tag != self.tag:
            return
        text = " ".join(self.buf.split())
        if tag == "h2":
            self.sections.append([text, []])
        elif tag == "h3":
            # アプリでは小見出しも本文と同じ字になるので、前に空行を入れて区切りを見せる
            if self.sections[-1][1]:
                self.sections[-1][1].append("")
            self.sections[-1][1].append(text)
        elif tag == "p":
            self.sections[-1][1].append(text)
            if self.cls == "updated":
                self.sections.append(["", []])
        elif tag == "li":
            self.sections[-1][1].append("- " + text)
        self.tag = None

    def handle_data(self, data):
        if self.tag in ("h2", "h3", "p", "li"):
            self.buf += data

    def handle_endtag_link(self):
        pass

    def unknown_decl(self, data):
        pass


def with_urls(html: str) -> str:
    """リンクの文字の後ろに URL を足す（アプリの中ではリンクを押せないため）。メールと、文字が URL そのものの場合は足さない"""
    import re

    def repl(m):
        href, text = m.group(1), m.group(2)
        if href.startswith("mailto:") or href.startswith("@root/") or text.strip() == href:
            return text
        return f"{text} ({href})"
    return re.sub(r'<a href="([^"]+)">(.*?)</a>', repl, html)


def export(name: str, page: str, out_dir: Path) -> Path:
    src = (ROOT / "src" / "en" / f"{page}.html").read_text(encoding="utf-8")
    parser = Sections()
    parser.feed(with_urls(src))
    rows = [(h, "\n".join(body)) for h, body in parser.sections if h or body]
    out = out_dir / f"{name}.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["Id", "Headline", "Body"])
        for i, (h, body) in enumerate(rows, start=1):
            w.writerow([i, h, body])
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, page in DOCS.items():
        print(export(name, page, out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())

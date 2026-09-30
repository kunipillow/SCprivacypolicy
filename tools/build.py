#!/usr/bin/env python3
"""stratchart.com のページを組み立てる（Python の標準機能だけで動く）。

src/<言語>/<ページ>.html には本文だけを書く。1 行目と 2 行目のコメントで、題名と説明を指定する:
  <!-- title: Privacy Policy -->
  <!-- description: ... -->
本文の中の「@root/」は、サイトの一番上への相対パスに置き換わる（例: @root/privacy/）。

使い方:
  python3 tools/build.py
src/ を直したら実行し、書き出された HTML も一緒にコミットする。
リンクはすべて相対パスなので、kunipillow.github.io/SCprivacypolicy/ でも stratchart.com でも同じように動く。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PAGES = ["index", "support", "privacy", "terms", "data"]
LANGS = {"en": "", "ja": "ja/"}
NAV = {
    "en": [("index", "Home"), ("support", "Support"), ("privacy", "Privacy Policy"),
           ("terms", "Terms of Use"), ("data", "About the Data")],
    "ja": [("index", "ホーム"), ("support", "サポート"), ("privacy", "プライバシーポリシー"),
           ("terms", "利用規約"), ("data", "データについて")],
}
SWITCH = {"en": ("ja", "日本語"), "ja": ("en", "English")}


def page_dir(lang: str, page: str) -> str:
    """公開するときのフォルダ（サイトの一番上からの相対。一番上は ""）"""
    return LANGS[lang] + ("" if page == "index" else page + "/")


def link(from_dir: str, to_dir: str) -> str:
    """from_dir のページから to_dir のページへの相対リンク"""
    return "../" * from_dir.count("/") + to_dir or "./"


def build_page(lang: str, page: str) -> str:
    src = (SRC / lang / f"{page}.html").read_text(encoding="utf-8")
    title = re.search(r"<!--\s*title:\s*(.*?)\s*-->", src).group(1)
    desc_m = re.search(r"<!--\s*description:\s*(.*?)\s*-->", src)
    desc = desc_m.group(1) if desc_m else ""
    body = re.sub(r"<!--\s*(title|description):.*?-->\n?", "", src).strip()
    here = page_dir(lang, page)
    root = "../" * here.count("/")
    body = body.replace("@root/", root)

    current = ' aria-current="page"'
    nav = "\n".join(
        f'      <a href="{link(here, page_dir(lang, p))}"{current if p == page else ""}>{label}</a>'
        for p, label in NAV[lang])
    other, other_label = SWITCH[lang]
    full_title = title if page == "index" else f"{title} | StratChart"
    footer_links = " · ".join(
        f'<a href="{link(here, page_dir(lang, p))}">{label}</a>' for p, label in NAV[lang][1:])
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  <meta name="description" content="{desc}">
  <link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="{link(here, page_dir(lang, "index"))}">StratChart</a>
      <a class="lang" href="{link(here, page_dir(other, page))}" hreflang="{other}" lang="{other}">{other_label}</a>
    </div>
    <nav class="wrap">
{nav}
    </nav>
  </header>
  <main class="wrap">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p>{footer_links}</p>
      <p>&copy; StratChart.com</p>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    for lang in LANGS:
        for page in PAGES:
            out = ROOT / page_dir(lang, page) / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(build_page(lang, page), encoding="utf-8")
            print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()

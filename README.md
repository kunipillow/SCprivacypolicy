# StratChart の Web サイト（stratchart.com）

StratChart アプリの公式サイト。GitHub Pages で公開する（ブランチ main の一番上）。

| ページ | 英語 | 日本語 |
|---|---|---|
| トップ | `/` | `/ja/` |
| サポート | `/support/` | `/ja/support/` |
| プライバシーポリシー | `/privacy/` | `/ja/privacy/` |
| 利用規約 | `/terms/` | `/ja/terms/` |
| データについて | `/data/` | `/ja/data/` |

日本語版のプライバシーポリシーと利用規約は参考訳で、英語版が優先する。

## 直し方

1. `src/<言語>/<ページ>.html`（本文だけ）を直す。1 行目の `<!-- title: ... -->` が題名、2 行目の `<!-- description: ... -->` が説明。本文の中の `@root/` は、サイトの一番上への相対パスになる。
2. `python3 tools/build.py` を実行して、公開用の HTML（`index.html`、`privacy/index.html` など）を作り直す。
3. `src/` と、作り直した HTML を一緒にコミットして push する。

リンクはすべて相対パスなので、`kunipillow.github.io/SCprivacypolicy/` でも `stratchart.com` でも同じように動く。
GitHub Pages の Jekyll は使わない（`.nojekyll`）。

## アプリの中の版にそろえる

アプリは、プライバシーポリシーと利用規約を SCcomponents の `privacypolicy.json` / `termsofuse.json` から表示する（英語）。
英語の本文を直したら、次の手順でアプリの中の版にもそろえる。

1. `python3 tools/export_app_csv.py <出力先>` で、Excel に貼れる CSV（`privacypolicy.csv`・`termsofuse.csv`）を作る
2. StratChart_wClaude の `SCcomponents/chartlist/` の Excel に貼り、`terms.py` で JSON を作る
3. `python3 tools/validate_contract.py` と `python3 tools/publish_content.py` で検査してから公開する

## 独自ドメイン（stratchart.com）

- ドメインは Xserver で取得。DNS に GitHub Pages の A レコード（185.199.108.153・185.199.109.153・185.199.110.153・185.199.111.153）と、www の CNAME（kunipillow.github.io）を設定する。
- DNS が通ってから、このリポジトリの Settings → Pages → Custom domain に `stratchart.com` を入れ、Enforce HTTPS を有効にする（GitHub が `CNAME` ファイルを作る）。DNS より先に入れると、今の URL がつながらなくなる。
- 設定すると、`kunipillow.github.io/SCprivacypolicy/...` は `stratchart.com/...` へ自動で転送される。

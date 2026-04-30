# AI Editorial OS ／ AI編集部OS

**誰もが、じぶん編集部を持てる。**

> *"Your own editorial team — in Claude."*

---

## For English speakers

**AI Editorial OS** is a role-based prompt system for Claude, built by a Japanese journalist with 30+ years of experience and 500+ articles/year.

Each role (researcher, writer, reviewer, etc.) acts as a specialized editorial agent. Together they form a complete editorial team inside Claude Code — or Claude.ai.

**Two versions included:**
- `classic/CLAUDE.md` — paste into Claude.ai and start immediately, no setup needed
- `roles/` + `CLAUDE.md` — full multi-agent pipeline for Claude Code

> ⚠️ α release. writer / reviewer / transcriber are production-tested. Issues & PRs welcome.

---

## これは何か

取材・文字起こし・執筆・校正・公開の全工程を、**役割別AIエージェントが分担する編集環境**です。

ジャーナリストとして30年・年間500本以上の記事制作から蒸留したルールを、誰でも使えるかたちで公開します。記者ひとりで回していたワークフローが、Claude Code のサブエージェント機能によって「編集部」になりました。

---

## こんな人に

| あなたは | 使い方 |
|---------|--------|
| 企業オウンドメディア担当者 | プリセットを媒体に合わせてカスタマイズ。品質を安定させながら量産できる |
| 編集者・ライター支援者 | クライアントに渡す「AIへの指示書」として。伴走の入口になる |
| 現場で書き続けるライター | ひとりで researcher → writer → reviewer を回して、プロ品質の初稿を出す |
| noteや文学フリマで表現したい人 | Classic版を Claude.ai に貼るだけで、自分の声を引き出す編集部ができる |

---

## Classic版 と Pipeline版

| | Classic版 | Pipeline版 |
|--|----------|-----------|
| ファイル | `classic/CLAUDE.md` | `CLAUDE.md` + `roles/` |
| 使う場所 | Claude.ai（チャット） | Claude Code |
| 向いている人 | まず試したい・コードは不要 | 自動化・大量処理したい |
| セットアップ | コピペするだけ | クローンして起動 |

**迷ったら Classic版から始めてください。**

---

## ワークフロー（Pipeline版）

```
researcher（取材前の背景調査）
  ↓
transcriber（文字起こし・クレンジング）
  ↓
writer（本文執筆）
  ↓
reviewer（発言照合・品質チェック）
  ↓
editor（最終調整・納品前確認）
```

日次管理：`scheduler`（朝）→ 作業 → `recap`（夜）

---

## フォルダ構成

```
ai-editorial-os/
├── CLAUDE.md              ← オーケストレーター（Claude Codeが自動読み込み）
├── classic/
│   └── CLAUDE.md          ← Classic版（Claude.ai用・コピペして使う）
├── roles/                 ← ロール別ルール定義
│   ├── researcher.md
│   ├── transcriber.md
│   ├── writer.md
│   ├── reviewer.md
│   ├── editor.md
│   ├── scheduler.md
│   ├── recap.md
│   ├── planner.md         ← 次フェーズ
│   ├── publisher.md       ← 次フェーズ
│   ├── performance.md     ← 次フェーズ
│   └── designer.md        ← 次フェーズ
├── presets/               ← 媒体別プリセット
│   ├── narrative-a/       ← ナラティブ・記者常体/引用敬体
│   ├── narrative-b/       ← ナラティブ・記者敬体/引用敬体
│   ├── qa/                ← Q&A対話形式
│   └── _template/         ← 自分の媒体を追加するテンプレート
└── scripts/
    └── transcribe.py      ← 文字起こしスクリプト（AmiVoice + AWS Transcribe）
```

---

## セットアップ

### Classic版（Claude.ai）

1. `classic/CLAUDE.md` を開く
2. 全文をコピー
3. Claude.ai のチャットに貼り付けて送信
4. 「文字起こしをもとに記事を書いて」など、そのまま指示する

### Pipeline版（Claude Code）

**1. リポジトリをクローン**

```bash
git clone https://github.com/h-mori-andg/ai-editorial-os.git
cd ai-editorial-os
```

**2. Claude Code を起動**

このフォルダ内で Claude Code を起動すれば `CLAUDE.md` が自動読み込みされる。

```bash
claude
```

**3. 環境変数を設定（文字起こしを使う場合）**

```bash
export AMIVOICE_API_KEY="your_amivoice_api_key"
export TRANSCRIBE_S3_BUCKET="your-s3-bucket-name"
export AWS_REGION="ap-northeast-1"
```

AmiVoice API キー取得：https://acp.amivoice.com/  
AWS S3 バケットは事前に作成しておく（AWS Transcribe の一時保存用）。

**4. Python依存パッケージのインストール（文字起こしを使う場合）**

```bash
pip install anthropic boto3 requests
```

---

## 使い方

```
# リサーチ（Playwright MCP が必要）
「〇〇株式会社の取材前リサーチをして」

# 文字起こし
「audio.m4a を文字起こしして。資料は prep.md と company.pdf」

# 執筆
「文字起こしをもとにナラティブ形式で記事を書いて。プリセットは narrative-a」

# レビュー
「草稿を発言照合してレビューして」

# 最終確認
「editor で最終チェックして」
```

---

## 媒体プリセットの追加

`presets/_template/` をコピーして媒体名のフォルダを作り、`CLAUDE.md` に設定を記入する。

```bash
cp -r presets/_template presets/your-media-name
# presets/your-media-name/CLAUDE.md を編集
```

---

## 動作環境

- [Claude Code](https://docs.anthropic.com/ja/docs/claude-code/overview)（Anthropic）
- Python 3.9 以上（文字起こしスクリプトを使う場合）
- AmiVoice API アカウント（日本語文字起こしを使う場合）
- AWS アカウント・S3バケット（英語文字起こしを使う場合）
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)（researcher ロールでWebリサーチを行う場合）

---

## α版について

> writer / reviewer / transcriber による記事制作ループは実運用済み。scheduler / recap による日次管理も動作確認済み。researcher など一部ロールは環境依存あり。
>
> Issues・PRs 歓迎です。大きなカスタマイズはフォークを推奨します。

---

## ライセンス

MIT License

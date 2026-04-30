# AI編集部OS

フリーランス編集者・ライターの制作ワークフローを、役割別AIエージェントが支える編集環境。

**コンセプト：「じぶん編集部を持とう」**

Claude Code（Anthropic）の [サブエージェント機能](https://docs.anthropic.com/ja/docs/claude-code/overview) を活用し、取材前のリサーチから文字起こし・執筆・校正・公開までを一気通貫で回す。

---

## ワークフロー

```
researcher（背景調査）
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
├── CLAUDE.md           ← オーケストレーター（Claude Codeが自動読み込み）
├── roles/              ← ロール別ルール定義
│   ├── researcher.md
│   ├── transcriber.md
│   ├── writer.md
│   ├── reviewer.md
│   ├── editor.md
│   ├── scheduler.md
│   ├── recap.md
│   ├── planner.md      ← 次フェーズ
│   ├── publisher.md    ← 次フェーズ
│   ├── performance.md  ← 次フェーズ
│   └── designer.md     ← 次フェーズ
├── presets/            ← 媒体別プリセット
│   ├── narrative-a/    ← ナラティブ・記者常体/引用敬体
│   ├── narrative-b/    ← ナラティブ・記者敬体/引用敬体
│   ├── qa/             ← Q&A対話形式
│   └── _template/      ← 自分の媒体を追加するテンプレート
└── scripts/
    └── transcribe.py   ← 文字起こしスクリプト（AmiVoice + AWS Transcribe）
```

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/YOUR_USERNAME/ai-editorial-os.git
cd ai-editorial-os
```

### 2. CLAUDE.md を配置

Claude Code はカレントディレクトリ〜ホームディレクトリを遡って `CLAUDE.md` を読み込む。
このリポジトリを任意の場所に置き、プロジェクトルートとして使用する。

```bash
# 例：ホームディレクトリ直下に置く場合
cp CLAUDE.md ~/CLAUDE.md
# ※ ロールやプリセットへのパスをコピー先に合わせて書き換える
```

または、このフォルダ内で Claude Code を起動すれば `CLAUDE.md` が自動読み込みされる。

### 3. 環境変数を設定（文字起こしを使う場合）

```bash
export AMIVOICE_API_KEY="your_amivoice_api_key"
export TRANSCRIBE_S3_BUCKET="your-s3-bucket-name"
export AWS_REGION="ap-northeast-1"  # デフォルト値。変更する場合のみ設定
```

AmiVoice API キー取得：https://acp.amivoice.com/  
AWS S3 バケットは事前に作成しておく（AWS Transcribe の一時保存用）。

### 4. Python依存パッケージのインストール（文字起こしを使う場合）

```bash
pip install anthropic boto3 requests
```

---

## 使い方

Claude Code を起動し、自然言語で指示する。

```
# リサーチ
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

## Claude.ai での使い方

Claude Code を使わない場合でも、`writer` と `reviewer` はそのまま Claude.ai で使えます。

1. `roles/writer.md` または `roles/reviewer.md` を開いてファイル全体をコピー
2. Claude.ai のチャットに貼り付けて送信
3. そのまま指示を続ける（「文字起こしをもとに記事を書いて」など）

「先祖返り防止」セクションは Claude Code 専用の指示のため Claude.ai では機能しませんが、動作に影響はありません。

---

## 動作環境

- [Claude Code](https://docs.anthropic.com/ja/docs/claude-code/overview)（Anthropic）
- Python 3.9 以上（文字起こしスクリプトを使う場合）
- AmiVoice API アカウント（日本語文字起こしを使う場合）
- AWS アカウント・S3バケット（英語文字起こしを使う場合）

---

## ライセンス

MIT License

# AI編集部OS — オーケストレーター

## 機密確認（オーケストレーターのみ／プロジェクト開始時の1回限り）

**この確認はオーケストレーター（メインセッション）のみが、新しいプロジェクト・取材・記事作成の開始時に1回だけ実施する。サブエージェント（transcriber/writer/reviewer等）は実施しない。**

新しいプロジェクトを始めるとき、他の作業に入る前に一言確認する：
「未公開情報・機密情報を含みますか？（y/n）」
- y → 機密情報対応の環境（Bedrock等）に切り替えてから開始
- n → このまま続行

## ロール

各ロールの定義は `./roles/` を参照。

| ロール | 担当 |
|--------|------|
| researcher | 調査・情報収集 |
| planner | 取材設計・質問票作成 |
| interviewer | 自己インタビュー（暗黙知の顕在化） |
| transcriber | 文字起こし・クレンジング |
| writer | 本文執筆 |
| reviewer | 仕上げパス・発言照合 ※**Agentとして別起動**（下記参照） |
| editor | 最終調整・オーケストレーション |
| publisher | 公開処理 |
| scheduler | スケジュール管理 |
| recap | 日次振り返り |
| performance | パフォーマンス分析 |
| designer | デザイン・ビジュアル制作 |

## 媒体プリセット

記事制作を開始するとき：

- **媒体名が明示されている**
  → 対応するプリセットを即座に読み込む `./presets/{媒体ディレクトリ}/CLAUDE.md`
- **媒体名が不明**（「記事をつくります」のみ）
  → 「どの媒体向けですか？」と一言確認してからプリセットを読み込む

プリセットがない媒体の場合はロールファイルの設定に従い、記事タイプ・文体・字数をユーザーに確認する。

## 記事制作ワークフロー

オーケストレーターがハブとして各エージェントの完了レポートを受け取り、次のエージェントへのbriefingに織り込む。媒体別の詳細手順は各プリセットに記載。

```
planner（style-spec.md 出力）
  ↓ orchestrator中継（字数目標・フォーマット・サンプルパスをwriterに渡す）
[文字起こし]（後述：オーケストレーターが直接実行）
  ↓ クレンジング済み transcript.txt
writer（初稿 → v1.md）
  ↓ orchestrator中継（writerの懸念事項を重点確認項目としてreviewerに渡す）
reviewer（初回チェック・v1 を対象、🔴/🟡A/🟡B/🟢で分類）
  ↓ orchestrator中継（🔴と🟡Aを修正指示・🟡Bは現状維持としてwriterに渡す）
writer（修正 → v2.md・v1 は残置）
  ↓ orchestrator中継（修正箇所を明示してreviewerに渡す）
reviewer（再チェック・v2 を対象）
  ↓ orchestrator中継（残課題サマリーを添えて報告）
ユーザー（直接Editで最終仕上げ・AI再生成は v2 で打ち止め）
```

---

## ドラフトのバージョニング（全媒体共通ルール）

writer 出力は**毎回別ファイルに保存**し、上書きしない。媒体プリセットに関係なく全パイプラインに適用する。

| バージョン | 由来 | 保存先 | 扱い |
|---|---|---|---|
| **v1** | writer 初稿 | `{base}-draft-v1.md` | reviewer1 が照合し懸念点を末尾に追記 |
| **v2** | writer 修正版 | `{base}-draft-v2.md`（**v1 は残置**） | reviewer2 が再チェック。**AI 再生成はここで打ち止め** |
| v2 以降 | ユーザーの直接 Edit | `{base}-draft-v2.md` を上書き | 部分指示が来たら v2 を Edit。新バージョン（v3）は作らない |

**Why：**
- v2 が生成されている間に、ユーザーが v1 ＋ reviewer 指摘を並列レビューできる。v1 を上書きすると差分が追えず並列処理が成立しない
- v2 以降はユーザーの判断・トーンで仕上げる工程。AI が再生成するとユーザーの編集が消える

`{base}` は媒体・案件ごとに決める。

---

## reviewer 出力の4段階区分（全媒体共通ルール）

reviewer は指摘を以下の 4 段階で分類する。writer 修正フェーズで扱いが異なるため、混ぜずに明示する。

| 区分 | 意味 | writer 修正フェーズでの扱い |
|---|---|---|
| 🔴 要修正 | 致命的・writer が必ず対応 | 修正指示リストに含める |
| 🟡A writer 対応可 | 表記統一・字数調整など機械的に対応可能 | writer に判断委ね（無理なら現状維持） |
| 🟡B ユーザー判断待ち | 固有名詞の正誤・媒体方針判断など、人間の確認が必要 | **writer は触らない**（現状維持を明示） |
| 🟢 問題なし | 照合済み | 修正指示には含めない |

🟡B はユーザーが Web 一次ソース等で確定する責任範囲。writer/reviewer に確定を求めない。

---

## 質問票は orchestrator が直接対話で作成する（planner Agent を経由しない）

ユーザーが「質問票をつくります」「取材を設計して」「インタビューガイドを作って」と言ったら、サブエージェントは起動せず、orchestrator が `./roles/planner.md` と該当媒体プリセットの `question_templates/` を Read してから着手する。

理由：planner はユーザーへの問い返し（「一番聞きたいことは何ですか」等）を前提に設計されているため、サブエージェント起動だと中継できずパイプラインが詰まる。

## 文字起こしは orchestrator が直接実行する（transcriber Agent を経由しない）

サブエージェント経由だと機密確認が再起動するたびに走り、応答できずパイプラインが止まる。文字起こしは「思考の委譲」ではなく「スクリプト実行」なので、orchestrator が `Bash` ツールで直接呼ぶ。

```bash
python3 ./scripts/transcribe.py --lang ja <音声> <資料1> [資料2 ...]
```

`run_in_background: true` で投入し、出力ファイル `{base}_transcript_ja_sonnet45.txt` の生成を `until [ -f ... ]` ループで監視する。プロセスが死んだら即座にユーザーに報告する。

## writerを起動するときの必須パラメータ（初稿 → v1）

以下の情報を**必ず明示的に渡す**。省略するとwriterが独自判断で補完し、品質劣化の原因になる。**保存先は必ず v1.md**。

```
Agent(
  subagent_type="general-purpose",
  prompt="あなたはAI編集部OSのwriterです。./roles/writer.md に従って執筆してください。

style-spec.md：{style_spec_path}
字数目標：{word_count}字
フォーマット：{format}  ← A.ナラティブ／B.Q&A対話／C.講演レポート／D.パネル のいずれか
サンプル記事：{sample_path}
文字起こし：{transcript_path}

ドラフトを {base}-draft-v1.md に保存してください。"
)
```

## writerがドラフトを保存したら即座にreviewerを起動する（v1 を対象）

writerがドラフトファイルを保存した直後、ユーザーへの報告より前に、reviewerをAgentとして起動する。**4段階区分での出力を要求する**：

```
Agent(
  subagent_type="general-purpose",
  prompt="あなたはAI編集部OSのreviewerです。
./roles/reviewer.md のモード2（記事レビュー）に従い、以下を照合してください。

ドラフト：{base}-draft-v1.md
ソース（文字起こし）：{transcript_path}
ソース（PDF等）：{pdf_path}  ※ある場合のみ

指摘は以下の4段階で分類すること：
- 🔴 要修正（致命的・writer が必ず対応）
- 🟡A writer 対応可（表記統一・字数調整など機械的に対応可能）
- 🟡B ユーザー判断待ち（固有名詞の正誤・媒体方針判断など人間の確認が必要）
- 🟢 問題なし（照合済み）

懸念点リストをドラフトファイルの末尾に追記してください。"
)
```

reviewerの完了後、「ドラフトと懸念点リストを保存しました」とユーザーに報告する。

## writer 修正フェーズ（v1 を読み v2 に書き出す）

reviewer1 完了後、writer に修正を依頼するときは **入力（v1）と出力（v2）を別ファイル**にする。🟡B は writer に「触らない」よう明示する：

```
Agent(
  subagent_type="general-purpose",
  prompt="あなたはAI編集部OSのwriterです。
以下の修正指示に従い、v1 を読み込んだうえで v2 として新規保存してください。
v1 は上書きせず残すこと。

入力ドラフト（読込）：{base}-draft-v1.md
出力ドラフト（書込）：{base}-draft-v2.md

修正指示（🔴 要修正・必ず対応）：
{reviewer_required}

修正推奨（🟡A writer 対応可・writer が判断・無理なら現状維持）：
{reviewer_writer_optional}

ユーザー判断待ち（🟡B・writer は触らない・現状維持）：
{reviewer_user_pending}

修正完了後、writer完了レポート（対応状況付き）を出力してください。"
)
```

## reviewer 再チェック（v2 を対象）

```
Agent(
  subagent_type="general-purpose",
  prompt="あなたはAI編集部OSのreviewerです。
モード2で修正版ドラフト v2 を再チェックしてください。

ドラフト：{base}-draft-v2.md
ソース：{transcript_path}
修正箇所（🔴・🟡A）：
{writer_fixed_items}
前回指摘で対応不可だった項目：
{writer_unresolved}
ユーザー判断待ち（🟡B・現状維持で問題なし）：
{reviewer_user_pending}

reviewer完了レポート（修正確認結果付き）を出力してください。
原則として AI 再生成は v2 で打ち止め。v2 で 🔴 が残る場合のみ writer に再差し戻し。"
)
```

reviewer2 完了後、ユーザーに報告：

```
ドラフトの確認をお願いします。
- ドラフトパス：{base}-draft-v2.md
- ユーザー判断待ち（🟡B）：{user_pending_items}
- 残課題：{remaining_issues}（なければ「なし」）

v2 以降はユーザーが直接 Edit で仕上げる工程に入ります。AI による再生成は行いません。
```

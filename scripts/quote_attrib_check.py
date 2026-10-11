#!/usr/bin/env python3
"""カギ括弧の発言に帰属（〜氏は…）があるかを検査する。
使い方: python3 quote_attrib_check.py 原稿.md [--min 20]
文脈で話者が明らかな裸引用（直前文で「〜氏は…を置いている。「…」」等）も拾う＝ヒットは要確認。
媒体によっては裸引用を一定数まで許容する（各パート最大1・隣接段落で連続させない等）。
★圧縮・writer修正・docx化の直前に必ず回す（圧縮では帰属の尾が真っ先に削られ、脱落しやすい）。
★未解決の【要確認…】も数える。docx化の直前は0件であること。
帰属ありとみなす形:
  1. 「…」と○○氏は述べた（直後の同一文に「と」＋「氏」）
  2. ○○氏は「…」（同一文の前半に「氏」）
  3. ○○氏はこう語った。「…」／次のように述べた。「…」（直前文が こう/次のように/締めくくった 等で終わる）
20字未満のカギ括弧は用語・呼称、半分以上が英数字のものはイベント名等とみなし対象外。
「…」と続けた 型は、同じ段落の前半に話者名があれば帰属ありとみなす。"""
import re, sys
args=sys.argv[1:]; MIN=20
if '--min' in args: i=args.index('--min'); MIN=int(args[i+1]); del args[i:i+2]
# 末尾のレビュー追記・控えだけを外す（最初の --- で切ると、タイトル案の下に --- がある原稿は本文を一切検査しなくなる）
APPX=re.compile(r'^\s*#+\s*.*(レビュー|懸念|チェック|完了レポート|削除候補|控え|reviewer|writer|落とした素材)',re.I)
text='\n---\n'.join(c for c in open(args[0]).read().split('\n---\n') if not APPX.match(c.lstrip('\n')))
text=re.sub(r'<!--.*?-->','',text,flags=re.S)
NAME=r'(氏|さん|社長|理事長|CEO|担当者)'
bad=0
for ln,para in enumerate(text.split('\n'),1):
    if para.startswith(('#','【図')) or '「' not in para: continue
    for m in re.finditer(r'「([^「」]*(?:「[^」]*」[^「」]*)*)」',para):
        q=m.group(1)
        if len(q)<MIN: continue
        if sum(c.isascii() for c in q)>len(q)*0.5: continue  # イベント名・英語の製品名
        before=para[:m.start()]; after=para[m.end():]
        sent_before=re.split(r'[。！？]',before)[-1]
        prev_sent=re.split(r'[。！？]',before.rstrip('。'))[-1] if before.rstrip().endswith('。') else ''
        tail=re.split(r'[。！？]',after)[0]
        ok = (re.match(r'と',tail) and (re.search(NAME,tail) or re.search(NAME,before))) \
          or re.search(NAME,sent_before) \
          or (prev_sent and re.search(r'(こう|次のように|以下のように|締めくくった|結んだ|続けた|語った|述べた)$',prev_sent.strip()) and re.search(NAME,before[-80:]))
        ok = ok or re.match(r'\s*（[^（）]{1,10}）',after)  # 「…」（山田）＝名字カッコ止め（導入事例の型）
        nxt=re.split(r'[。！？]',after.lstrip('。'))[0]
        ok = ok or (re.search(r'(そう|こう)(述べ|語|話|言|明か|結|締め)',nxt) and re.search(NAME,nxt))  # 「…」。山田氏はそう述べ
        if not ok:
            bad+=1; print(f'L{ln}: 帰属なし（要確認）「{q[:28]}…」{after[:12]}')
print(f'→ 帰属なし {bad}件' if bad else '✅ 帰属なしの発言はありません')
# 未解決の【要確認】：文字起こし由来の【要確認：文字起こし[話者 MM:SS]】・根拠不明の数値など。納品前にゼロにする
left=[(ln,m.group(0)) for ln,para in enumerate(text.split('\n'),1) for m in re.finditer(r'【要確認[^】]*】',para)]
for ln,mk in left: print(f'L{ln}: 未解決 {mk}')
print(f'→ 未解決の【要確認】 {len(left)}件（納品前に音声・一次資料で確定して消す）' if left else '✅ 未解決の【要確認】はありません')
sys.exit(1 if (bad or left) else 0)

#!/usr/bin/env python3
"""draftcheck.py — ドラフトの字数・引用率・冗長重複を機械検査する

使い方:
    python3 draftcheck.py <ドラフト.md> [--target 4000]

出力:
    1. 本文字数（全体・章別）と目標との差
    2. 引用本数・引用字数・引用率（全体・章別）
    3. 近接重複語（同じ語が近い範囲で繰り返されている箇所）
    4. 同義反復の疑い（隣接する文どうしが似すぎている箇所）
    5. 引用と直前の地の文の内容重複の疑い

注意:
    - 見出し行（#で始まる）と、付録セクション以降は本文字数に含めない
    - 付録＝「引用箇所とタイムコード対応表」「懸念事項リスト」「reviewer チェック」等
    - あくまで検出補助。最終判断は人間（またはreviewer）が行う
"""

import re
import sys

APPENDIX_PAT = r'^#+\s*[\[［]?(引用箇所|懸念事項|reviewer|削除候補|タイムコード)'


def load_body(path):
    """本文だけを取り出す（付録以降と見出し行を除外）"""
    raw = open(path, encoding='utf-8').read()
    lines = raw.split('\n')
    body_lines = []
    for line in lines:
        if re.match(APPENDIX_PAT, line):
            break
        body_lines.append(line)
    return '\n'.join(body_lines)


def norm(text):
    return re.sub(r'\s', '', text)


def split_sections(body):
    """[(見出し, 本文), ...] に分割。冒頭のリードは見出し '（リード）' とする"""
    parts = re.split(r'^##\s+(.+)$', body, flags=re.M)
    out = [('（リード）', parts[0])]
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1]))
    return out


def strip_headings(text):
    return '\n'.join(l for l in text.split('\n') if not l.startswith('#'))


def quotes_of(text):
    return re.findall(r'「[^」]*」', text)


def report_length(sections, target):
    print('=' * 60)
    print('1. 字数と引用率')
    print('=' * 60)
    total_b = total_q = total_n = 0
    for title, text in sections:
        t = strip_headings(text)
        b = norm(t)
        qs = quotes_of(t)
        qc = sum(len(norm(q)) for q in qs)
        total_b += len(b)
        total_q += qc
        total_n += len(qs)
        ratio = qc / len(b) * 100 if b else 0
        print(f'  {title[:34]:36s} {len(b):5d}字  引用{len(qs):2d}本 {ratio:5.1f}%')
    ratio = total_q / total_b * 100 if total_b else 0
    print('-' * 60)
    print(f'  合計 {total_b}字 / 引用{total_n}本 {total_q}字 = {ratio:.1f}%')
    if target:
        diff = total_b - target
        sign = '+' if diff >= 0 else ''
        pct = diff / target * 100
        print(f'  目標 {target}字 に対して {sign}{diff}字（{sign}{pct:.1f}%）')
    if ratio > 30:
        print(f'  ⚠ 引用率が30%を超えています（目標15〜30%）')
    print()


def bigrams(s):
    s = norm(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def jaccard(a, b):
    A, B = bigrams(a), bigrams(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def build_stopwords(body, top_n=12):
    """記事全体の頻出語＝そのテーマの中心語なので、重複検査から除外する。
    「ドローン」「機体」「点検」のような避けようのない語を自動で外すのが狙い。"""
    text = strip_headings(body)
    word_pat = re.compile(r'[一-龥]{2,}|[ァ-ヶー]{3,}')
    counts = {}
    for w in word_pat.findall(text):
        counts[w] = counts.get(w, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: -x[1])
    return {w for w, c in ranked[:top_n]}


def report_repeated_words(body):
    """近接重複語：中心語を除いた語が、近い範囲で繰り返されている箇所"""
    print('=' * 60)
    print('3. 近接重複語（中心語を除く。同じ語が近い範囲で繰り返されている）')
    print('=' * 60)
    stop = build_stopwords(body)
    print(f'  ※ 除外した中心語: {"、".join(sorted(stop))}')
    text = strip_headings(body)
    paras = [p for p in text.split('\n') if norm(p)]
    word_pat = re.compile(r'[一-龥]{2,}|[ァ-ヶー]{3,}')
    hits = []
    for i, p in enumerate(paras):
        window = ' '.join(paras[max(0, i - 1):i + 2])
        counts = {}
        for w in word_pat.findall(p):
            if w in stop:
                continue
            counts[w] = counts.get(w, 0) + 1
        for w, c in counts.items():
            wide = window.count(w)
            if c >= 2 or wide >= 3:
                hits.append((i + 1, w, c, wide))
    if not hits:
        print('  検出なし')
    for idx, w, c, wide in sorted(hits, key=lambda x: (-x[3], -x[2]))[:15]:
        print(f'  段落{idx:3d}  「{w}」 段落内{c}回 / 前後3段落で{wide}回')
    print()


def report_similar_sentences(body, threshold=0.32):
    """同義反復：隣接する文どうしが似すぎている"""
    print('=' * 60)
    print(f'4. 同義反復の疑い（隣接文の類似度 >= {threshold}）')
    print('=' * 60)
    text = strip_headings(body)
    sents = [s for s in re.split(r'(?<=。)', text.replace('\n', '')) if norm(s)]
    found = False
    for a, b in zip(sents, sents[1:]):
        if len(norm(a)) < 12 or len(norm(b)) < 12:
            continue
        j = jaccard(a, b)
        if j >= threshold:
            found = True
            print(f'  類似度 {j:.2f}')
            print(f'    A: {a.strip()[:60]}')
            print(f'    B: {b.strip()[:60]}')
    if not found:
        print('  検出なし')
    print()


def report_quote_overlap(body, threshold=0.25):
    """引用と直前の地の文が同じことを言っていないか"""
    print('=' * 60)
    print(f'5. 引用と直前の地の文の重複（類似度 >= {threshold}）')
    print('=' * 60)
    text = strip_headings(body)
    paras = [p for p in text.split('\n') if norm(p)]
    found = False
    for i, p in enumerate(paras):
        qs = quotes_of(p)
        if not qs:
            continue
        before = paras[i - 1] if i else ''
        # 同じ段落内の引用より前の地の文も見る
        lead_in = p.split('「')[0]
        for src, label in ((before, '直前の段落'), (lead_in, '同じ段落の導入部')):
            if len(norm(src)) < 15:
                continue
            for q in qs:
                if len(norm(q)) < 15:
                    continue
                j = jaccard(src, q)
                if j >= threshold:
                    found = True
                    print(f'  類似度 {j:.2f}（{label}）')
                    print(f'    地の文: {src.strip()[:60]}')
                    print(f'    引用  : {q[:60]}')
    if not found:
        print('  検出なし')
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    target = None
    if '--target' in sys.argv:
        target = int(sys.argv[sys.argv.index('--target') + 1])

    body = load_body(path)
    sections = split_sections(body)

    report_length(sections, target)
    print('=' * 60)
    print('2. 章別の偏り')
    print('=' * 60)
    lens = [(t, len(norm(strip_headings(x)))) for t, x in sections[1:]]
    if lens:
        avg = sum(n for _, n in lens) / len(lens)
        for t, n in lens:
            flag = '  ← 突出（圧縮の第一候補）' if n > avg * 1.25 else ''
            print(f'  {t[:34]:36s} {n:5d}字（平均比 {n / avg:.2f}）{flag}')
    print()

    report_repeated_words(body)

    print('=' * 60)
    print('4. 機械では拾えないので、必ず読んで確認すること')
    print('=' * 60)
    print("""  以下は文字の重なりでは検出できない（実測で類似度0.09〜0.14しか出ず、
  無関係な文と区別がつかないため機械判定は断念した）。reviewer が通読して判断する。

  [ ] 同義反復：言い方を変えて同じことを2回言っていないか
      例「点検データとしては使いにくい」と「点検としては失敗となる」が並記
  [ ] 引用と地の文の重複：引用の直前に地の文で内容を先取りしていないか
      ※これは字数と引用率を同時に押し上げる最頻出パターン
  [ ] 同じ論点の引用が近接して複数ないか（1本に統合できないか）
  [ ] 説明の3連：地の文→引用→地の文で同じ概念を繰り返していないか
      例 ホバリングの説明が3段落連続""")
    print()
    print('※ 検出はあくまで候補。削除・統合の判断は文脈を読んで行うこと。')


if __name__ == '__main__':
    main()

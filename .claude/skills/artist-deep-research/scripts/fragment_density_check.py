#!/usr/bin/env python3
"""Per-song quote-density gate (quoted fragments + unquoted 8-char Korean runs; song titles exempt) for research reports.

fragment_density_check.py <collection_dir> <report.md>

Collects every quoted fragment in the report (「…」, "…", “…”, ‘…’, '…') and,
per song, measures how much of the song's original lines AND Korean meaning
lines those fragments cover. Fails if any song has >10% of either text quoted,
or any single line ≥50% quoted. Prints only song titles and percentages.
"""
import sys, os, re, glob
coll, rep = sys.argv[1], sys.argv[2]
r = open(rep, encoding='utf-8').read()
# song titles (original and README Korean 뜻/읽기) are allowed: blank them out first
titles = set()
try:
    for l in open(os.path.join(coll, 'README.md'), encoding='utf-8'):
        c = [x.strip() for x in l.split('|')]
        if len(c) > 7 and c[1].isdigit():
            m = re.match(r'\[(.*)\]\(', c[3]); titles.update(t for t in (m.group(1) if m else c[3], c[5], c[6]) if len(t) >= 2)
except OSError:
    pass
for t in sorted(titles, key=len, reverse=True):
    r = r.replace(t, ' ')
NGRAM = 8  # unquoted Korean runs this long that match a meaning line also count
rn = re.sub(r'\s+', '', r)
frags = set()
for pat in (r'「([^「」]{2,40})」', r'"([^"\n]{2,40})"', r'“([^”\n]{2,40})”', r'‘([^’\n]{2,40})’', r"'([^'\n]{2,40})'"):
    frags.update(f.strip() for f in re.findall(pat, r))
frags = {f for f in frags if len(f) >= 2}

def cover(text, fr):
    mask = [0] * len(text)
    for f in fr:
        for m in re.finditer(re.escape(f), text):
            for i in range(m.start(), m.end()): mask[i] = 1
    return mask

bad = []; rows = []
for p in sorted(glob.glob(os.path.join(coll, '[0-9]*.md'))):
    L = open(p, encoding='utf-8').read().split('\n')
    title = next((l[2:].strip() for l in L if l.startswith('# ')), os.path.basename(p))
    orig, mean = [], []
    for i, l in enumerate(L):
        s = l.strip()
        if s.startswith('**') and s.rstrip().endswith('**') and not s.startswith('**作') and i + 2 < len(L):
            o = s.strip('*').strip()
            if o == title or not o: continue
            orig.append(o)
            mline = L[i + 2].strip()
            if mline and not mline.startswith('**'): mean.append(mline)
    fr = [f for f in frags if f != title]
    worst_line = 0
    res = []
    for k, lines in enumerate((orig, mean)):
        body = '\n'.join(lines)
        if not body.strip(): res.append(0); continue
        mask = cover(body, fr)
        if k == 1:
            flat = [(i, ch) for i, ch in enumerate(body) if not ch.isspace()]
            fs = ''.join(ch for _, ch in flat)
            for i in range(len(fs) - NGRAM + 1):
                if fs[i:i + NGRAM] in rn:
                    for j in range(i, i + NGRAM): mask[flat[j][0]] = 1
        chars = sum(1 for c in body if c != '\n')
        res.append(sum(mask) / chars if chars else 0)
        pos = 0
        for ln in lines:
            seg = mask[pos:pos + len(ln)]
            if len(ln) >= 6 and sum(seg) >= 0.5 * len(ln): worst_line += 1
            pos += len(ln) + 1
    rows.append((max(res), res[0], res[1], worst_line, title))
    if max(res) > 0.10 or worst_line: bad.append(title)
rows.sort(reverse=True)
for m, a, b, w, t in rows[:15]:
    print(f'JA {a:.0%}  KO {b:.0%}  lines>=50%: {w}  {t}')
print('FAIL' if bad else 'OK', len(bad), 'songs over limit (>10% of original or meaning text quoted, or any line >=50% quoted)')
sys.exit(1 if bad else 0)

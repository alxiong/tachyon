"""Validate every A("phrase"[, occ]) in a chapter file against words.json before rendering."""
import re, sys
from style import anchor, WORDS
src = open(sys.argv[1]).read()
bad = 0
for cls in re.split(r"\nclass ", src)[1:]:
    m = re.search(r'SID = "([\d.]+)"', cls)
    if not m:
        continue
    sid = m.group(1); last = -1
    for ph, occ in re.findall(r'A\("([^"]+)"(?:,\s*(\d+))?\)', cls):
        try:
            t = anchor(sid, ph, int(occ or 1))
            flag = "  <-- out of order" if t < last else ""
            last = max(last, t)
            print(f"{sid} {t:7.2f}  {ph}{flag}")
        except ValueError as e:
            bad += 1; print(f"{sid}   MISSING  {ph}")
sys.exit(1 if bad else 0)

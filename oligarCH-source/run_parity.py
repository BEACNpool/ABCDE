#!/usr/bin/env python3
"""Parity gate: the page's assembled SVG must be byte-identical to build_pfp.build().

Run after ANY change to build_pfp.py or build_pfp_page.py:

    python3 run_parity.py [http://127.0.0.1:8461/]

⚠️ Cases are expanded to a FULL explicit pick before driving the page — the page keeps state
between cases, so a case that leans on defaults inherits the previous case's traits and the
failure looks like an assembler bug when it is only test bleed-through.

Cases deliberately cover: cap-bound short lines, I/L/space strings past 12 chars (the exact
class the old 22*(len-1)+16 scale approximation got wrong), two-line wraps, double spaces,
a no-space long string, an empty line, every mood/prop interaction, and the 32-char maximum.
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import build_pfp as B

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8461/'

CASES = [
    dict(pick=dict(), text='THUG LIFE'),
    dict(pick=dict(eyes='thug', neck='thug'), text='$BEACN'),
    dict(pick=dict(mood='mad', neck='ada'), text='ILL WILL IIII LLLL'),
    dict(pick=dict(mood='mad', prop='joint', bg='smoke'), text='SOMETIMES YOU DEAL WITH OLIGARCH'),
    dict(pick=dict(mood='duck', prop='grill', hat='crown', bg='ivyom'), text='I VOTE YES ON ME F5'),
    dict(pick=dict(mark='teardrop2', bg='bars'), text='LLLLIIIILLLLIIIILLL'),
    dict(pick=dict(mood='tongue', bg='hotel', hat='halo'), text=''),
    dict(pick=dict(prop='cigar', neck='tie', bg='org'), text='AAAA  BBBB CCCC DDDD'),
    dict(pick=dict(eyes='laser', bg='tgm'), text='ALL YOUR MONEY'),
    dict(pick=dict(prop='diamond', bg='dnpg', neck='ada'), text='WE ARE ALL GOING TO MAKE IT 100'),
    dict(pick=dict(pet='flamingo', bg='hotel', hat='crown'), text='AFRICA'),
    dict(pick=dict(pet='crane', neck='ada', bg='smoke', mood='mad'), text='THE BIRDS WORK FOR ME'),
]

DEF = dict(mood='signature', prop='none', bg='byttg', hat='none', eyes='none',
           neck='none', mark='none', pet='none')
full_cases, refs = [], []
for c in CASES:
    p = dict(DEF); p.update(c['pick'])
    full_cases.append(dict(pick=p, text=c['text']))
    mouth = p['prop'] if p['prop'] != 'none' else p['mood']
    refs.append(B.build(bg=p['bg'], hat=p['hat'], eyes=p['eyes'], mouth=mouth,
                        neck=p['neck'], mark=p['mark'], pet=p['pet'], text=c['text']))

out = subprocess.run(['node', str(HERE / 'paritytest.mjs'), URL, json.dumps(full_cases)],
                     capture_output=True, text=True)
if out.returncode:
    print(out.stderr[-2000:]); sys.exit(1)
got = json.loads(out.stdout)
if got['errors']:
    print('PAGE ERRORS:', got['errors']); sys.exit(1)

fails = 0
for i, (ref, page) in enumerate(zip(refs, got['svgs'])):
    ok = ref == page
    fails += not ok
    print(f'  {"PASS" if ok else "FAIL"}  case {i}  {len(ref):6,} B  text={CASES[i]["text"]!r}')
    if not ok:
        for j, (a, b) in enumerate(zip(ref, page)):
            if a != b:
                print(f'        diff at {j}: py …{ref[max(0,j-30):j+50]!r}\n'
                      f'                 page …{page[max(0,j-30):j+50]!r}')
                break
        else:
            print(f'        length: py {len(ref)} vs page {len(page)}')
print('\n  ALL PARITY PASS' if not fails else f'\n  {fails} FAILED')
sys.exit(1 if fails else 0)

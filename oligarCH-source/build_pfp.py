#!/usr/bin/env python3
"""The oligarCH PFP creator — trait catalogue + assembler.

Unlocked by holding piece 9. The user picks traits, the page assembles ONE svg from the chosen
parts only, and that svg goes on chain in the mint. Cost is per-selection, not per-catalogue:
an unpicked trait costs nothing because it is never in the file.

⚠️ TRAITS ARE OVERLAYS, NOT SURGERY. The canonical head from reference/character.md is one
monolithic block with its glasses, brows and mouth baked in. Cutting them out by regex would be
fragile and would drift the character. Everything draws ON TOP — the correct draw order anyway,
and it keeps every PFP provably the same man underneath.

⚠️ ALL TRAIT COORDINATES ARE IN THE CHARACTER'S NATIVE SPACE, the same one character.md uses:
    lenses (540,325) and (632,325) r=30   ·   head centre (585,310) rx130 ry122
    ears (454,330) (716,330)              ·   mouth spans x 530-646, y 378-420
    chin/beard bottom ~470                ·   shoulders below ~560
Never hand-convert to screen coords; the assembler applies one transform at the end.

  python3 build_pfp.py --sheet            # contact sheet of the catalogue
  python3 build_pfp.py --eyes thug --mouth joint --neck thug --mark teardrop --text "THUG LIFE"
"""
import argparse, math, pathlib, re, subprocess

# ⚠️ PYTHON AND JAVASCRIPT DISAGREE ON round(-5.5). Python's format('.0f') uses banker's
# rounding (-6); JS Math.round rounds half toward +Infinity (-5). The preview and the minted
# bytes MUST be the same string, so both sides use this one rule instead: floor(v + 0.5).
def R(v):
    return math.floor(v + 0.5)

HERE = pathlib.Path(__file__).parent
REF = pathlib.Path.home() / '.claude/skills/oligarch/reference'
_b = re.findall(r'```xml\n(.*?)\n```', (REF / 'character.md').read_text(), re.S)
HEAD_DEFS, HEAD = _b[0], _b[1]
_ALPHA_SRC = (REF / 'alphabet.md').read_text()
ALL_GLY = dict(re.findall(r'<path id="([A-Z0-9])" d="([^"]+)"/>', _ALPHA_SRC))
# '$' cannot be an XML id in strict parsers and cannot be referenced as href="#$", so the
# currency mark ships under the id DL. Everything else is A-Z 0-9 straight from the reference.
_dl = re.search(r'<path id="\$" d="([^"]+)"/>', _ALPHA_SRC)
if _dl:
    ALL_GLY['$'] = _dl.group(1)
ADV = {'I': 17, 'L': 17}
GID = {'$': 'DL'}                 # character -> svg id, where they differ

# ⚠️ Raised 10 -> 32 on David's call (2026-07-31): the line should INVITE a saying, not just
# fit a ticker. Legibility is handled by the layout, not the limit — once the single-line
# scale would drop below 2.0 the band wraps to two balanced lines (split at the space nearest
# equal width), so even 32 chars renders large. Bytes are irrelevant (~30 B per char; the
# heaviest trait load + 32 chars is still ~63% of the tx cap — measured, see git history).
# There is deliberately NO content filter: the mint is permissionless and anyone can hand-build
# the tx anyway, every mint is signed by a traceable wallet, and the public wall has a
# hand-maintained blocklist (wall_blocklist.txt) as the backstop if something cannot stand.
MAX_TEXT = int(__import__("os").environ.get("PFP_MAX", 32))
OK_CHARS = set(ALL_GLY) | {' '}

K = 'stroke="#111" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"'
SKIN, SHIRT, CREAM, TAN, RED = '#f2cfa6', '#6ba3d0', '#f2ece0', '#c08f57', '#ed1c24'
GOLD, DARK, METAL, ICE = '#e0b02c', '#1f1f23', '#75757c', '#bfe9f5'
BEARD = '#bb9668'

# Painting over the canonical mouth means painting over the BEARD, so the patch has to be the
# beard's fill AND its hatch at the same opacity, or it shows as a bald smear.
COVER = (f'<ellipse cx="588" cy="398" rx="74" ry="34" fill="{BEARD}"/>'
         f'<ellipse cx="588" cy="398" rx="74" ry="34" fill="url(#h)" opacity=".55"/>')
LIP = 'fill="none" stroke="#111" stroke-width="9" stroke-linecap="round"'

# ── BACKGROUNDS — one per series piece, in release order, plus the pen ────────────
# Each is a CHEAP motif of its piece (the bust hides the middle, so motifs live in the top
# band, the upper sides and behind the shoulders). Reuse of the head's hatch pattern url(#h)
# is free — it ships in HEAD_DEFS regardless.
BG = {
    # 1 BYTTG — the plain grey field, exactly like the piece. It had flames once; David read
    # them as "4 red claws" on the default view and the REAL piece's background is bare grey
    # anyway (the red belongs to the caption). Plain is faithful AND fixes the start screen.
    'byttg': '<rect width="1024" height="1024" fill="#c3c3c3"/>',
    # 2 TGM — inside the video player
    'tgm':   '<rect width="1024" height="1024" fill="#e9e7e3"/>'
             '<rect width="1024" height="86" fill="#17171b"/>'
             '<rect y="860" width="1024" height="164" fill="#17171b"/>'
             f'<rect x="28" y="21" width="64" height="44" rx="12" fill="{RED}"/>'
             '<path d="M50 32v22l20-11z" fill="#fff"/>'
             '<path d="M0 860h1024" stroke="#3a3a42" stroke-width="9"/>'
             f'<path d="M0 860h430" stroke="{RED}" stroke-width="9"/>'
             f'<circle cx="430" cy="860" r="15" fill="{RED}"/>'
             '<path d="M38 912v44l36-22z" fill="#fff"/>',
    # 3 IVYOM — the treasury vault, one bag already out
    'ivyom': '<rect width="1024" height="1024" fill="#c9c7c3"/>'
             '<g stroke="#111" stroke-width="8">'
             '<rect x="14" y="14" width="306" height="430" fill="#4a4a52"/>'
             '<rect x="46" y="46" width="242" height="366" fill="#3a3a42"/>'
             f'<circle cx="167" cy="229" r="64" fill="{METAL}"/>'
             '<path d="M167 173v112M111 229h112M128 190l78 78M206 190l-78 78" fill="none"/></g>'
             f'<g stroke="#111" stroke-width="7"><path d="M886 128l-16 30q-50 16-50 62'
             f' 0 54 66 54t66-54q0-46-50-62l-16-30z" fill="{GOLD}"/>'
             '<path d="M870 240l16-44 16 44M864 222h44M861 232h50" fill="none" '
             'stroke-width="5" stroke-linecap="round"/></g>',
    # 4 ORG — the drum, and the tube still paying out
    'org':   '<rect width="1024" height="1024" fill="#cfcdc9"/>'
             '<g stroke="#111" stroke-width="8" transform="rotate(14 118 140)">'
             '<rect x="72" y="-40" width="92" height="330" fill="#8a8a92"/>'
             '<rect x="72" y="-40" width="92" height="330" fill="url(#h)" opacity=".3"/></g>'
             f'<g stroke="#111" stroke-width="7"><circle cx="200" cy="356" r="24" fill="{GOLD}"/>'
             f'<circle cx="242" cy="436" r="18" fill="{GOLD}"/></g>'
             '<g stroke="#111" stroke-width="8">'
             f'<circle cx="856" cy="196" r="128" fill="{CREAM}"/>'
             '<circle cx="856" cy="196" r="128" fill="url(#h)" opacity=".35"/>'
             f'<circle cx="818" cy="166" r="26" fill="{GOLD}"/>'
             '<circle cx="898" cy="228" r="26" fill="#c3c3c3"/>'
             f'<circle cx="888" cy="146" r="21" fill="{TAN}"/></g>',
    # 5 HOTEL — you can check out any time you like
    'hotel': '<rect width="1024" height="1024" fill="#efe9df"/>'
             '<circle cx="200" cy="150" r="64" fill="#2b2b31"/>'
             '<circle cx="228" cy="132" r="56" fill="#efe9df"/>'
             '<g fill="#26262c"><rect x="700" y="60" width="70" height="96"/>'
             '<rect x="820" y="60" width="70" height="96"/>'
             '<rect x="700" y="210" width="70" height="96"/>'
             '<rect x="820" y="210" width="70" height="96"/></g>'
             '<path d="M262 1024V620q250-210 500 0v404z" fill="#3a3a40"/>',
    # 6 NDL — two doors left, one already open
    'ndl':   '<rect width="1024" height="1024" fill="#e7e2d8"/>'
             '<rect x="392" y="0" width="240" height="324" fill="#1c1c22"/>'
             f'<g stroke="#111" stroke-width="8">'
             f'<rect x="36" y="70" width="184" height="430" rx="12" fill="{TAN}"/>'
             f'<rect x="804" y="70" width="184" height="430" rx="12" fill="{TAN}"/></g>'
             '<g fill="#111"><circle cx="196" cy="290" r="10"/><circle cx="828" cy="290" r="10"/></g>'
             f'<g fill="{RED}"><ellipse cx="128" cy="530" rx="92" ry="17"/>'
             '<ellipse cx="896" cy="530" rx="92" ry="17"/></g>',
    # 7 DNPG — the title deed
    'dnpg':  f'<rect width="1024" height="1024" fill="{CREAM}"/>'
             f'<rect x="-10" y="-10" width="1044" height="160" fill="{RED}" '
             'stroke="#111" stroke-width="8"/>'
             '<path d="M0 176h1024M0 196h1024" stroke="#111" stroke-width="6"/>'
             f'<g fill="{RED}" stroke="#111" stroke-width="6">'
             '<path d="M56 560v-26l32-22 32 22v26z"/><path d="M148 560v-26l32-22 32 22v26z"/>'
             '<path d="M808 560v-26l32-22 32 22v26z"/><path d="M900 560v-26l32-22 32 22v26z"/></g>',
    # 8 SMOKE — the theatre, fog rolling in
    'smoke': '<rect width="1024" height="1024" fill="#221419"/>'
             '<g fill="#5c1f26" stroke="#111" stroke-width="8">'
             '<path d="M-10-10h176q44 320-30 640l-146 60z"/>'
             '<path d="M1034-10H858q-44 320 30 640l146 60z"/></g>'
             '<g fill="none" stroke="#3d151b" stroke-width="9">'
             '<path d="M64 30q36 280-18 560M960 30q-36 280 18 560"/></g>'
             f'<rect x="210" y="26" width="604" height="86" rx="14" fill="#101012" '
             f'stroke="{RED}" stroke-width="9"/>'
             f'<g fill="{GOLD}">' + ''.join(
                 f'<circle cx="{x}" cy="69" r="9"/>' for x in (252, 342, 432, 512, 592, 682, 772))
             + '</g>'
             '<g fill="#e7e5e1" opacity=".92"><circle cx="120" cy="720" r="62"/>'
             '<circle cx="236" cy="760" r="46"/><circle cx="904" cy="720" r="62"/>'
             '<circle cx="788" cy="760" r="46"/></g>',
    # …and the optional fun one
    'bars':  '<rect width="1024" height="1024" fill="#3a3a42"/>'
             + f'<g stroke="{METAL}" stroke-width="26" stroke-linecap="round">'
             + ''.join(f'<path d="M{x} 0v1024"/>' for x in (96, 256, 416, 576, 736, 896))
             + '</g>',
}

# ── HEADWEAR ──────────────────────────────────────────────────────────────────────
HAT = {
    'none': '',
    'top':   f'<g {K}><path d="M446 196h280M470 194v-150h232v150" fill="{DARK}"/>'
             f'<path d="M470 168h232" fill="none" stroke="{RED}" stroke-width="22"/></g>',
    'crown': f'<g {K}><path d="M452 200 470 78l72 62 44-90 44 90 72-62 18 122z" fill="{GOLD}"/></g>'
             f'<g fill="{RED}" stroke="#111" stroke-width="6"><circle cx="512" cy="152" r="13"/>'
             f'<circle cx="586" cy="140" r="13"/><circle cx="660" cy="152" r="13"/></g>',
    'cap':   f'<g {K}><path d="M456 202q4-124 130-124t130 124z" fill="{SHIRT}"/>'
             f'<path d="M716 202q76 4 94 30-116 18-214 0z" fill="#4d7fa8"/></g>',
    'durag': f'<g {K}><path d="M452 208q6-136 134-136t134 136q-70-40-134-40t-134 40z" fill="#2b2b31"/>'
             f'<path d="M452 190q-70 22-96 74 66 6 104-34z" fill="#2b2b31"/></g>',
    'halo':  f'<g fill="none" stroke="{GOLD}" stroke-width="16">'
             f'<ellipse cx="586" cy="96" rx="118" ry="28"/></g>',
    'horns': f'<g {K} fill="{RED}"><path d="M474 176q-52-40-46-96 44 14 70 66z"/>'
             f'<path d="M698 176q52-40 46-96-44 14-70 66z"/></g>',
    'band':  f'<g {K}><path d="M456 250q130 40 260 0l-6-46q-124 36-248 0z" fill="{RED}"/>'
             f'<path d="M456 226q-56 10-74 44 50 12 82-16z" fill="{RED}"/></g>',
}

# ── EYEWEAR ───────────────────────────────────────────────────────────────────────
EYES = {
    'none':    '',
    'shades':  f'<g {K}><path d="M470 306h232l-8 30q-6 46-52 46t-54-44h-4q-2 44-52 44t-54-46z" '
               f'fill="{DARK}"/><path d="M470 300h232" fill="none" stroke-width="12"/></g>',
    'thug':    f'<g fill="{DARK}"><rect x="452" y="292" width="268" height="30"/>'
               f'<rect x="466" y="322" width="98" height="44"/>'
               f'<rect x="608" y="322" width="98" height="44"/></g>',
    'laser':   f'<g><path d="M540 314h-540v22h540z" fill="{RED}" opacity=".85"/>'
               f'<path d="M632 314h392v22H632z" fill="{RED}" opacity=".85"/>'
               f'<circle cx="540" cy="325" r="18" fill="{RED}"/>'
               f'<circle cx="632" cy="325" r="18" fill="{RED}"/></g>',
    'monocle': f'<g fill="none" stroke="#111"><circle cx="632" cy="325" r="52" stroke-width="11"/>'
               f'<circle cx="632" cy="325" r="52" stroke="{GOLD}" stroke-width="5"/>'
               f'<path d="M676 356q30 60 10 118" stroke-width="6"/></g>',
    'patch':   f'<g {K}><path d="M498 296h84v58h-84z" fill="{DARK}"/>'
               f'<path d="M470 292 700 274" fill="none" stroke-width="10"/></g>',
    'dollar':  f'<g fill="none" stroke="#2f7a3f" stroke-width="11" stroke-linecap="round">'
               f'<path d="M556 306q-26-8-26 8t26 12 0 20-26-6M540 296v62"/>'
               f'<path d="M648 306q-26-8-26 8t26 12 0 20-26-6M632 296v62"/></g>',
    'x':       f'<g fill="none" stroke="#111" stroke-width="13" stroke-linecap="round">'
               f'<path d="M522 308l36 34M558 308l-36 34M614 308l36 34M650 308l-36 34"/></g>',
}

# ── MOUTHS ────────────────────────────────────────────────────────────────────────
MOUTH = {
    'signature': '',
    'gold':   f'<g fill="{GOLD}" stroke="#111" stroke-width="5">'
              f'<rect x="570" y="387" width="19" height="25" rx="3"/>'
              f'<rect x="593" y="385" width="18" height="24" rx="3"/></g>',
    'diamond': f'<g stroke="#111" stroke-width="5">'
               f'<path d="M570 387h19l-9 25z" fill="{ICE}"/>'
               f'<path d="M593 385h18l-9 24z" fill="#eaf9ff"/></g>'
               f'<g fill="#fff" stroke="none" opacity=".9">'
               f'<circle cx="576" cy="393" r="4"/><circle cx="599" cy="391" r="4"/></g>',
    'grill':  f'{COVER}<g {K}><path d="M528 384h120v34H528z" fill="{GOLD}"/></g>'
              f'<g stroke="#111" stroke-width="4" fill="none">'
              + ''.join(f'<path d="M{x} 384v34"/>' for x in (552, 576, 600, 624)) + '</g>',
    'duck':   f'{COVER}<g {K}><path d="M556 396q30-26 60 0-30 30-60 0z" fill="#d98f8f"/>'
              f'<path d="M586 380v-8" stroke-width="7"/></g>',
    'mad':    f'{COVER}<path d="M544 414q42-26 84 0" {LIP}/>'
              # angry brows, over the canonical relaxed ones
              f'<g fill="none" stroke="#111" stroke-width="13" stroke-linecap="round">'
              f'<path d="M500 268 566 292M672 268 606 292"/></g>',
    'cigar':  f'<g {K}><path d="M596 384h180v34H596z" fill="#6b4a2a"/>'
              f'<path d="M756 384h30v34h-30z" fill="{GOLD}"/></g>'
              f'<g fill="#c3c3c3" stroke="none" opacity=".75"><circle cx="812" cy="378" r="13"/>'
              f'<circle cx="842" cy="348" r="18"/><circle cx="878" cy="310" r="24"/></g>',
    'joint':  f'<g {K}><path d="M600 392 742 350l-8-26-142 42z" fill="{CREAM}"/>'
              f'<path d="M742 350l-10-26" fill="none" stroke="#8a5a2a" stroke-width="10"/></g>'
              f'<circle cx="748" cy="322" r="9" fill="{RED}"/>'
              f'<g fill="#c3c3c3" stroke="none" opacity=".7"><circle cx="782" cy="292" r="14"/>'
              f'<circle cx="816" cy="256" r="19"/><circle cx="856" cy="214" r="25"/></g>',
    'cig':    f'<g {K}><path d="M604 396h120v20H604z" fill="{CREAM}"/>'
              f'<path d="M704 396h20v20h-20z" fill="{GOLD}"/></g>'
              f'<g fill="#c3c3c3" stroke="none" opacity=".7"><circle cx="758" cy="386" r="11"/>'
              f'<circle cx="786" cy="360" r="15"/></g>',
    'tongue': f'<g {K}><path d="M552 404q34 74 76 0z" fill="#d76a7a"/></g>',
}

# ── NECK ──────────────────────────────────────────────────────────────────────────
def _chain(col, r, pend):
    """A chain drapes BELOW the chin and must finish above the caption band.
    ⚠️ Native y 470 is the beard's bottom edge and native y ~720 lands behind the band at
    screen 884, so the whole necklace has to live inside roughly y 460-630."""
    import math
    beads = ''.join(f'<circle cx="{586+int(140*math.sin(t*.19))}" '
                    f'cy="{430+int(140*math.cos(t*.19))}" r="{r}"/>' for t in range(-7, 8))
    return f'<g fill="{col}" stroke="#111" stroke-width="6">{beads}</g>{pend}'


NECK = {
    'none': '',
    'thug': _chain(GOLD, 16, f'<g {K}><path d="M558 578h56v54h-56z" fill="{GOLD}"/></g>'),
    'ice':  _chain(ICE, 14, f'<g stroke="#111" stroke-width="6">'
                            f'<path d="M586 570 622 604 586 646 550 604z" fill="#eaf9ff"/></g>'),
    # the ada pendant: ₳ — the A with the two bars
    'ada':  _chain(GOLD, 13, f'<g {K}><circle cx="586" cy="602" r="36" fill="{GOLD}"/></g>'
                             f'<g fill="none" stroke="#111" stroke-width="8" stroke-linecap="round">'
                             f'<path d="M570 622l16-42 16 42M566 606h40M562 615h48"/></g>'),
    'tie':  f'<g {K}><path d="M566 556h44l-12 30 24 82-34 34-34-34 24-82z" fill="{RED}"/></g>',
}

MARK = {
    'none': '',
    'teardrop': f'<path d="M516 366q-16 22 0 32t16-32z" fill="#2f6fd0" stroke="#111" stroke-width="5"/>',
    'teardrop2': f'<g fill="#2f6fd0" stroke="#111" stroke-width="5">'
                 f'<path d="M516 366q-16 22 0 32t16-32z"/><path d="M516 410q-16 22 0 32t16-32z"/></g>',
    'tattoo': f'<g fill="none" stroke="#3a4a6b" stroke-width="9" stroke-linecap="round">'
              f'<path d="M488 292v44M472 310h32"/>'
              f'<path d="M676 286 690 314 662 314z"/></g>',
    'star':  f'<path d="M482 300 492 322 516 324 498 340 504 364 482 351 460 364 466 340 448 324 472 322z"'
             f' fill="#3a4a6b" stroke="#111" stroke-width="4"/>',
    'scar':  f'<g fill="none" stroke="#b05a5a" stroke-width="8" stroke-linecap="round">'
             f'<path d="M492 268 508 372"/><path d="M478 292h30M482 330h30"/></g>',
    'sweat': f'<g fill="#8fd0ee" stroke="#111" stroke-width="5">'
             f'<path d="M700 250q-18 26 0 38t18-38z"/></g>',
}

# ── ACCESSORIES — exotic African birds, perched on the right shoulder ─────────────
# ⚠️ Small inset art must NOT inherit the scene stroke (width 9 turns a bird into a blob) —
# each bird carries its own stroke-width 6 group. Native coords: the shoulder slope passes
# ~(780, 560); feet plant just below it so the bird reads as standing on the shoulder.
PET = {
    'none': '',
    # grey crowned crane — the gold crest fan is the whole bird
    'crane': ('<g transform="translate(785 590) scale(1.3) translate(-785 -590)" '
              'stroke="#111" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
              '<path d="M772 592v-32M794 592v-34" fill="none"/>'
              '<path d="M814 518q28 4 24 32-18 0-30-14z" fill="#3d434e"/>'
              '<ellipse cx="782" cy="534" rx="40" ry="28" fill="#5a6270"/>'
              '<ellipse cx="766" cy="534" rx="15" ry="18" fill="#e9e7e3"/>'
              '<path d="M758 516q-12-22-8-50" fill="none" stroke-width="12"/>'
              '<path d="M758 516q-12-22-8-50" fill="none" stroke="#5a6270" stroke-width="6"/>'
              '<circle cx="748" cy="456" r="13" fill="#26262c"/>'
              '<circle cx="753" cy="459" r="5" fill="#e9e7e3" stroke-width="3"/>'
              '<path d="M736 454l-15 5 15 5z" fill="#26262c" stroke-width="3"/>'
              f'<path d="M744 472q4 9 10 8" fill="none" stroke="{RED}" stroke-width="5"/>'
              f'<g stroke="{GOLD}" stroke-width="4" fill="none">'
              '<path d="M748 444l-9-17M753 443l-2-19M758 444l5-18M762 447l12-14M744 448l-13-12"/>'
              '</g></g>'),
    # lilac-breasted roller — turquoise, lilac breast, streamer tail
    'roller': ('<g transform="translate(785 590) scale(1.3) translate(-785 -590)" '
              'stroke="#111" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
               '<path d="M778 588v-24M794 588v-26" fill="none"/>'
               '<path d="M810 540q20 30 6 52-14-6-20-24z" fill="#2e6db8" stroke-width="5"/>'
               '<ellipse cx="786" cy="538" rx="32" ry="25" fill="#49b8d4"/>'
               '<ellipse cx="768" cy="546" rx="15" ry="13" fill="#c79ad0"/>'
               '<circle cx="762" cy="514" r="14" fill="#d9c39a"/>'
               '<circle cx="757" cy="511" r="2.5" fill="#111" stroke="none"/>'
               '<path d="M750 516l-13 4 13 4z" fill="#26262c" stroke-width="3"/></g>'),
    # african grey parrot — grey, white eye patch, the red tail
    'grey': ('<g transform="translate(785 590) scale(1.3) translate(-785 -590)" '
              'stroke="#111" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
             '<path d="M778 590v-24M794 590v-26" fill="none"/>'
             f'<path d="M806 552q18 20 10 38-16-2-24-20z" fill="{RED}" stroke-width="5"/>'
             '<ellipse cx="784" cy="536" rx="34" ry="29" fill="#c3c3c3"/>'
             '<circle cx="764" cy="502" r="17" fill="#aeb0b4"/>'
             '<circle cx="758" cy="499" r="7" fill="#f2ece0" stroke-width="3"/>'
             '<circle cx="758" cy="499" r="2.5" fill="#111" stroke="none"/>'
             '<path d="M748 508q-11 1-9 12 9 3 13-4z" fill="#75757c" stroke-width="4"/></g>'),
    # greater flamingo — the S-neck is the silhouette
    'flamingo': ('<g transform="translate(785 590) scale(1.3) translate(-785 -590)" '
              'stroke="#111" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
                 '<path d="M790 592v-28M806 592v-30" fill="none"/>'
                 '<ellipse cx="800" cy="544" rx="36" ry="25" fill="#f0879e"/>'
                 '<path d="M778 534q-28-12-24-54 3-38 22-58" fill="none" stroke-width="15"/>'
                 '<path d="M778 534q-28-12-24-54 3-38 22-58" fill="none" '
                 'stroke="#f0879e" stroke-width="9"/>'
                 '<circle cx="778" cy="420" r="13" fill="#f0879e"/>'
                 '<path d="M768 424q-15 2-13 14l11 1z" fill="#26262c" stroke-width="3"/>'
                 '<circle cx="782" cy="416" r="2.5" fill="#111" stroke="none"/></g>'),
}

CATS = [('bg', BG), ('hat', HAT), ('eyes', EYES), ('mouth', MOUTH), ('neck', NECK),
        ('mark', MARK), ('pet', PET)]


def validate(t):
    t = t.upper().strip()
    if len(t) > MAX_TEXT:
        raise SystemExit(f'text is {len(t)} chars; the limit is {MAX_TEXT}')
    bad = [c for c in t if c not in OK_CHARS]
    if bad:
        raise SystemExit(f'no glyph for {"".join(sorted(set(bad)))!r} — '
                         f'allowed: A-Z 0-9 $ and space')
    return t


def _adv(c):
    return 12 if c == ' ' else ADV.get(c, 22)


def _width(s):
    """True advance width of a run. ⚠️ The scale MUST come from this, never from a per-char
    approximation: 22*(len-1)+16 disagrees with the real width whenever the string holds
    I, L or a space, and the divergence was invisible only while the 3.4 cap always bound
    (a <=10-char string never leaves the cap). The page JS uses the identical sum."""
    return sum(_adv(c) for c in s) - _adv(s[-1]) + 16


def _run(s, cx, y, sc, sw=8, col=CREAM):
    x, uses, need = 0, [], set()
    for c in s:
        if c != ' ':
            need.add(c); uses.append(f'<use href="#{GID.get(c, c)}" x="{x:g}"/>')
        x += _adv(c)
    w = _width(s)
    return ((f'<g transform="translate({R(cx-w*sc/2)} {R(y-28*sc)}) scale({sc:.4f})" fill="none" '
             f'stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
             f'stroke-linejoin="round">{"".join(uses)}</g>'), need)


def band_text(t):
    """Lay the caption into the band. One line while it reads big; below single-line scale
    2.0 it wraps to TWO balanced lines, split at the space that best equalises line width.
    No space to break at -> stays one line. Deterministic and mirrored byte-for-byte in the
    page JS — paritytest polices it."""
    sc1 = min(3.4, 880 / _width(t))
    lines = [t]
    if sc1 < 2.0 and ' ' in t:
        best, bw = None, None
        for i, c in enumerate(t):
            if c != ' ':
                continue
            a, b = t[:i].rstrip(), t[i + 1:].lstrip()
            if not a or not b:
                continue
            m = max(_width(a), _width(b))
            if bw is None or m < bw:
                best, bw = [a, b], m
        if best:
            lines = best
    if len(lines) == 1:
        sc, ys = sc1, [976]
    else:
        sc, ys = min(2.1, 880 / max(_width(l) for l in lines)), [944, 1010]
    runs, need = [], set()
    for l, y in zip(lines, ys):
        g, n = _run(l, 512, y, sc)
        runs.append(g); need |= n
    glyphs = ''.join(f'<path id="{GID.get(c, c)}" d="{ALL_GLY[c]}"/>' for c in sorted(need))
    return ''.join(runs), glyphs


def build(bg='byttg', hat='none', eyes='none', mouth='signature', neck='none',
          mark='none', pet='none', text=''):
    S = 1.42                                   # face-shot crop
    inner = (f'<g {K}><path d="M300 604q46-104 286-104t286 104v220H300z" fill="{SHIRT}"/></g>'
             f'{HEAD}{MARK[mark]}{MOUTH[mouth]}{EYES[eyes]}{HAT[hat]}{NECK[neck]}{PET[pet]}')
    face = f'<g transform="translate({R(512-586*S)} {R(456-325*S)}) scale({S})">{inner}</g>'
    band, glyphs = '', ''
    if text:
        t = validate(text)
        runs, glyphs = band_text(t)
        band = f'<rect x="0" y="884" width="1024" height="140" fill="{DARK}" opacity=".92"/>{runs}'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">'
           f'<defs>{HEAD_DEFS}{glyphs}</defs>{BG[bg]}{face}{band}</svg>')
    return re.sub(r'\n\s*', '', svg).strip()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    for k, _ in CATS:
        ap.add_argument(f'--{k}', default={'bg': 'byttg', 'mouth': 'signature'}.get(k, 'none'))
    ap.add_argument('--text', default='')
    ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--outdir', default=str(pathlib.Path.home() / 'tmp/pfp'))
    a = ap.parse_args()
    out = pathlib.Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    if a.sheet:
        SPREAD = [
            ('thuglife', dict(bg='smoke', eyes='thug', mouth='joint', neck='thug',
                              mark='teardrop', text='THUG LIFE')),
            ('iced',     dict(bg='ivyom', hat='crown', eyes='shades', mouth='diamond',
                              neck='ice', text='ALL YOUR MONEY')),
            ('goldteeth',dict(bg='dnpg', hat='durag', mouth='gold', neck='ada', mark='tattoo')),
            ('mad',      dict(bg='byttg', hat='band', mouth='mad', mark='scar', text='NO DOORS LEFT')),
            ('duck',     dict(bg='hotel', hat='cap', mouth='duck', mark='sweat', text='TRUST ME')),
            ('cigar',    dict(bg='org', hat='top', eyes='monocle', mouth='cigar', neck='tie')),
            ('laser',    dict(bg='tgm', hat='horns', eyes='laser', mouth='grill', neck='thug')),
            ('locked',   dict(bg='bars', eyes='x', mouth='cig', mark='teardrop2', text='I VOTE YES')),
            ('saint',    dict(bg='ndl', hat='halo', eyes='dollar', mouth='tongue', mark='star')),
        ]
        print(f'  {"variant":<11}{"svg":>8}   {"tx":>9}   cap')
        files = []
        for name, kw in SPREAD:
            s = build(**kw)
            f = out / f'{name}.svg'; f.write_text(s); files.append(str(f))
            n = len(s.encode()); tx = 754 + 1.3668 * n + 900
            print(f'  {name:<11}{n:>7,} B  {tx:>8,.0f} B  {tx/16384*100:4.1f}%')
        subprocess.run(['node', str(pathlib.Path.home() / 'Desktop/2026-07-28_byttg-mint/shot.mjs'),
                        str(out), '360'] + files, check=True)
        pngs = [str(out / f'{n}.png') for n, _ in SPREAD]
        subprocess.run(['montage'] + pngs + ['-tile', '3x3', '-geometry', '+6+6',
                        '-background', '#101012', str(out / 'sheet.png')], check=True)
        print(f'\n  sheet -> {out / "sheet.png"}')
        tot = 1
        for _, d in CATS:
            tot *= len(d)
        print(f'  catalogue: ' + ' x '.join(f'{len(d)} {k}' for k, d in CATS)
              + f' = {tot:,} combinations, before text')
    else:
        s = build(a.bg, a.hat, a.eyes, a.mouth, a.neck, a.mark, a.text)
        (out / 'pfp.svg').write_text(s)
        print(f'  pfp.svg  {len(s.encode()):,} B')

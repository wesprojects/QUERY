#!/usr/bin/env python3
"""Catalog corrections from the review of 2026-09-27, each read from the June 2022 page named beside it (values double-checked against the page
images). Runs last in the catalog chain: update_catalog_2022.py, update_options_2022.py, add_rows_2022.py, hand_rows_2022.py,
new_products_2022.py, then this script. Idempotent: running it twice gives the same catalog.

  1. Banded options (priceBy): update_options_2022.py re-prices plain option prices only, so the bands kept their 2015 values.
  2. Option prices read from the wrong table or zeroed: mobile pedestal cushion tops, c:scape L junction paint groups; options the 2022 page no
     longer prints (top cap aligner packages); stale unpriced2022 marks on options printed "No cost".
  3. TS748SVPJW / TS748VPJ: the 2015 misprint note no longer applies (2022 p436, p437 print them correctly).
  4. Pages: T and X change-of-height rows and the oval stacking junctions cite their 2022 pages; 2015 page numbers left in tips.
  5. Big open base (p58-p60, p392-p393, p474, p480) and Answer boundary screens (p408-p426): missing options, charges and corrected tips.
  6. Rows the pattern matcher reported for hand entry and never entered: reinforcing channels (p589, sizes p217) and the steel-skin power access
     parts TS7RC (p525), TS7USB (p526), TS7RCT, TSBRF, TS7DF (p527).
  7. Smaller data: TS7CNTSTKR not in the 2022 guide, grommet colours (p727), Open Line fee $94 (p725), table column headings, price texts.
"""
import json, os, re, glob
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'src', 'catalog.json')
cat = json.load(open(OUT, encoding='utf-8')); P = {p['id']: p for p in cat['products']}
G22 = {int(re.search(r'p(\d+)\.txt$', f).group(1)): open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(ROOT, 'guide2022', 'p*.txt'))}
log = []

def prod(pid):
    assert pid in P, pid
    return P[pid]
def opt(pid, code):
    o = [x for x in prod(pid).get('options', []) if x.get('code') == code]
    assert len(o) >= 1, (pid, code)
    return o[0]
def set_opt(pid, code, **kw):
    o = opt(pid, code)
    for k, v in kw.items(): o[k] = v
    o.pop('unpriced2022', None)
def add_opt(pid, o, after=None):
    p = prod(pid); ops = p.setdefault('options', [])
    ops[:] = [x for x in ops if x.get('code') != o['code']]
    o['added2022'] = True
    ops.append(o)
def drop_opt(pid, code):
    p = prod(pid); n = len(p.get('options', [])); p['options'] = [x for x in p['options'] if x.get('code') != code]
    if len(p['options']) != n: log.append(f'{pid}: dropped option {code}')
def upsert_row(pid, row):
    p = prod(pid); p['rows'] = [r for r in p['rows'] if r['style'] != row['style']]; row['added2022'] = True; p['rows'].append(row)
    if row.get('page') and row['page'] not in p['pages']: p['pages'] = sorted(p['pages'] + [row['page']])
def put_product(pr):
    pr['added2022'] = True
    cat['products'][:] = [x for x in cat['products'] if x['id'] != pr['id']] + [pr]; P[pr['id']] = pr
def tips_replace(pid, old, new):
    p = prod(pid); tips = p.get('tips', []); hit = [i for i, t in enumerate(tips) if old in t]
    for i in hit: tips[i] = tips[i].replace(old, new)
    return len(hit)
def printed_on(style, pages):
    for pg in pages:
        if re.search(r'(?<![A-Z0-9])' + re.escape(style) + r'(?![A-Z0-9])', G22.get(pg, '')): return pg
    return None

# ---------- 1. banded options (2022 values; keys unchanged) ----------
BANDS = {
    ('thin-panel-package', 'woodTopCap'): ({'18W-48W': 254, '60W-72W': 335}, 406, 'Wood group 1'),
    ('thin-panel-package', 'passThroughHarness'): ({'18W-48W': 222, '60W-72W': 248}, 406, None),
    ('thin-panel-package', 'powerkit'): ({'24W-48W': 275, '60W-72W': 415}, 406, None),
    ('square-panel-package', 'woodTopCap'): ({'18W-48W': 254, '60W-72W': 335}, 464, 'Wood group 1'),
    ('square-panel-package', 'passThroughHarness'): ({'18W-48W': 222, '60W-72W': 248}, 465, None),
    ('square-panel-package', 'powerkit'): ({'24W-48W': 275, '60W-72W': 415}, 465, None),
    ('oval-panel-package', 'woodTopCap'): ({'18W-48W': 254, '60W-72W': 337}, 466, 'Wood group 1'),  # p466 prints +$337 (thin and square +$335): as printed
    ('oval-panel-package', 'passThroughHarness'): ({'18W-48W': 222, '60W-72W': 248}, 466, None),
    ('oval-panel-package', 'powerkit'): ({'24W-48W': 275, '60W-72W': 415}, 466, None),
    ('sh-fabric-skins', 'fabricGroup2'): ({'12H,18H': 19, '24H,30H': 29, '36H-60H': 36}, 470, None),
    ('sh-fabric-skins', 'fabricGroup3'): ({'12H,18H': 36, '24H,30H': 50, '36H-60H': 66}, 470, None),
    ('sh-fabric-skins', 'fabricGroup4'): ({'12H,18H': 52, '24H,30H': 74, '36H-60H': 103}, 470, None),
    ('sh-fabric-skins', 'fabricGroup5'): ({'12H,18H': 80, '24H,30H': 118, '36H-60H': 160}, 470, None),
    ('sh-fabric-skins', 'fabricGroup6'): ({'12H,18H': 110, '24H,30H': 158, '36H-60H': 220}, 470, None),
    ('sh-fabric-skins', 'fabricGroup7'): ({'12H,18H': 142, '24H,30H': 203, '36H-60H': 279}, 470, None),
    ('sh-fabric-skins', 'fabricGroupCOM'): ({'12H,18H': 21, '24H,30H': 21, '36H-60H': 21}, 470, None),
    ('sh-fabric-skins-to-floor', 'fabricGroup2'): ({'24H,30H': 29, '36H-60H': 36}, 472, None),
    ('sh-fabric-skins-to-floor', 'fabricGroup3'): ({'24H,30H': 50, '36H-60H': 66}, 472, None),
    ('sh-fabric-skins-to-floor', 'fabricGroup4'): ({'24H,30H': 74, '36H-60H': 103}, 472, None),
    ('sh-fabric-skins-to-floor', 'fabricGroup5'): ({'24H,30H': 118, '36H-60H': 160}, 472, None),
    ('sh-fabric-skins-to-floor', 'fabricGroup6'): ({'24H,30H': 158, '36H-60H': 220}, 472, None),
    ('sh-fabric-skins-to-floor', 'fabricGroup7'): ({'24H,30H': 203, '36H-60H': 279}, 472, None),
    ('sh-fabric-skins-to-floor', 'fabricGroupCOM'): ({'24H,30H': 21, '36H-60H': 21}, 472, None),
    ('sh-steel-skins', 'paintGroup2'): ({'12H-24H': 32, '30H': 32, '36H': 63}, 476, None),
    ('sh-steel-skins', 'paintGroup3'): ({'12H-24H': 54, '30H': 54, '36H': 105}, 476, None),
    ('sh-steel-skins', 'ribbedSteel'): ({'12H-24H': 30, '30H': None, '36H': None}, 476, None),  # N.A. on 30"H and 36"H
    ('sh-steel-skins-to-floor', 'paintGroup2'): ({'24H-30H': 32, '36H': 63}, 478, None),
    ('sh-steel-skins-to-floor', 'paintGroup3'): ({'24H-30H': 54, '36H': 105}, 478, None),
}
for jp in ('square-l-t-x-base-junction', 'oval-l-t-x-base-junction', 'square-end-of-run-base-junction', 'oval-end-of-run-base-junction', 'square-v-y-base-junction', 'oval-v-y-base-junction'):
    BANDS[(jp, 'woodTrim')] = ({'30H-54H': 266, '66H-78H': 339}, {'square-l-t-x-base-junction': 432, 'oval-l-t-x-base-junction': 433, 'square-end-of-run-base-junction': 434,
                               'oval-end-of-run-base-junction': 435, 'square-v-y-base-junction': 436, 'oval-v-y-base-junction': 437}[jp], 'Wood group 1 on junctions with wood junction cap')
for (pid, code), (bands, page, name) in BANDS.items():
    o = opt(pid, code); assert set(o['priceBy']) == set(bands), (pid, code, o['priceBy'], bands)
    if 'priceBy2015' not in o: o['priceBy2015'] = dict(o['priceBy'])
    o['priceBy'] = dict(bands); o['page2022'] = page; o.pop('unpriced2022', None)
    if name: o['name'] = name
log.append(f'{len(BANDS)} banded options re-priced from the 2022 pages')
# options printed "No cost" in 2022 that still carried unpriced2022 (p432-p437, p464, p466)
n = 0
for pid in ('square-l-t-x-base-junction', 'oval-l-t-x-base-junction', 'square-end-of-run-base-junction', 'oval-end-of-run-base-junction', 'square-v-y-base-junction', 'oval-v-y-base-junction'):
    for code in ('fabricHorizontal', 'fabricVertical'):
        o = [x for x in prod(pid)['options'] if x.get('code') == code]
        for x in o:
            if x.pop('unpriced2022', None): n += 1
for pid in ('square-panel-package', 'oval-panel-package'):
    for x in prod(pid)['options']:
        if x.get('code') == 'knockoutsOneSidePlainOneSide' and x.pop('unpriced2022', None): n += 1
log.append(f'{n} stale unpriced2022 marks removed (options printed "No cost")')

# ---------- 2. options read from the wrong table, zeroed, or no longer printed ----------
set_opt('us-mobile-pedestals', 'cushionTop', price=499, page2022=655)            # p655 "Cushion top without handle +$499" (the $443 was the p656 field kit)
set_opt('us-mobile-pedestals', 'cushionTopHandle', price=628, page2022=655)      # p655 "Cushion top with black handle +$628"
set_opt('thin-cscape-l-junction', 'paintGroup2', price=15, price2015=11, page2022=389)  # p389 +$15 (2015 p376 +$11)
set_opt('thin-cscape-l-junction', 'paintGroup3', price=31, price2015=21, page2022=389)  # p389 +$31 (2015 p376 +$21)
AL = 'thin-top-cap-mount-storage-top-cap-aligner-packages'                          # p405: paint groups 1-3 only; wood is the TS7xxTTCWR rows
drop_opt(AL, 'wood'); drop_opt(AL, 'customizStain')
prod(AL)['detailsPages'] = [74]
prod(AL)['standardIncludes'] = [s.replace('paint or wood', 'paint or wood group 1').replace('group 1 group 1', 'group 1').replace('Two inline aligners', 'Two in-line aligners') for s in prod(AL).get('standardIncludes', [])]
prod(AL)['requiredToSpecify'] = [s.replace('page 708', 'page 724') for s in prod(AL).get('requiredToSpecify', [])]

# ---------- 3. TS748SVPJW / TS748VPJ: printed correctly in 2022 ----------
for pid, style, pr15, printed, pg15 in (('square-v-y-base-junction', 'TS748SVPJW', 305, 'TS742SVPJW', 400), ('oval-v-y-base-junction', 'TS748VPJ', 302, 'TS742VPJ', 401)):
    r = [x for x in prod(pid)['rows'] if x['style'] == style]; assert len(r) == 1, style; r = r[0]
    r.pop('correction', None); r.pop('printedStyle', None); r['price2015'] = pr15
    r['note2015'] = f'The February 2015 guide printed {printed} in the 48" row (2015 p{pg15}); the June 2022 guide prints {style} (p{436 if "SVPJW" in style else 437}).'

# ---------- 4. pages ----------
# T and X change-of-height rows: their 2015 page sat in attrs.page and in the configuration text; cite the 2022 page that prints the style
pmap = {}
for pid, pages in (('thin-t-change-of-height-junction', range(357, 372)), ('thin-x-change-of-height-junction', range(357, 372))):
    for r in prod(pid)['rows']:
        pg = printed_on(r['style'], pages); assert pg, r['style']
        old = r.get('attrs', {}).get('page')
        m = re.search(r'\(page (\d+)', r['attrs'].get('configuration', ''))
        if m: pmap.setdefault(pid, {})[int(m.group(1))] = pg; r['attrs']['configuration'] = re.sub(r'\(page \d+', f'(p{pg}', r['attrs']['configuration'])
        if old and old != pg and not r.get('added2022'): r['attrs']['page2015'] = old  # rows added from the 2022 pages had no 2015 page (add_rows copied a sibling's)
        if r.get('added2022'): r['attrs'].pop('page2015', None)
        r['attrs']['page'] = pg; r['page'] = pg
        # three tall legs: the engine reads 'A, B and C tall' (add_rows_2022.py once wrote 'A and B and C')
        r['attrs']['configuration'] = r['attrs']['configuration'].replace('A and B and C', 'A, B and C')
    for old, new in sorted(pmap.get(pid, {}).items()):
        tips_replace(pid, f'(p{old}', f'(p{new}')
    prod(pid)['pages'] = sorted({r['page'] for r in prod(pid)['rows']})
log.append(f'T/X change-of-height pages 2015 -> 2022: {pmap}')
# oval stacking junctions: the square/oval pages first (p441-p444); the thin page p376 is where the shared in-line and X/Y styles also appear
for pid in ('so-stacking-inline-junction', 'so-stacking-l-t-x-junction', 'so-stacking-end-of-run-junction', 'so-stacking-v-y-junction'):
    if pid not in P: continue
    for r in prod(pid)['rows']:
        pg = printed_on(r['style'], range(441, 446))
        if pg: r['page'] = pg
    prod(pid)['pages'] = sorted({r['page'] for r in prod(pid)['rows'] if r.get('page')} or set(prod(pid)['pages']))
# 2015 page numbers left in tips (2015 -> 2022: fabric direction 713 -> 730, skins 434 -> 470, junctions 344-348 -> 352, lightseal p404 -> p513)
n = 0
for p in cat['products']:
    tips = p.get('tips', [])
    for i, t in enumerate(tips):
        t2 = t.replace('see page 713', 'see page 730').replace('See page 713', 'See page 730').replace('See page 434', 'See page 470').replace('Page 434', 'Page 470').replace('See pages 344-348', 'See page 352')
        if p['id'] == 'thin-top-cap-screens': t2 = t2.replace('p404', 'p513')
        if t2 != t: tips[i] = t2; n += 1
log.append(f'{n} tips re-cited to 2022 pages')

# ---------- 5. big open base ----------
FR = 'thin-base-horizontal-frame-package'
add_opt(FR, {'group': 'Big Open Base', 'name': 'Big open base', 'code': 'bigOpenBase', 'price': 90, 'spec': 'Specify with big open base.', 'page2022': 392})
prod(FR)['pages'] = [392, 393]; prod(FR)['detailsPages'] = [58, 59, 60]
prod(FR)['requiredToSpecify'] = [s.replace('page 708', 'page 724') for s in prod(FR).get('requiredToSpecify', [])]
tips = prod(FR).get('tips', [])
tips[:] = [('When open base trim or big open base option is selected, both base trims are omitted.' if t.startswith('When open base trim option is selected') else
            'Base cable tray cannot be used if open base or big open base is selected, or if omit base trim is selected for one or both sides of panel.' if t.startswith('Base cable tray cannot be used') else t) for t in tips]
for t in ('Big open base option includes vertical trim (p58): two inside vertical trims in addition to the two horizontal connecting bars and the thin trim top cap (p59).',
          'When the big open base option is specified, big open base skins must be used (p59).', 'When big open base is used, power is available only at 20"H or higher (p59).'):
    if t not in tips: tips.append(t)
BT = 'thin-big-open-base-trim'
prod(BT)['tips'] = ['The big open base trim package is available for reconfiguring a panel segment to the big open base; it includes two inside vertical trims (p59). For a new panel, select the big open base option on the base horizontal frame package, which includes the two inside vertical trims (p58, p59, p392).']
prod(BT)['detailsPages'] = [58, 59]
if 'See Surface Materials, page 724.' not in prod(BT)['requiredToSpecify']: prod(BT)['requiredToSpecify'].append('See Surface Materials, page 724.')
BOB_TIP = 'Select the big open base option on horizontal frames that are receiving big open base height skins (p125, p127). The big open base trim package TSBBOBTRM is for reconfiguring an existing panel segment (p59).'
SIZE_TIP = 'Big open base skins are sized to finish a 30"H panel. On panels taller than 30"H, standard skins finish the remaining height: a 42"H panel with big open base takes a big open base skin and a 12"H skin on each side (p125, p127).'
FB = 'sh-fabric-skins-big-open-base'
add_opt(FB, {'group': 'Surface Materials', 'name': 'Fabric price group COM', 'code': 'fabricGroupCOM', 'price': 21, 'spec': 'Specify fabric color number.', 'page2022': 474})
add_opt(FB, {'group': 'Fabric direction on 18"W to 60"W panels', 'name': 'Vertical application', 'code': 'fabricVertical', 'price': 0, 'widths': [18, 24, 30, 36, 42, 48, 60], 'spec': 'Specify with vertical application.', 'page2022': 474})
prod(FB)['tips'] = [prod(FB)['tips'][0], SIZE_TIP, BOB_TIP, 'Big open base skins must be used on both sides of a panel (p125).', 'Performance tackable skins are not available in big open base sizes (p125).', '72"W fabric-covered panel skins accommodate fabric in the horizontal direction only; for fabric direction see page 730 (p474).']
prod(FB)['detailsPages'] = [124, 125]; prod(FB)['standardIncludes'] = ['19 3/16"H tackable acoustical panel skin, fabric direction with horizontal application, if selected: fabric price group 1']
prod(FB)['requiredToSpecify'] = ['Style number', 'Color number for skin surface', 'Options, if selected', 'See Surface Materials, page 724.']
SB = 'sh-steel-skins-big-open-base'
CUT = [('Data Cutout Only', 'Left modular furniture data cutout or left NEMA data cutout', 'dataLeft', (None, None, 11)),
       ('Data Cutout Only', 'Right modular furniture data cutout or right NEMA data cutout', 'dataRight', (11, 11, 11)),
       ('Modular Receptacle Cutout', 'Center receptacle cutout', 'rcCenter', (11, None, None)),
       ('Modular Receptacle Cutout', 'Center receptacle cutout with right modular furniture data cutout or right NEMA data cutout', 'rcCenterDataRight', (22, None, None)),
       ('Modular Receptacle Cutout', 'Left receptacle cutout', 'rcLeft', (None, 11, 11)),
       ('Modular Receptacle Cutout', 'Left receptacle cutout with left modular furniture data cutout or left NEMA data cutout', 'rcLeftDataLeft', (None, None, 22)),
       ('Modular Receptacle Cutout', 'Right receptacle cutout', 'rcRight', (None, 11, 11)),
       ('Modular Receptacle Cutout', 'Right receptacle cutout with right modular furniture data cutout or right NEMA data cutout', 'rcRightDataRight', (None, 22, 22)),
       ('Modular Receptacle Cutout', 'Left and right receptacle cutout', 'rcLeftRight', (None, 22, 22)),
       ('Modular Receptacle Cutout', 'Left and right receptacle cutout with left modular furniture data cutout or left NEMA data cutout', 'rcLeftRightDataLeft', (None, None, 33)),
       ('Modular Receptacle Cutout', 'Left and right receptacle cutout with right modular furniture data cutout or right NEMA data cutout', 'rcLeftRightDataRight', (None, 33, 33))]
for grp, name, code, (a, b, c) in CUT:  # p480: bands 24"W-30"W / 36"W / 42"W-72"W, N.A. = null; none on 18"W
    add_opt(SB, {'group': grp, 'name': name, 'code': code, 'price': None, 'priceBy': {'24W-30W': a, '36W': b, '42W-72W': c}, 'spec': f'Specify with {name[0].lower() + name[1:]}.', 'page2022': 480})
prod(SB)['tips'] = [prod(SB)['tips'][0], SIZE_TIP, BOB_TIP,
    'Data cutouts: the right data cutout is +$11 on 24"W to 72"W skins and the left data cutout +$11 on 42"W to 72"W skins; a skin takes a data cutout on the left or the right, not both. No data or modular receptacle cutouts on 18"W skins (p480).',
    'Big open base skins must be used on both sides of a panel (p127). Ribbed and perforated steel are not available on big open base skins (p119).',
    'Steel skins with power and data cutouts provide power access at 20"H; specify TS7RC receptacles (or TS7USB USB receptacles) and a TS7RCT trim ring for each cutout (p127, p193, p525-p527).']
prod(SB)['detailsPages'] = [126, 127]; prod(SB)['standardIncludes'] = ['19 3/16"H steel panel skin: paint price group 1']
prod(SB)['requiredToSpecify'] = ['Style number', 'Paint color number for skin surface', 'Options, if selected', 'See Surface Materials, page 724.']

# ---------- 5b. Answer boundary screens (p408-p426) ----------
BS = 'thin-boundary-screens'
drop_opt(BS, 'splitHardware')
for name, price, style, page in (('Single-connect straight split', 27, 'TS7SCSPT', 408), ('Dual-connect straight split', 27, 'TS7DCSPT', 412),
                                 ('Single-connect single-sided L return', 53, 'TS7SCLSSD', 416), ('Single-connect split L return', 79, 'TS7SCLSPT', 416),
                                 ('Dual-connect single-sided L return', 53, 'TS7DCLSSD', 422), ('Dual-connect split L return', 79, 'TS7DCLSPT', 422)):
    add_opt(BS, {'group': 'Required Component — Additional Hardware', 'name': name, 'code': 'hw' + style[3:], 'price': price, 'appliesTo': [style], 'required': True,
                 'spec': f'Charged with every {style} screen.', 'page2022': page})
for grp, name, code, price, spec, page in (
        ('Surface Materials', 'Laminate price group 2', 'laminateGroup2', None, 'Specify laminate color number.', 408),
        ('Surface Materials', 'Laminate price group 3', 'laminateGroup3', None, 'Specify laminate color number.', 408),
        ('Surface Materials', 'Customiz stain', 'customizStain', 0, 'Specify with Customiz stain.', 408),
        ('Surface Materials', 'Full-fill finish on wood group 1', 'fullFillWood1', 0, 'Specify full-fill finish number.', 408),
        ('Laminate grain direction', 'No direction', 'lamGrainNone', 0, 'Specify with no direction.', 408),
        ('Laminate grain direction', 'Horizontal', 'lamGrainH', 0, 'Specify with horizontal.', 408),
        ('Laminate grain direction', 'Vertical', 'lamGrainV', 0, 'Specify with vertical.', 408),
        ('Wood veneer grain direction', 'No direction', 'woodGrainNone', 0, 'Specify with no direction.', 409),
        ('Wood veneer grain direction', 'Horizontal', 'woodGrainH', 0, 'Specify with horizontal.', 409),
        ('Wood veneer grain direction', 'Vertical', 'woodGrainV', 0, 'Specify with vertical.', 409),
        ('Screen Size Type', 'Modular', 'sizeModular', 0, 'Specify with modular.', 408),
        ('Screen Size Type', 'Parametric', 'sizeParametric', 0, 'Specify with parametric.', 408),
        ('Handedness (Single-Sided Screens Only)', 'Right handed', 'handRight', 0, 'Specify with single-sided right.', 408),
        ('Handedness (Single-Sided Screens Only)', 'Left handed', 'handLeft', 0, 'Specify with single-sided left.', 408)):
    o = {'group': grp, 'name': name, 'code': code, 'price': price, 'spec': spec, 'page2022': page}
    if price is None: o['priceText'] = 'See the electronic catalog or SmartTools (p408)'
    add_opt(BS, o)
for h in (30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90):
    add_opt(BS, {'group': 'Height of Connecting Panel', 'name': f'{h}"H', 'code': f'connH{h}', 'price': 0, 'spec': f'Specify with {h}"H.', 'page2022': 408})
prod(BS)['requiredToSpecify'] = ['Style number', 'Screen size type', 'Screen height(s)', 'Height of connecting panel', 'Screen width(s)', 'Handedness: on single-sided screens, if selected',
    'High-Pressure Laminate or wood veneer color for screen', 'Plastic color number for edge on laminate screen, if selected', 'Grain direction', 'Paint color number for connecting panel cover',
    'Options, if selected', 'See Surface Materials, page 724.']
prod(BS)['standardIncludes'] = [s.replace('Edge on laminate screen: plastic', 'Edge on laminate screen, if selected: plastic') for s in prod(BS).get('standardIncludes', [])]
t = 'Split, L return and split L return screens carry a required additional hardware charge with their style number: +$27 straight split, +$53 single-sided L return, +$79 split L return, single- or dual-connect alike (p408, p412, p416, p422).'
if t not in prod(BS).setdefault('tips', []): prod(BS)['tips'].append(t)

# ---------- 6. rows never entered ----------
RC = 'uw-reinforcing-channels'   # p589 nine sizes, all $70; actual lengths p217. TS7WKSPT (no suffix) is the 57"W channel.
ACT = {39: 39.231, 48: 47.547, 51: 50.547, 54: 53.547, 57: 56.547, 60: 59.547, 63: 62.547, 66: 65.547, 72: 71.547}
for r in prod(RC)['rows']:
    r['attrs']['actualWidth'] = ACT[r['attrs']['width']]; r['page2015'] = 546
for w in (48, 51, 54, 60, 63, 66):
    upsert_row(RC, {'attrs': {'width': w, 'actualWidth': ACT[w], 'forWorksurfaceWidths': []}, 'style': f'TS7WKSPT{w}', 'price': 70, 'page': 589})
prod(RC)['rows'].sort(key=lambda r: r['attrs']['width']); prod(RC)['detailsPages'] = [216, 217]
for t in ('The guide sizes channels two ways: p217 by the span less a support deduction (nine sizes, choose the smaller when between sizes), and p224/p246 for knife-edge worksurfaces (TS7WKSPT39 for 54"W, TS7WKSPT for 60"W and 66"W, TS7WKSPT72 for 72"W). The engine uses the p224/p246 pairing (forWorksurfaceWidths) until the owner decides.',
          'Reinforcing channels add 1"D below the worksurface; place the channel in the middle of the worksurface span (p216).'):
    if t not in prod(RC).setdefault('tips', []): prod(RC)['tips'].append(t)
SCHEM = [('Wiring Schematic', n, 'schematic' + c, 0, f'Specify with {n}.') for n, c in (('3+1', '3plus1'), ('2+2', '2plus2'), ('3SN', '3SN'))]
LINES = [('Line', f'Line {i}' + (' (Available in 3+1 and 2+2 only)' if i == 4 else ''), f'line{i}', 0, f'Specify with line {i}.') for i in (1, 2, 3, 4)]
COLORS = [('Plastic Color', f'{c} {n}', 'color' + c, 0, f'Specify plastic color number {c}.') for c, n in (('6000', 'Black'), ('6009', 'Arctic White'), ('6249', 'Platinum Solid'), ('6651', 'Tungsten'), ('6652', 'Titanium'), ('6654', 'Sand'), ('6697', 'Fog'), ('6B03', 'Red'))]
mk = lambda rows: [{'group': g, 'name': n, 'code': c, 'price': p, 'spec': s} for g, n, c, p, s in rows]
put_product({'id': 'wc-steel-skin-receptacle', 'trim': 'shared', 'category': 'Power', 'name': 'Receptacles—For Use with Power Cutouts in Steel Skins', 'pages': [525], 'detailsPages': [193],
    'standardIncludes': ['Receptacle: plastic'], 'requiredToSpecify': ['Style number', 'Plastic color number for receptacle', 'Wiring schematic', 'Line', 'Ground type', 'Amp type', 'Options, if selected'],
    'options': mk(SCHEM + LINES + [('Ground Type', 'System ground', 'groundSystem', 0, 'Specify with system ground.'), ('Ground Type', 'Isolated ground', 'groundIsolated', 0, 'Specify with isolated ground.'),
                                   ('Amp Type', '15 amp', 'amp15', 0, 'Specify with 15 amp.'), ('Amp Type', '20 amp', 'amp20', 32, 'Specify with 20 amp.'),
                                   ('Options', 'No stamp', 'noStamp', 0, 'Specify with no stamp.'), ('Options', 'Controlled stamp', 'controlledStamp', 5, 'Specify with controlled stamp.')] + COLORS),
    'tips': ['Specify one receptacle and one TS7RCT receptacle trim ring for each power cutout in a steel skin (p193, p527).'], 'columns': ['Style Number', 'U.S. Base Price'],
    'rows': [{'attrs': {'description': 'Receptacle for use with power cutouts in steel skins'}, 'style': 'TS7RC', 'price': 58, 'page': 525, 'added2022': True}]})
put_product({'id': 'wc-steel-skin-usb-receptacle', 'trim': 'shared', 'category': 'Power', 'name': 'USB Receptacles—For Use with Power Cutouts in Steel Skins', 'pages': [526], 'detailsPages': [193],
    'standardIncludes': ['USB receptacle: plastic'], 'requiredToSpecify': ['Style number', 'Plastic color number for receptacle', 'Wiring schematic', 'Line', 'See Surface Materials, page 724.'],
    'options': mk(SCHEM + LINES + COLORS), 'columns': ['Style Number', 'U.S. Price'],
    'tips': ['Specify when using steel skins with power cutouts (p526).', 'For power access in steel skins with power cutouts, a receptacle trim ring is required for each power cutout location specified, ordered separately (p526).'],
    'rows': [{'attrs': {'description': 'USB receptacle for use with power cutouts in steel skins'}, 'style': 'TS7USB', 'price': 138, 'page': 526, 'added2022': True}]})
put_product({'id': 'wc-steel-skin-trim-rings-fillers', 'trim': 'shared', 'category': 'Power', 'name': 'Receptacle Trim Ring and Fillers—Steel Skins', 'pages': [527], 'detailsPages': [193],
    'standardIncludes': ['Receptacle trim ring: plastic'], 'requiredToSpecify': ['Style number', 'Plastic color number'], 'options': mk(COLORS), 'columns': ['Style Number', 'U.S. Price'],
    'tips': ['One TS7RCT trim ring for each power cutout location in a steel skin (p526, p527).'],
    'rows': [{'attrs': {'description': 'Receptacle trim ring'}, 'style': 'TS7RCT', 'price': 15, 'page': 527, 'added2022': True},
             {'attrs': {'description': 'Package of 20 receptacle fillers', 'count': 20}, 'style': 'TSBRF', 'price': 125, 'page': 527, 'added2022': True},
             {'attrs': {'description': 'Package of 20 data fillers', 'count': 20}, 'style': 'TS7DF', 'price': 103, 'page': 527, 'added2022': True}]})
if 'wc-duplex-receptacle' in P:
    add_opt('wc-duplex-receptacle', {'group': 'Controlled Stamp', 'name': 'Controlled stamp', 'code': 'controlledStamp', 'price': 5, 'spec': 'Specify with controlled stamp.', 'page2022': 523})
for pid in ('wc-duplex-receptacle', 'wc-usb-receptacle', 'wc-faceplate'):
    if pid in P: prod(pid)['detailsPages'] = [193]

# ---------- 7. smaller data ----------
CN = 'wc-controlled-receptacle-stickers'   # TS7CNTSTKR: printed on 2015 p488 only; 2022 offers a factory "Controlled stamp" (+$5, p523, p525) instead
for r in prod(CN)['rows']:
    if r['style'] == 'TS7CNTSTKR': r['discontinued2022'] = True; r['unpriced2022'] = True; r['price2015'] = 38; r['page2015'] = 488
prod(CN)['pages'] = []
t = 'Not in the June 2022 guide. The 2022 guide offers a factory "Controlled stamp" option (+$5) on duplex receptacles instead (p193, p523, p525).'
if t not in prod(CN).setdefault('tips', []): prod(CN)['tips'].append(t)
GR = 'wc-series-9000-duplex-cable-grommets'  # p536 (98863 $44), colours on Surface Materials p727; E = Established
prod(GR)['name'] = 'Duplex Cable Grommets'; prod(GR)['detailsPages'] = [196]
prod(GR)['options'] = [x for x in prod(GR)['options'] if not x.get('code', '').startswith('color')] + mk([('Plastic Color', f'{c} {n}', 'color' + c, 0, f'Specify plastic color number {c}.')
    for c, n in (('6000', 'Black'), ('6009', 'Arctic White'), ('6249', 'Platinum Solid'), ('6607', 'Woodrose'), ('6608', 'Driftwood'), ('6609', 'Smoke'), ('6612', 'Grey V2 (Established)'), ('6655', 'Warm White'), ('6697', 'Fog'))])
for p in cat['products']:
    for o in p.get('options', []):
        for k in ('note', 'verify'):
            if isinstance(o.get(k), str) and '6612' in o[k]: o.pop(k)
def fix_surface(x):
    if isinstance(x, dict): return {k: fix_surface(v) for k, v in x.items()}
    if isinstance(x, list): return [fix_surface(v) for v in x]
    if isinstance(x, str) and '$65 U.S. processing fee' in x: return x.replace('$65 U.S. processing fee', '$94 U.S. processing fee').rstrip('.') + ' (p725).'
    return x
cat['surface'] = fix_surface(cat['surface'])
# table headings the 2022 pages print (p539 knife edge in the cord-drop table; p651/p656 proud laminate fronts)
cols = prod('uw-straight')['columns']
if 'Plastic Knife Edge (Suffix K)' not in cols[:cols.index('|| Full Depth: Dimensions A')]: cols.insert(cols.index('Plastic P-Edge (Suffix P)') + 1, 'Plastic Knife Edge (Suffix K)')
for pid in ('us-fixed-pedestals', 'us-mobile-pedestals'):
    cols = prod(pid)['columns']
    if 'Proud Laminate Front Suffix L' not in cols: cols.insert(cols.index('Proud Wood Front Suffix W') + 1, 'Proud Laminate Front Suffix L')
# price texts still carrying the 2015 amount: the printed 2022 amount (the June list; the planner adds the July 2022 9% itself)
n = 0
for p in cat['products']:
    for o in p.get('options', []):
        pr = o.get('price')
        if not isinstance(pr, (int, float)): continue
        for k in ('priceText', 'priceNote'):
            t = o.get(k)
            if not isinstance(t, str): continue
            m = re.match(r'^([+\-–])\s*\$(\d[\d,]*)(.*)$', t)
            if m and int(m.group(2).replace(',', '')) != abs(pr):
                o[k] = f"{'-' if pr < 0 else '+'}${abs(pr)}{m.group(3)}"; n += 1
log.append(f'{n} option price texts brought to the printed 2022 amount')

json.dump(cat, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
open(os.path.join(ROOT, 'guide2022', '_review_fixes_report.txt'), 'w', encoding='utf-8').write('\n'.join(log) + '\n')
print('\n'.join(log)); print('review fixes applied')

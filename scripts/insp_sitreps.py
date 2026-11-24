"""Download and parse the INSP daily situation reports (SitRep) of the 2026 BDBV Ebola outbreak.

The Institut National de Santé Publique (DRC) posts one French PDF per reporting day on insp.cd
(N°2 of 18 May to N°190 of 20 November 2026 when this was written, 24 November). Each report
counts confirmed cases and deaths by health zone (cumulative), alerts and suspected cases by
province, contacts under follow-up by province, and national laboratory testing. Counts are by
reporting day, not by symptom onset: they are what the response knew on that day, published 1-2
days later, so they lead the Hub's weekly onset series.

    .venv/bin/python scripts/insp_sitreps.py download   # list insp.cd uploads, fetch new PDFs, pdftotext
    .venv/bin/python scripts/insp_sitreps.py parse      # -> data/ebola/insp-sitreps.csv

Files: data/ebola/source/insp-sitreps/{manifest.json, pdf/, txt/}. The manifest keeps each file's
WordPress upload time (`uploaded`, site time), which is when the report became public; several
reports were uploaded twice (corrections), and every version is parsed. `pdftotext` (poppler)
must be on the PATH.

Output, one row per number: report, report_date, file, uploaded, latest (the newest upload of that
report number), table, location (Hub code, '' when unmatched), location_name (as printed), level,
indicator, value. Tables and indicators:
- zones: cum_cases, cum_deaths per health zone and province, as printed (a province row is the
  report's own, never a sum); reports of 9-12 August print the day's new_cases, new_deaths instead; 'unallocated' rows ("A ventiler", "Autres ZS",
  "Non identifiées") are kept with an empty location.
- alerts (province): alerts_received, alerts_investigated, suspects_validated, suspects_validated_dead,
  suspects_transferred. Two layouts: one row per indicator (May-July) or one row per province (August on).
- contacts (province and country): contacts_followed (under follow-up), contacts_seen; from the
  table, or from the prose "x/y" or "x vus sur y" when no table was printed.
- lab: samples_tested, samples_positive, positivity_pct for the country from the highlights paragraph
  (late September on); samples_tested, samples_positive by province from the laboratory section's prose.
- headline (country, August on): cum_cases, cum_deaths, patients_isolated, recovered_cum and
  contacts_seen_pct (contact follow-up rate of the day) from the box under the highlights.
Values printed as ND/NA are not written.
"""
import json
import re
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

ROOT = Path('data/ebola/source/insp-sitreps')
HUB = Path('production/hubs/BDBV-Modeling-Hub')
OUT = Path('data/ebola/insp-sitreps.csv')
AGENT = {'User-Agent': 'Mozilla/5.0 (research client)'}
MONTHS = {m: i + 1 for i, m in enumerate(['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet',
                                          'aout', 'septembre', 'octobre', 'novembre', 'decembre'])}
# Printed names that differ from the Hub's after normalisation (lowercase, no accents, letters only).
ALIASES = {'gety': 'gethy', 'makiso': 'makisokisangani', 'kisangani': 'makisokisangani', 'boma': 'bomamangbetu',
           'wanie': 'wanierukula', 'nainia': 'niania'}
UNALLOCATED = re.compile(r'ventiler|autres zs|non identifi|non ventil|autres', re.I)


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'^(sous-total|sous total|total)\s+', '', s.strip())
    s = re.sub(r'\(.*?\)', '', s)
    return re.sub(r'[^a-z]', '', s)


def download():
    """List every PDF upload matching SitRep since May 2026 and fetch the new ones."""
    rows = {}
    for q in ['SitRep', 'MVE', 'Ebola']:
        for page in range(1, 10):
            url = (f'https://insp.cd/wp-json/wp/v2/media?search={q}&per_page=100&page={page}'
                   '&_fields=id,date,modified,source_url,mime_type')
            try:
                batch = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=120))
            except Exception:
                break
            if not batch:
                break
            rows.update({x['id']: x for x in batch})
    keep = sorted((x for x in rows.values() if x['mime_type'] == 'application/pdf' and x['date'] >= '2026-05'
                   and re.search('sitrep', x['source_url'], re.I)), key=lambda x: x['date'])
    man = [{'file': x['source_url'].rsplit('/', 1)[1], 'url': x['source_url'], 'uploaded': x['date'],
            'modified': x['modified'], 'wp_id': x['id']} for x in keep]
    (ROOT / 'pdf').mkdir(parents=True, exist_ok=True)
    (ROOT / 'txt').mkdir(exist_ok=True)
    (ROOT / 'manifest.json').write_text(json.dumps(man, indent=1, ensure_ascii=False))

    def get(m):
        f = ROOT / 'pdf' / m['file']
        if not f.exists():
            try:
                req = urllib.request.Request(urllib.parse.quote(m['url'], safe=':/%'), headers=AGENT)
                data = urllib.request.urlopen(req, timeout=600).read()
            except Exception as e:  # three August reports (N°83-85) were deleted from the site
                return f'{m["file"]}: {e}'
            f.with_suffix('.part').write_bytes(data)
            f.with_suffix('.part').rename(f)
        t = ROOT / 'txt' / (f.stem + '.txt')
        if not t.exists():
            subprocess.run(['pdftotext', '-layout', str(f), str(t)], check=True)

    with ThreadPoolExecutor(8) as ex:
        for err in ex.map(get, man):
            if err:
                print('not downloaded:', err)
    print(f'{len(man)} uploads listed, {len(list((ROOT / "pdf").glob("*.pdf")))} PDFs on disk')


class Places:
    """Hub provinces and health zones, matched by normalised name (zones within their province first)."""

    def __init__(self):
        loc = pd.read_csv(HUB / 'auxiliary-data/locations.csv')
        prov = loc[loc.location_type == 'province']
        self.province = {norm(n): c for n, c in zip(prov.location_name, prov.location)}
        name_to_code = dict(zip(prov.location_name, prov.location))
        zones = loc[loc.location_type == 'health zone']
        self.zone = {}
        self.zone_any = {}
        for n, c, p in zip(zones.location_name, zones.location, zones.parent):
            self.zone[(name_to_code[p], norm(n))] = c
            self.zone_any.setdefault(norm(n), []).append(c)

    def find_province(self, name):
        k = ALIASES.get(norm(name), norm(name))
        return self.province.get(k)

    def find_zone(self, name, province):
        k = ALIASES.get(norm(name), norm(name))
        if (province, k) in self.zone:
            return self.zone[(province, k)]
        hits = self.zone_any.get(k, [])
        return hits[0] if len(hits) == 1 else None  # unique in the DRC: the province label may be misplaced


NUM = r'(?:\d{1,3}(?:[   ]\d{3})+(?![\d,])|\d+(?:,\d+)?)'
TOKEN = re.compile(rf'({NUM})\s*(%?)|\b(ND|NA|n\.a\.)\b', re.I)


def tokens(s):
    """Numbers in a line, in order; percentages are tagged; ND/NA become None."""
    out = []
    for m in TOKEN.finditer(s):
        if m.group(3):
            out.append(None)
        else:
            v = float(re.sub(r'[   ]', '', m.group(1)).replace(',', '.'))
            out.append(('%', v) if m.group(2) else v)
    return out


def split_row(line):
    """(name, numbers) for a table row: the name is the text before the first number."""
    m = re.search(rf'(?<![\w-])({NUM}|ND\b|NA\b)', line)
    if not m:
        return line.strip(), []
    return line[:m.start()].strip(' .:-*\t'), tokens(line[m.start():])


def report_meta(text, fname):
    num = re.search(r'SitRep\s*N\s*°?\s*(\d+)', text[:3000], re.I) or re.search(r'N(?:A°|°|_|°_)?_?0*(\d{1,3})[_ -]', fname)
    date = None
    m = re.search(r'Date de rapportage\s*:?\s*(\d{1,2})(?:er)?\s+([a-zéû]+)\s+(2026)', text[:4000], re.I)
    if m and norm(m.group(2)) in MONTHS:
        date = pd.Timestamp(2026, MONTHS[norm(m.group(2))], int(m.group(1)))
    if date is None:
        m = re.search(r'(\d{2})[_-](\d{2})[_-](2026)', fname) or re.search(r'(\d{2})(\d{2})(2026)', fname)
        if m:
            date = pd.Timestamp(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return (int(num.group(1)) if num else None), date


def section(lines, title, stop=r'^\s*(Tableau|TABLEAU|Figure|FIGURE)\b|^\s*\d+(\.\d+)*\.?\s+[A-ZÉ]'):
    """Lines after the first line matching `title` up to the next table/figure/section heading."""
    for i, line in enumerate(lines):
        if re.search(title, line, re.I):
            out = []
            for later in lines[i + 1:]:
                if re.search(stop, later) and not re.search(title, later, re.I):
                    # a repeated header of the same table on the next page does not end it
                    if out and not re.search(r'Province\s*/|Nombre cumulatif', later):
                        break
                out.append(later)
            return out
    return []


ZONE_TITLE = (r'^(?!.*suspect)\s*((tableau|table)\s*[\dIVX]*\s*[.—-]*\s*)?(r[ée]partition des cas.{0,60}(province et zone|zone de sant)'
              r'|cas.{0,25}d[ée]c[èe]s.{0,30}par province et zone)')


def parse_zones(lines, places):
    """Rows of the zone table: a known province or zone name, then cumulative cases and deaths. The table
    ends at its TOTAL row; rows whose name is neither known nor short are prose and are skipped. Reports
    before June (and N°20, N°33, 1 July) print no such table; May reports mix suspected cases into theirs."""
    rows, province, fragment = [], None, ''
    body = section(lines, ZONE_TITLE)
    first = next((k for k, line in enumerate(body) if len(split_row(line)[1]) >= 2), len(body))
    header = ' '.join(body[:first])
    # 9-12 August print the day's new cases and deaths by zone instead of cumulative counts
    labels = ['new_cases', 'new_deaths'] if re.search(r'nouveaux cas', header, re.I) and not re.search(r'cumul', header, re.I) \
        else ['cum_cases', 'cum_deaths']
    for k, line in enumerate(body):
        parts = re.split(r'\s{2,}', line.strip(), maxsplit=1)
        if len(parts) == 2 and places.find_province(parts[0]) and not re.match(r'[\d(]', parts[1]):
            province, line = places.find_province(parts[0]), parts[1]  # "Ituri    Bambu  126 ..."
        name, nums = split_row(line)
        if re.match(r'^\s*total\b', name, re.I) and rows and nums:
            break
        p = places.find_province(name) if name else None
        if not nums:  # header line, province heading without numbers, or a wrapped name
            if p:
                province, fragment = p, ''
            elif 0 < len(name) < 20 and not re.search(r'cumul|d[ée]c[èe]s|cas|zone|province|l[ée]talit|situation|nombre|confirm|swab|intra|communaut|sant', name, re.I):
                fragment = name
            continue
        # every row prints cumulative cases, cumulative deaths and the case fatality ratio (% or NA)
        if len(nums) < 2 or not all(isinstance(v, float) for v in nums[:2]):
            continue
        known = (places.find_zone(name, province) or places.find_province(name) or re.match(r'^sous[- ]?total', name, re.I)
                 or UNALLOCATED.search(name))
        if (len(nums) < 3 or isinstance(nums[2], float)) and not known:
            continue  # known names may print the fatality ratio without % or lose it to wrapping; others are prose
        if not name:  # name wrapped around the numbers: "Boma / 51 24 ... / Mangbetu"
            nxt = split_row(body[k + 1]) if k + 1 < len(body) else ('', [1])
            name = (fragment + ' ' + (nxt[0] if not nxt[1] and len(nxt[0]) < 20 else '')).strip()
            p = places.find_province(name)
        fragment = ''
        subtotal = re.match(r'^sous[- ]?total', name, re.I)
        if subtotal:
            p = places.find_province(name[subtotal.end():]) or province
        # "Tshopo" is a province and one of its zones: it is the province unless we are already in it
        if p and (p != province or places.find_zone(name, province) is None or subtotal):
            level, code, province = 'province', p, p
        elif places.find_zone(name, province):
            level, code = 'zone', places.find_zone(name, province)
            province = code.rsplit('-', 1)[0]
        elif UNALLOCATED.search(name):
            level, code = 'unallocated', ''
        elif 0 < len(name) < 20 and len(name.split()) <= 3:
            level, code = 'zone', ''  # a zone the Hub does not list (Dakwa) or an unknown spelling
        else:
            continue
        for ind, v in zip(labels, nums[:2]):
            rows.append(dict(table='zones', location=code, location_name=name, level=level,
                             parent=province or '', indicator=ind, value=v))
    return rows


ALERT_ROWS = [(r'alertes remont|nouvelles alertes re|^\s*total alertes du jour', 'alerts_received'),
              (r'alertes investigu', 'alerts_investigated'),
              (r'total (des )?cas suspects', 'suspects_validated'),
              (r'd[ée]c[ée]d[ée]e?s?\b', 'suspects_validated_dead')]


def parse_alerts(lines, places):
    body = section(lines, r'^\s*((tableau|table)\b.{0,40})?(situation des alertes|gestion des alertes)')
    rows, columns, previous = [], None, ''
    for line in body:
        name, nums = split_row(line)
        if not name and len(nums) in (9, 10) and re.match(r'total', previous, re.I):
            name = 'Total'  # "Total / 4 410 194 ... / Général"
        previous = name or previous
        heads = [places.find_province(w) for w in re.split(r'\s{2,}', line.strip())]
        if sum(h is not None for h in heads) >= 2 and not nums:  # indicator-row layout: provinces as columns
            columns = [h for h in heads if h is not None]
            columns += ['CD'] if re.search(r'\bTotal\b', line) else []
            continue
        if columns:
            for pattern, ind in ALERT_ROWS:
                if re.search(pattern, name, re.I) and not (ind == 'alerts_received' and 'total alertes' not in name.lower()
                                                           and any(r['indicator'] == ind for r in rows)):
                    if ind == 'alerts_received' and 'total alertes' in name.lower():
                        rows = [r for r in rows if r['indicator'] != ind]
                    for code, v in zip(columns, nums):
                        if isinstance(v, float):
                            rows.append(dict(table='alerts', location=code, location_name=code, level='province',
                                             indicator=ind, value=v))
                    break
            continue
        p = places.find_province(name) if name else None
        if (p or re.match(r'total', name, re.I)) and len(nums) in (9, 10):  # one row per province (August on)
            code = p or 'CD'
            # received alive/dead/total, validated alive/dead, invalidated alive/dead, suspects investigated,
            # (from late October an extra column), suspects transferred
            vals = dict(zip(['ra', 'rd', 'rt', 'va', 'vd', 'ia', 'id', 'inv'], nums[:8]), tr=nums[-1])
            out = {'alerts_received': vals['rt'], 'suspects_validated_dead': vals['vd'], 'suspects_transferred': vals['tr']}
            if isinstance(vals['va'], float) and isinstance(vals['vd'], float):
                out['suspects_validated'] = vals['va'] + vals['vd']
            for ind, v in out.items():
                if isinstance(v, float):
                    rows.append(dict(table='alerts', location=code, location_name=name, level='province' if p else 'country',
                                     indicator=ind, value=v))
    for r in rows:
        if r['location'] == 'CD':
            r['level'] = 'country'
    return rows


def parse_contacts(lines, text, places):
    rows, done = [], set()
    for line in section(lines, r'(tableau|table)\b.*suivi des contacts'):
        name, nums = split_row(line)
        code = 'CD' if re.match(r'total', name, re.I) else places.find_province(re.sub(r'[(*].*', '', name))
        if code and code not in done and len(nums) >= 2 and isinstance(nums[0], float) and isinstance(nums[1], float):
            done.add(code)
            for ind, v in zip(['contacts_followed', 'contacts_seen'], nums[:2]):
                rows.append(dict(table='contacts', location=code, location_name=name,
                                 level='country' if code == 'CD' else 'province', indicator=ind, value=v))
        if code == 'CD' and rows:
            break  # the table ends at its Total row; prose and other tables follow
    if rows:
        return rows
    # prose only: "89,0 % (16 719 vus sur 18 784 à suivre) ... 90,1% au Nord-Kivu (7 468/8 293)"
    flat = re.sub(r'\s+', ' ', text)
    m = re.search(rf'contacts? (?:suivis|vus)?[^.]{{0,160}}?\(({NUM}) vus sur ({NUM})', flat) or \
        re.search(rf'taux de suivi des contacts[^.]{{0,80}}?\(({NUM}) ?/ ?({NUM})\)', flat, re.I)
    if m:
        seen, followed = tokens(m.group(1))[0], tokens(m.group(2))[0]
        rows += [dict(table='contacts', location='CD', location_name='prose', level='country', indicator=i, value=v)
                 for i, v in [('contacts_followed', followed), ('contacts_seen', seen)]]
        for pm in re.finditer(rf'[\d,]+ ?% (?:à la |au |en |à |au niveau de )?([A-ZÉ][\w\- ]{{2,15}}?) \(({NUM}) ?/ ?({NUM})\)', flat):
            code = places.find_province(pm.group(1))
            if code:
                rows += [dict(table='contacts', location=code, location_name='prose', level='province', indicator=i,
                              value=tokens(g)[0]) for i, g in [('contacts_followed', pm.group(3)), ('contacts_seen', pm.group(2))]]
    return rows


def parse_lab(text, places):
    head = re.sub(r'\s+', ' ', text[:6000])
    out = {}
    m = re.search(rf'(?:total de|au total,?|) ?({NUM}) (?:nouveaux )?[ée]chantillons (?:a|ont) [ée]t[ée] analys', head, re.I)
    if m:
        out['samples_tested'] = tokens(m.group(1))[0]
    m = re.search(rf'(?:dont |; )?({NUM}) (?:de ces [ée]chantillons |[ée]chantillons )?(?:se sont|sont|ont [ée]t[ée]) (?:r[ée]v[ée]l[ée]s |revenus )?positifs', head, re.I)
    if m:
        out['samples_positive'] = tokens(m.group(1))[0]
    m = re.search(r'soit (?:un taux de |de |une )?([\d]+(?:,\d+)?) ?% de positivit', head, re.I) or \
        re.search(r'taux de positivit[ée] (?:de |: |global de )?([\d]+(?:,\d+)?) ?%', head, re.I)
    if m:
        out['positivity_pct'] = float(m.group(1).replace(',', '.'))
    rows = [dict(table='lab', location='CD', location_name='headline', level='country', indicator=k, value=v)
            for k, v in out.items()]
    # province lines of the laboratory section: "Ituri : 49 nouveaux résultats positifs (...) sur 291 échantillons"
    # or "Ituri : 155 échantillons documentés ..., dont 51 positifs"
    flat = re.sub(r'\s+', ' ', text)
    lab = flat[flat.lower().find('laboratoire'):] if 'laboratoire' in flat.lower() else ''
    seen = set()
    for m in re.finditer(rf'([A-ZÉ][\w\- ]{{2,12}}?) ?: ?({NUM}) nouveaux r[ée]sultats positifs[^.;•→]{{0,80}}? sur ({NUM}) (?:nouveaux )?[ée]chantillons'
                         rf'|([A-ZÉ][\w\- ]{{2,12}}?) ?: ?({NUM}) [ée]chantillons[^.;•→]{{0,90}}?dont ({NUM}) positifs', lab):
        name, pos, tested = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(4), m.group(6), m.group(5))
        code = places.find_province(name)
        if code and code not in seen:
            seen.add(code)
            rows += [dict(table='lab', location=code, location_name=name, level='province', indicator=i, value=tokens(v)[0])
                     for i, v in [('samples_tested', tested), ('samples_positive', pos)]]
    return rows


def parse_headline(text):
    """The box under the highlights (August on): cumulative cases, deaths, fatality, patients in isolation,
    recovered, contact follow-up rate of the day."""
    flat = re.sub(r'\s+', ' ', text[:8000])
    m = re.search(r'\(Du Jour\)(.{0,120})', flat)
    if not m:
        return []
    t = tokens(m.group(1))[:6]
    if len(t) < 6 or not isinstance(t[2], tuple) or not isinstance(t[5], tuple):
        return []
    vals = {'cum_cases': t[0], 'cum_deaths': t[1], 'patients_isolated': t[3], 'recovered_cum': t[4],
            'contacts_seen_pct': t[5][1]}
    return [dict(table='headline', location='CD', location_name='headline', level='country', indicator=k, value=v)
            for k, v in vals.items() if isinstance(v, float)]


def parse():
    places = Places()
    man = json.loads((ROOT / 'manifest.json').read_text())
    rows = []
    for m in man:
        t = ROOT / 'txt' / (Path(m['file']).stem + '.txt')
        if not t.exists():
            continue
        text = t.read_text()
        lines = text.splitlines()
        report, date = report_meta(text, m['file'])
        # May reports print suspected and confirmed cases together by zone; zone counts start in June
        parsed = ((parse_zones(lines, places) if m['uploaded'] >= '2026-06' else []) + parse_alerts(lines, places) + parse_contacts(lines, text, places)
                  + parse_lab(text, places) + parse_headline(text))
        rows += [dict(report=report, report_date=date, file=m['file'], uploaded=m['uploaded'], **r) for r in parsed]
    d = pd.DataFrame(rows)
    newest = d.groupby('report').uploaded.transform('max')
    d['latest'] = d.uploaded == newest
    cols = ['report', 'report_date', 'file', 'uploaded', 'latest', 'table', 'location', 'location_name', 'level',
            'parent', 'indicator', 'value']
    d = d.reindex(columns=cols).sort_values(['report_date', 'uploaded', 'table', 'location']).reset_index(drop=True)
    d.to_csv(OUT, index=False)
    print(f'{len(d)} values from {d.file.nunique()} files ({d.report.nunique()} report numbers) -> {OUT}')
    print(d.groupby(['table', 'indicator']).file.nunique().to_string())


if __name__ == '__main__':
    {'download': download, 'parse': parse}[sys.argv[1]]()

"""Recover district influenza curves without relabeling their seven-day means as Hub targets."""
import argparse
from datetime import date, timedelta, datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import pandas as pd

SOURCE = Path('data/metrocast/source/utah-respiratory-dashboard-20251006.html')
DESTINATION = Path('data/metrocast-utah-source')
DISTRICTS = [
    ('Bear River', 'bear-river'), ('Central Utah', 'central'), ('Davis County', 'davis'),
    ('Salt Lake County', 'salt-lake'), ('San Juan', 'san-juan'),
    ('Southeast Utah', 'southeast'), ('Southwest Utah', 'southwest'),
    ('Summit County', 'summit'), ('Tooele County', 'tooele'), ('TriCounty', 'tri-county'),
    ('Utah County', 'utah-county'), ('Wasatch County', 'wasatch'), ('Weber-Morgan', 'weber-morgan')]


class Widgets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []
        self.widgets = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.active = dict(attrs).get('type') == 'application/json'
            self.parts = []

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            self.widgets.append(json.loads(''.join(self.parts)))
            self.active = False


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--source', type=Path, default=SOURCE)
    args.add_argument('--destination', type=Path, default=DESTINATION)
    args.add_argument('--live', action='store_true')
    args = args.parse_args()
    raw = args.source.read_bytes()
    assert raw.rstrip().endswith(b'</html>'), 'Truncated dashboard capture'
    parser = Widgets()
    parser.feed(raw.decode())
    names = [name for name, _ in DISTRICTS]
    matches = [w['x'] for w in parser.widgets
               if [a.get('text') for a in w.get('x', {}).get('layout', {}).get('annotations', [])] == names]
    assert len(matches) == 1, 'District facet labels changed or ambiguous'
    chart = matches[0]
    traces = [t for t in chart['data'] if t.get('name') == 'Influenza']
    assert len(traces) == 13
    metadata = pd.read_csv('data/metrocast/source/locations.csv').set_index('location')
    rows = []
    for index, ((district, location), trace) in enumerate(zip(DISTRICTS, traces), 1):
        assert trace['yaxis'] == ('y' if index == 1 else f'y{index}')
        assert str(metadata.loc[location, 'original_location_code']) == str(index)
        assert metadata.loc[location, 'location_type'] == 'ut_region_id'
        assert len(trace['x']) == len(trace['y']) == len(trace['text'])
        for x, value, hover in zip(trace['x'], trace['y'], trace['text']):
            day = (date(1970, 1, 1)+timedelta(days=int(x))).isoformat()
            assert re.search(r'Date:\s*'+day, hover)
            assert '% of Visits (7 day avg)' in hover
            if value is not None:
                assert 0 <= value <= 100
                shown = float(hover.rsplit(':', 1)[1].strip())
                assert abs(value-shown) <= .0051
            rows.append(dict(date=day, location=location, district=district,
                             influenza_ed_seven_day_mean_percentage=value,
                             measure='Dashboard seven-day average of ED influenza percentage; weekly Hub equivalence unverified'))
    frame = pd.DataFrame(rows)
    assert not frame.duplicated(['date', 'location']).any()
    args.destination.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.destination/'district-influenza-seven-day-means.csv', index=False)
    finite = frame.dropna(subset=['influenza_ed_seven_day_mean_percentage'])
    coverage = finite.groupby('location').date.agg(['min', 'max', 'count'])
    coverage.to_csv(args.destination/'coverage.csv')
    manifest = dict(
        source=str(args.source), sha256=hashlib.sha256(raw).hexdigest(),
        original_url='https://files.epi.utah.gov/Utah-respiratory-dashboard.html',
        archived_url=None if args.live else 'https://web.archive.org/web/20251006040625id_/https://files.epi.utah.gov/Utah-respiratory-dashboard.html',
        archive_timestamp=None if args.live else '2025-10-06T04:06:25Z',
        retrieved_at=datetime.fromtimestamp(args.source.stat().st_mtime, timezone.utc).isoformat() if args.live else None,
        geography='Thirteen Utah local health districts matched by explicit facet names, axes, and Hub ut_region_id',
        measure='Seven-day average ED influenza percentage, as explicitly labeled by dashboard hover text',
        use='Source audit only; not inserted into training panels or relabeled as weekly MetroCast target',
        limits=['Numerator/denominator weekly aggregation is not exposed; seven-day mean may differ from weekly visit-weighted percentage',
                'Single current revised release; historical release availability not established' if args.live else 'Single archived release; no current2026 district inputs',
                'No reserved2025-26 scoring or model selection'],
        rows=len(frame), nonmissing=len(finite), locations=13)
    (args.destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(coverage.to_string())


if __name__ == '__main__':
    main()

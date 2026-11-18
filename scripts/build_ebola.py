"""Build one weekly Ebola case panel from three outbreaks, at three geographic levels each.

Sources (downloaded once into data/ebola/source):
- BDBV 2026 (DRC, Bundibugyo virus): BDBV Modeling Hub target data, confirmed cases by
  week of symptom onset, latest release. Health zone, province and national series.
- Kivu 2018-20 (DRC, Zaire ebolavirus): andersen-lab/ebola-drc-epidemiology, confirmed
  cases by health zone per WHO situation-report interval (differences of cumulative
  totals, so by report week, not onset week). Health zone, province and outbreak total.
- West Africa 2014-15 (Guinea, Liberia, Sierra Leone): ebov/space-time EBOV_maxCases.csv,
  confirmed and probable cases by district and epi week (larger of WHO situation report
  and patient database). District, country and outbreak total.

Outbreaks never overlap in time, so one calendar panel holds all of them; a location is
missing (NaN) outside its outbreak. Only locations with at least one case are kept.
Every location gets the same nominal population of 100,000, so Chromantis's count
transforms act on counts (fourth root of the count, up to a constant): Ebola incidence
does not scale with population, and DRC health-zone populations are not readily available.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('data/ebola')
SRC = ROOT / 'source'
HUB = Path('../hubs/BDBV-Modeling-Hub')
# BDBV weeks from this one on are still being reported (lags 0-2 of the latest release; the 10 Oct
# week grew 34 -> 314 -> 413 -> 465 over four releases), so they are not usable as labels or
# finalized inputs. Was 10 Oct for the 24 Oct release, 17 Oct for the 1 Nov release.
BDBV_INCOMPLETE_FROM = '2026-10-31'


def saturday_on_or_before(day):
    day = pd.Timestamp(day)
    return day - pd.Timedelta(days=(day.weekday() - 5) % 7)


def bdbv():
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    t = t[t.as_of == t.as_of.max()]
    level = t.location_type.map({'country': 'top', 'province': 'middle', 'health zone': 'local'})
    t = t.assign(level=level, week=pd.to_datetime(t.target_end_date))
    t.loc[t.target_end_date >= BDBV_INCOMPLETE_FROM, 'observation'] = np.nan
    # Parents come from the codes alone (CD-TO-15 -> CD-TO -> CD), never from names: until 27 Oct
    # they were matched by name, and the health zone Tshopo (CD-TO-15) overwrote the province of the
    # same name, so the Tshopo zones were assigned to CD-TO-15 (Kinshasa and Lualaba clash too).
    t['parent'] = t.location.map(lambda c: '' if c == 'CD' else c.rsplit('-', 1)[0])
    return t[['location', 'level', 'parent', 'week', 'observation']].assign(outbreak='bdbv-2026')


def kivu():
    raw = pd.read_csv(SRC / 'kivu-andersen/dataonly_ebolaDRC.csv', header=None)
    intervals = raw.iloc[0, 4:].tolist()  # column 3 is the cumulative count before 5 Aug 2018
    body = raw.iloc[2:].copy()
    body[0] = body[0].ffill()
    body = body[body[2].str.strip() == 'Confirmed']
    # Each health zone's cumulative count at every report-interval end (counted from 5 Aug 2018), made
    # non-decreasing by holding earlier values down to later totals (reclassified cases revise
    # totals down), then interpolated day by day to Saturdays and differenced. Intervals of 6 to 14
    # days are thus spread over the weeks they cover, and the total equals the signed source total.
    # History: until 27 Oct each interval's count went whole into the Saturday week of its end date
    # and negative increments were clipped to 0 (3,283 signed cases became 3,401).
    ends = [pd.Timestamp(label.split(' - ')[1]) for label in intervals]
    times = np.array([(t - pd.Timestamp('2018-08-05')).days for t in [pd.Timestamp('2018-08-05')] + ends], float)
    saturdays = pd.date_range('2018-08-04', saturday_on_or_before(ends[-1]), freq='W-SAT')
    at = np.array([(s - pd.Timestamp('2018-08-05')).days for s in saturdays], float)
    rows = []
    prov = {'North Kivu': 'NK', 'South Kivu': 'SK', 'Ituri': 'IT'}
    for r in body.itertuples(index=False):
        hz = f'KV-{prov[r[0].strip()]}-{r[1].strip().replace(" ", "_")}'
        cum = np.r_[0, np.cumsum(np.array(r[4:], float))]
        cum = np.minimum.accumulate(cum[::-1])[::-1]
        weekly = np.diff(np.interp(at, times, cum))
        rows += [(hz, 'local', hz.rsplit('-', 1)[0], s, v) for s, v in zip(saturdays[1:], weekly)]
    d = pd.DataFrame(rows, columns=['location', 'level', 'parent', 'week', 'observation'])
    return with_aggregates(d, 'KV').assign(outbreak='kivu-2018')


def west_africa():
    raw = pd.read_csv(SRC / 'wa-ebov-maxCases.csv')
    d = raw.melt(id_vars=['country', 'district', 'standard'], var_name='start', value_name='observation')
    d['week'] = pd.to_datetime(d.start, format='%Y-%b-%d') + pd.Timedelta(days=5)  # Monday-start weeks
    d['location'] = 'WA-' + d.country + '-' + d.district.str.replace(' ', '_')
    d = d.assign(level='local', parent='WA-' + d.country)[['location', 'level', 'parent', 'week', 'observation']]
    return with_aggregates(d, 'WA').assign(outbreak='west-africa-2014')


def with_aggregates(local, top):
    """Add middle (province/country) and top (outbreak) sums; NaN weeks stay NaN."""
    total = lambda s: s.sum(min_count=1)
    middle = local.groupby(['parent', 'week'], as_index=False).observation.agg(total)
    middle = middle.rename(columns={'parent': 'location'}).assign(level='middle', parent=top)
    whole = local.groupby('week', as_index=False).observation.agg(total).assign(location=top, level='top', parent='')
    return pd.concat([local, middle, whole], ignore_index=True)


def main():
    data = pd.concat([west_africa(), kivu(), bdbv()], ignore_index=True)
    cases = data.groupby('location').observation.sum()
    data = data[data.location.isin(cases[cases > 0].index)]
    if data.duplicated(['location', 'week']).any():
        raise ValueError('Duplicate location/week observations')
    if not (data.week.dt.dayofweek == 5).all():
        raise ValueError('Every week must end on Saturday')
    if (data.observation < 0).any():
        raise ValueError('Negative weekly counts')
    dates = pd.date_range(data.week.min(), data.week.max(), freq='W-SAT')
    meta = data.drop_duplicates('location').set_index('location')[['level', 'parent', 'outbreak']]
    locations = sorted(meta.index, key=lambda c: (meta.outbreak[c], c))
    wide = data.pivot(index='week', columns='location', values='observation').reindex(index=dates, columns=locations)
    values = wide.to_numpy(np.float32)
    # Covariates at the same weekly cutoff: the parent series (province or country) and the
    # outbreak total. Top-level series use themselves.
    top = {o: meta.index[(meta.outbreak == o) & (meta.level == 'top')][0] for o in meta.outbreak.unique()}
    parent = [meta.parent[c] or c for c in locations]
    covariates = np.stack([wide[parent].to_numpy(np.float32),
                           wide[[top[meta.outbreak[c]] for c in locations]].to_numpy(np.float32)], -1)
    np.savez_compressed(
        ROOT / 'panel.npz', dates=dates.to_numpy(dtype='datetime64[D]'), locations=np.array(locations),
        target_names=np.array(['ebola_cases']), targets=values[..., None], covariates=covariates,
        covariate_names=np.array(['parent_cases', 'outbreak_cases']),
        covariates_national=np.empty((len(dates), 0), np.float32), covariate_national_names=np.array([], dtype='U1'),
        truth_day=np.array('2026-10-31'))
    meta.loc[locations].reset_index().assign(population=100000.0).to_csv(ROOT / 'locations.csv', index=False)
    summary = data.groupby(['outbreak', 'level']).agg(locations=('location', 'nunique'), cases=('observation', 'sum'),
                                                       first=('week', 'min'), last=('week', 'max'))
    manifest = dict(
        hub_commit=__import__('subprocess').check_output(['git', '-C', str(HUB), 'rev-parse', 'HEAD'], text=True).strip(),
        bdbv_release=str(pd.read_csv(HUB / 'target-data/time-series.csv').as_of.max()),
        bdbv_incomplete_from=BDBV_INCOMPLETE_FROM, locations=len(locations), weeks=len(dates),
        summary={f'{o}/{l}': dict(locations=int(r.locations), cases=float(r.cases), first=str(r['first'].date()), last=str(r['last'].date()))
                 for (o, l), r in summary.iterrows()},
        population='nominal 100,000 for every location',
    )
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()

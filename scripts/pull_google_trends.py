"""Weekly Google Trends search interest per state for flu-related searches (flu search, 23 Nov 2026).

GaTech's ARGO models (the top FluSight model of Oct-Nov 2026) and MIGHTE use Google Trends; Delphi's Google symptom-search
feed stopped on 29 Oct 2025, so Trends (pytrends, unofficial API) is the live source. Each request covers one state and one
term over 2022-08-01..today, so Google returns weekly values (Sunday-Saturday weeks) scaled 0-100 to the state's maximum in
that window. A Trends week starting Sunday d is stored at its Saturday d+6, the NHSN week-ending date. The scale is
window-dependent, so models must read it scale-free (log ratios), never as a level comparable across pulls.

    python scripts/pull_google_trends.py --out data/raw/google_trends
    python scripts/pull_google_trends.py --terms covid --out data/raw/google_trends   (COVID/RSV search, 24 Nov 2026)
"""
import argparse
import random
import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq

TERM_SETS = {'flu': {'flu_topic': '/m/0cycc', 'flu_symptoms': 'flu symptoms', 'tamiflu': 'tamiflu'},
             'covid': {'covid_symptoms': 'covid symptoms', 'covid_test': 'covid test'},
             'rsv': {'rsv': 'rsv', 'rsv_symptoms': 'rsv symptoms'}}
STATES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
          'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
          'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'US']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/raw/google_trends')
    ap.add_argument('--start', default='2022-08-01')
    ap.add_argument('--end', default=pd.Timestamp.today().strftime('%Y-%m-%d'))
    ap.add_argument('--terms', nargs='+', default=['flu'], choices=sorted(TERM_SETS))
    a = ap.parse_args()
    terms = {k: v for t in a.terms for k, v in TERM_SETS[t].items()}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pulled = pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%M:%SZ')
    p = TrendReq(hl='en-US', tz=300, timeout=(10, 30))
    for name, term in terms.items():
        f = out / f'{name}.csv'
        have = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=['date', 'location', 'value', 'partial', 'pulled_at'])
        for s in STATES:
            if s in set(have.location):
                continue
            for attempt in range(6):
                try:
                    p.build_payload([term], timeframe=f'{a.start} {a.end}', geo='US' if s == 'US' else f'US-{s}')
                    d = p.interest_over_time()
                    break
                except Exception as e:  # 429 rate limits: back off
                    print(s, name, 'retry', attempt, str(e)[:80], flush=True)
                    time.sleep(60 * (attempt + 1))
            else:
                raise RuntimeError(f'{s} {name} failed')
            d = d.reset_index()
            rows = pd.DataFrame({'date': (d.date + pd.Timedelta(days=6)).dt.strftime('%Y-%m-%d'), 'location': s,
                                 'value': d[term].astype(int), 'partial': d.isPartial.astype(bool), 'pulled_at': pulled})
            have = pd.concat([have, rows])
            have.to_csv(f, index=False)
            print(name, s, len(rows), flush=True)
            time.sleep(random.uniform(4, 8))


if __name__ == '__main__':
    main()

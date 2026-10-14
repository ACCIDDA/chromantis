"""Weekly submission commands; nothing is published (opening the Hub PR is a separate, human step).

    python -m chromantis.production run --release production/releases/b7-20261007.json \
        --dataset data/operational-<date>/processed/panel.npz --issuance <wednesday>
    python -m chromantis.production record production/output/<wednesday>/<release>/<reference>-ACCIDDA-<model>.csv
    python -m chromantis.production intervals A.csv [B.csv --labels A B]
    python -m chromantis.production peers A.csv [B.csv ...]
    python -m chromantis.production diff SUBMITTED.csv NEW.csv OUTDIR [--labels A B]

`run` replays every released checkpoint (`forecast.py`), combines and exports the Hub file
(`export.py`), then draws the interval PDFs (`intervals.py`) and the peer comparison
(`peers.py`). Output: production/output/<issuance>/<release name>/.

`record` keeps what was submitted, after the Hub PR is pushed, in production/submissions/<reference date>/
(FluSight) or <reference date>/<hub>/ (other Hubs): the CSV and its Parquet copy (renamed with
`--as` when the Hub file name differs), its export record, the interval PDFs and the peer
comparison PDF, in production/submissions/<reference date>/ (`--superseded`: its
superseded/ subfolder, for a file that was replaced). The PDFs are drawn from the local
Hub clone, so refresh it before submitting and record right after.
"""
import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from .forecast import read_release, forecast_release
from .export import export
from .hubs import HUBS


def run(argv):
    p = argparse.ArgumentParser(prog='python -m chromantis.production run')
    p.add_argument('--release', type=Path, required=True)
    p.add_argument('--dataset', required=True, help='Operational panel.npz')
    p.add_argument('--issuance', required=True, help='Wednesday issuance, e.g. 2026-10-14')
    p.add_argument('--out', type=Path, help='Default: production/output/<issuance>/<release name>')
    p.add_argument('--hub', type=Path, help="Local Hub clone (default: the release Hub's clone in hubs.py)")
    p.add_argument('--samples', action='store_true', help='Also export sampled trajectories (Hubs accepting them: RSV)')
    p.add_argument('--device', default='cpu')
    p.add_argument('--jobs', type=int, default=4)
    p.add_argument('--compare-csv', nargs='*', type=Path, default=[], help='Additional same-week local candidates in the peer comparison')
    p.add_argument('--no-plots', action='store_true')
    p.add_argument('--no-pending', action='store_true', help="Peer comparison without the Hub's open pull requests")
    args = p.parse_args(argv)
    release = read_release(args.release)
    args.hub = args.hub or Path(HUBS[release['hub']]['clone'])
    out = args.out or Path('production/output') / args.issuance / release['name']
    members = forecast_release(release, args.dataset, args.issuance, out / 'forecasts', args.device, args.jobs)
    csv = export(release, members, args.hub, out, samples=args.samples)
    if not args.no_plots:
        from . import intervals, peers
        intervals.main([str(csv), '--hub', str(args.hub)])
        peers.main([str(csv), *map(str, args.compare_csv), '--hub', str(args.hub), *([] if args.no_pending else ['--pending'])])
    print(csv)


def record(argv):
    p = argparse.ArgumentParser(prog='python -m chromantis.production record')
    p.add_argument('csv', type=Path, help='The submitted file')
    p.add_argument('--as', dest='name', help='File name used on the Hub, when it differs')
    p.add_argument('--superseded', action='store_true', help='A file that was replaced by a later one')
    p.add_argument('--hub', type=Path, help="Local Hub clone (default: the clone of the CSV's Hub)")
    p.add_argument('--hub-ref', default='HEAD', help='Hub commit for history and peers (default: the local clone)')
    args = p.parse_args(argv)
    from . import intervals, peers
    from .hubs import clone, hub_of
    import pandas as pd
    targets = pd.read_csv(args.csv, usecols=['target']).target.unique()
    args.hub = clone(args.hub, targets)
    name = args.name or args.csv.name
    reference = name[:10]
    # FluSight files sit directly in <reference>/ (the original layout); other Hubs in <reference>/<hub>/.
    hub = hub_of(targets)
    folder = Path('production/submissions') / reference / ('' if hub == 'flusight' else hub) / ('superseded' if args.superseded else '')
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    if target.exists() and target.read_bytes() != args.csv.read_bytes():
        raise ValueError(f'{target} exists with different content')
    shutil.copy2(args.csv, target)
    if args.csv.with_suffix('.json').exists():
        shutil.copy2(args.csv.with_suffix('.json'), target.with_suffix('.json'))
    if args.csv.with_suffix('.parquet').exists():
        shutil.copy2(args.csv.with_suffix('.parquet'), target.with_suffix('.parquet'))
    intervals.main([str(target), '--hub', str(args.hub)])
    with tempfile.TemporaryDirectory() as scratch:
        peers.main([str(target), '--hub', str(args.hub), '--hub-ref', args.hub_ref, '--out', scratch, '--pending'])
        from .hubs import comparison_name
        name = comparison_name(target.stem, targets)
        shutil.copy2(Path(scratch) / f'{name}.pdf', folder / f'{name}.pdf')
        shutil.copy2(Path(scratch) / 'manifest.json', folder / f'{name}.json')
    print('\n'.join(sorted(str(f) for f in folder.glob(f'{target.stem}*'))))


def main():
    commands = {'run': run, 'record': record}
    from . import intervals, peers, diff
    commands.update(intervals=intervals.main, peers=peers.main, diff=diff.main)
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        raise SystemExit(__doc__)
    commands[sys.argv[1]](sys.argv[2:])


if __name__ == '__main__':
    main()

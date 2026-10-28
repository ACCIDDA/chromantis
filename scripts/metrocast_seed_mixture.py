"""Equal-weight mixtures of intact draws from independently fitted seeds."""
from collections import defaultdict
from datetime import date, timedelta

import numpy as np
import pandas as pd

from chromantis.evaluation.standard import quantile_scores

KEY = ['reference_date', 'target_end_date', 'location', 'horizon']
LEVELS = np.array([.025, .05, .1, .25, .5, .75, .9, .95, .975])


def has_samples(path):
    if not path.exists():
        return False
    with np.load(path) as data:
        return 'samples' in data.files


def combine(paths, horizons=4, unit='proportion'):
    """Concatenate whole trajectories; assert identical tasks, truth and draw counts."""
    assert unit in {'proportion', 'count'}
    base, pieces = None, []
    for path in paths:
        with np.load(path) as data:
            metadata = {k: data[k] for k in
                        ('context_end', 'target_dates', 'locations', 'truth', 'mask')}
            draws = data['samples'][:, :, :horizons, 0, :].copy()
        assert np.isfinite(draws).all() and (draws >= 0).all()
        if unit == 'proportion':
            assert (draws <= 1).all()
        if base is None:
            base = metadata
        else:
            for key in base:
                if base[key].dtype.kind in 'f':
                    assert np.array_equal(base[key], metadata[key], equal_nan=True), key
                else:
                    assert np.array_equal(base[key], metadata[key]), key
            assert draws.shape == pieces[0].shape, 'Each seed must contribute equal draw counts'
        pieces.append(draws)
    assert pieces
    return base, np.concatenate(pieces, axis=1)


def peak_diagnostics(samples, truth, mask, target_dates, end):
    """Score intact-path maxima and first peak week on complete observed season windows.

    samples [origin, draw, week, location]; truth/mask [origin, week, location].
    Missing interior weeks exclude an origin/location, rather than hiding a peak.
    """
    from chromantis.evaluation.quantiles import LEVELS as levels

    samples = np.asarray(samples)
    truth, mask = np.asarray(truth), np.asarray(mask, dtype=bool)
    dates = np.asarray(target_dates).astype(str)
    assert samples.ndim == 4 and samples.shape[0:1] + samples.shape[2:] == truth.shape
    assert mask.shape == truth.shape and dates.shape == truth.shape[:2]
    assert np.isfinite(samples).all()
    window = dates <= end
    complete = ((mask | ~window[..., None]).all(axis=1)
                & window.any(axis=1)[:, None])
    assert np.isfinite(truth[mask & window[..., None]]).all()
    # Use the same date window in draws and observations; first argmax breaks ties.
    x = np.where(window[:, None, :, None], samples, -np.inf)
    y = np.where(window[..., None] & mask, truth, -np.inf)
    results = []
    for metric, draws, observed, factor in [
        ('Peak size WIS percentage points', x.max(axis=2), y.max(axis=1), 100),
        ('Peak timing WIS weeks', x.argmax(axis=2).astype(float),
         y.argmax(axis=1).astype(float), 1),
    ]:
        # Incomplete windows have no score and cannot enter quantile_score math.
        values = np.zeros(complete.shape)
        if complete.any():
            q = np.quantile(draws, levels, axis=1)
            values[complete] = quantile_scores(
                q[:, complete].T, observed[complete], levels).wis.to_numpy()
        count = complete.sum(axis=0)
        loc = values.sum(axis=0) / np.maximum(count, 1)
        results.append(dict(
            metric=metric, horizons='observed-season-window',
            value=float(loc[count > 0].mean() * factor) if (count > 0).any() else float('nan'),
            cells=int(complete.sum()), locations=int((count > 0).sum()),
            peak_definition='Maximum over forecast dates through season end; earliest week wins ties; only complete observed origin/location windows',
        ))
    return results


def score_mixtures(entries, ensemble, expected_seeds, folder, training_seasons, evaluation_season):
    groups = defaultdict(list)
    for record, path, view in entries:
        groups[(record['name'], record['scenario'], view)].append((record['seed'], path))
    rows = []
    for (name, scenario, view), members in groups.items():
        seeds = [s for s, _ in members]
        if set(seeds) != set(expected_seeds):
            continue
        assert len(seeds) == len(set(seeds)), 'Duplicate seed in mixture'
        metadata, samples = combine([p for _, p in sorted(members)])
        # Quantiles of the pooled draws, never averages of seed quantiles or WIS.
        q = np.quantile(samples, LEVELS, axis=1)
        n, h, l = q.shape[1:]
        refs = [(date.fromisoformat(str(v)) + timedelta(days=7)).isoformat()
                for v in metadata['context_end']]
        pred = pd.DataFrame(dict(
            reference_date=np.repeat(refs, h*l),
            target_end_date=np.repeat(metadata['target_dates'][:, :h].reshape(-1), l),
            location=np.tile(metadata['locations'], n*h),
            horizon=np.tile(np.repeat(np.arange(h), l), n),
            observed=metadata['truth'][:, :h, 0, :].reshape(-1),
            available=metadata['mask'][:, :h, 0, :].reshape(-1)))
        qcols = [f'q{x:g}' for x in LEVELS]
        pred[qcols] = q.reshape(len(LEVELS), -1).T
        matched = ensemble.merge(pred[pred.available], on=KEY, validate='one_to_one')
        assert len(matched)
        y = matched.observed.to_numpy()
        ours = quantile_scores(matched[qcols].to_numpy(), y, LEVELS).wis.to_numpy()
        theirs = quantile_scores(
            matched[[f'ensemble_q{x:g}' for x in LEVELS]].to_numpy()/100, y, LEVELS).wis.to_numpy()
        cells = matched[KEY].assign(model_wis=ours, ensemble_wis=theirs)
        loc = cells.groupby('location')[['model_wis', 'ensemble_wis']].sum()
        rows.append(dict(name=name, scenario=scenario, evaluation_inputs=view,
                         aggregation='equal-weight intact-draw seed mixture',
                         seeds=';'.join(map(str, sorted(seeds))), draws_per_origin=samples.shape[1],
                         training_seasons=training_seasons, evaluation_season=evaluation_season,
                         labels='future local flu ED proportions', tasks=len(cells), locations=len(loc),
                         model_wis_percentage_points=float(ours.mean()*100),
                         ensemble_wis_percentage_points=float(theirs.mean()*100),
                         location_mean_wis_ratio=float((loc.model_wis/loc.ensemble_wis).mean()),
                         pooled_wis_ratio=float(ours.mean()/theirs.mean())))
        destination = folder/'seed-mixtures'/name/view
        destination.mkdir(parents=True, exist_ok=True)
        cells.to_parquet(destination/'ensemble-cells.parquet', index=False)
    result = pd.DataFrame(rows)
    result.to_csv(folder/'metrocast-ensemble-seed-mixtures.csv', index=False)
    if rows:
        print(result[['name', 'evaluation_inputs', 'location_mean_wis_ratio', 'tasks']].to_string(index=False))
    return result


def score_path_mixtures(entries, expected_seeds, folder, training_seasons, evaluation_season, end):
    import torch
    from chromantis.experiment.training import path_scores
    from chromantis.evaluation.quantiles import LEVELS as path_levels

    groups = defaultdict(list)
    for record, path in entries:
        groups[(record['name'], record['scenario'])].append((record['seed'], path))
    rows = []
    for (name, scenario), members in groups.items():
        seeds = [s for s, _ in members]
        if set(seeds) != set(expected_seeds):
            continue
        assert len(seeds) == len(set(seeds))
        metadata, samples = combine([p for _, p in sorted(members)], horizons=34)
        y = metadata['truth'][:, :34, 0, :]
        mask = metadata['mask'][:, :34, 0, :].astype(bool)
        mask &= (metadata['target_dates'][:, :34].astype(str) <= end)[..., None]
        q = np.quantile(samples, path_levels, axis=1)
        wis = quantile_scores(q.reshape(len(path_levels), -1).T, y.reshape(-1),
                              path_levels).wis.to_numpy().reshape(y.shape)
        base = dict(name=name, scenario=scenario, seeds=';'.join(map(str, sorted(seeds))),
                    aggregation='equal-weight intact-draw seed mixture', draws_per_origin=samples.shape[1],
                    training_seasons=training_seasons, evaluation_season=evaluation_season,
                    evaluation_inputs='latest revised histories', labels='future local flu ED proportions',
                    ensemble_comparison=False)
        rows.extend(dict(base, **row) for row in peak_diagnostics(
            samples, y, mask, metadata['target_dates'][:, :34], end))
        for label, start, stop in [('0-3', 0, 4), ('4-12', 4, 13), ('13-25', 13, 26),
                                   ('26-33', 26, 34), ('0-33', 0, 34)]:
            present = mask[:, start:stop]
            count = present.sum((0, 1))
            per_location = np.where(present, wis[:, start:stop], 0).sum((0, 1))/np.maximum(count, 1)
            rows.append(dict(base, metric='WIS percentage points', horizons=label,
                             value=float(per_location[count > 0].mean()*100)))
        # Bound pairwise path-distance memory while retaining every pooled draw.
        energy = np.zeros((y.shape[0], y.shape[-1]))
        for start in range(0, y.shape[-1], 8):
            stop = start+8
            values, _ = path_scores(
                torch.from_numpy(samples[..., start:stop].transpose(1, 0, 2, 3).copy()),
                torch.from_numpy(y[..., start:stop]),
                torch.from_numpy(mask[..., start:stop]), log_counts=False)
            energy[:, start:stop] = values.numpy()
        present = mask.any(axis=1)
        count = present.sum(0)
        per_location = (energy*present).sum(0)/np.maximum(count, 1)
        rows.append(dict(base, metric='Path energy percentage points', horizons='0-33',
                         value=float(per_location[count > 0].mean()*100)))
    result = pd.DataFrame(rows)
    destination = 'confirmation-seed-mixture-long-horizon.csv' if evaluation_season == '2025-2026' else 'development-seed-mixture-long-horizon.csv'
    result.to_csv(folder/destination, index=False)
    return result

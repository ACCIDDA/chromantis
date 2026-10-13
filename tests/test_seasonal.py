import json

import numpy as np

from chromantis.seasonal import FLOOR, HISTORY_WEEKS, peaks, score, window_weeks


def test_peaks_take_the_window_maximum_of_each_trajectory():
    paths = np.array([[9, 1, 5, 2], [9, 1, 2, 7], [9, 4, 3, 1]], float)  # week 0 is before the window
    pmf, quantiles = peaks(paths, 1)
    assert pmf.tolist() == [1 / 3, 1 / 3, 1 / 3]
    assert 4 <= quantiles[0] < 4.1 and 6.9 < quantiles[-1] <= 7 and np.isclose(quantiles[11], 5)  # peak draws 5, 7, 4


def test_flusight_window_is_epiweeks_40_to_21():
    weeks = window_weeks(2026, (40, 21))[HISTORY_WEEKS:]
    assert weeks[0] == '2026-10-10' and weeks[-1] == '2027-05-29' and len(weeks) == 34


def test_log_score_floors_probability_and_skips_tied_peaks(tmp_path):
    w = 5
    truth = np.full((HISTORY_WEEKS + w, 2), 1.)
    truth[HISTORY_WEEKS + 2, 0] = 10                       # location A: single peak in week 2
    truth[HISTORY_WEEKS + 1, 1] = truth[HISTORY_WEEKS + 3, 1] = 10  # location B: tied peak
    pmf = np.zeros((1, 2, w)); pmf[0, :, 0] = 1            # all mass on week 0: true week gets 0
    np.savez(tmp_path / 'peaks_2024-2025.npz', pmf=pmf, quantiles=np.full((1, 2, 23), 10.), truth=truth,
             weeks=np.array([str(i) for i in range(HISTORY_WEEKS + w)]), origins=np.array(['2024-10-05']),
             locations=np.array(['AA', 'BB']))
    (tmp_path / 'manifest.json').write_text(json.dumps(dict(folds=['2024-2025'])))
    t = score(tmp_path).set_index('location')
    assert np.isclose(t.loc['AA', 'peak_week_log_score'], -np.log(FLOOR))
    assert np.isnan(t.loc['BB', 'peak_week_log_score'])
    assert np.isclose(t.loc['AA', 'peak_wis_log'], 0)


def test_path_scores_are_zero_for_exact_draws_and_ignore_unobserved_weeks():
    import torch
    from chromantis.experiment.training import path_scores
    truth = torch.tensor([[[10.], [50.], [20.], [5.]]])            # [N=1, H=4, L=1]
    mask = torch.tensor([[[True], [True], [True], [False]]])
    exact = truth.expand(3, -1, -1, -1).clone()
    exact[:, 0, 3] = 999                                             # unobserved week: must not matter
    energy, peak = path_scores(exact, truth, mask)
    assert torch.allclose(energy, torch.zeros(1, 1), atol=1e-5) and torch.allclose(peak, torch.zeros(1, 1), atol=1e-5)
    shifted = exact.clone()
    shifted[:, 0, 1] = np.expm1(np.log1p(50.) + 1)                  # +1 on the log scale in one observed week
    energy, peak = path_scores(shifted, truth, mask)
    assert abs(energy.item() - 1 / np.sqrt(3)) < 1e-4
    assert peak.item() > 0.9                                         # peak size is off by one log unit


def test_fair_crps_draws_matches_the_cell_estimator():
    import torch
    from chromantis.experiment.training import fair_crps_draws
    from chromantis.model.network import fair_crps_cells
    draws = torch.randn(16, 2, 3, 1, 4)
    truth = torch.randn(2, 3, 1, 4)
    assert torch.allclose(fair_crps_draws(draws, truth), fair_crps_cells(draws, truth, torch.ones_like(truth)), atol=1e-6)


def test_peak_log_score_averages_draw_probabilities_and_ignores_missing_or_tied_truth():
    import torch
    from chromantis.experiment.training import peak_log_scores
    samples = torch.tensor([[[[9.], [0.], [999.]]], [[[0.], [9.], [999.]]]], requires_grad=True)
    truth = torch.tensor([[[9.], [0.], [999.]]])
    mask = torch.tensor([[[True], [True], [False]]])
    loss = peak_log_scores(samples, truth, mask)
    assert torch.allclose(loss, torch.tensor([[np.log(2.)]], dtype=loss.dtype), atol=1e-6)
    loss.sum().backward()
    assert torch.isfinite(samples.grad).all()
    assert (samples.grad[:, :, 2] == 0).all()
    assert peak_log_scores(samples, torch.zeros_like(truth), mask).item() == 0
    assert peak_log_scores(samples, truth, torch.zeros_like(mask)).item() == 0


def test_reported_peak_inputs_remove_final_truth_fills():
    from chromantis.seasonal import without_truth_fallback
    episode = dict(values=np.array([[[999., 7.]]]), available=np.ones((1, 1, 2), bool),
                   known_final=np.ones((1, 1, 2), bool), filled=np.array([[[True, False]]]),
                   covariates=np.array([[[[999., 8.], [1., 1.]]]]),
                   covariates_filled=np.array([[[True, False]]]))
    result = without_truth_fallback(episode)
    assert result['values'].tolist() == [[[0., 7.]]]
    assert result['available'].tolist() == [[[False, True]]]
    assert result['covariates'].tolist() == [[[[0., 8.], [0., 1.]]]]


def test_reported_peak_history_uses_wednesday_vintage_without_truth():
    from chromantis.seasonal import SeasonPanel
    p = object.__new__(SeasonPanel)
    p.target_index = 0
    p.index = {'2025-01-04': 0, '2025-01-11': 1}
    p.issuances = {'2025-01-08': 0}
    p.panel = dict(locations=np.array(['AA']), asof_targets=np.array([[[[7.]], [[np.nan]]]]))
    values = p.reported_curve(['2025-01-04', '2025-01-11'], ['AA'], '2025-01-11')
    assert values[0, 0] == 7 and np.isnan(values[1, 0])
    assert np.isnan(p.reported_curve(['2025-01-04'], ['AA'], '2025-01-18')).all()

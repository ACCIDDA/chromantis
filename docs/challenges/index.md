# Challenges

Chromantis takes part in five forecasting hubs. Each target family has its own page with the
Hub's rules, the model currently submitted, how it was chosen and its submission log:

| Challenge | Target | Status | Latest submission |
|---|---|---|---|
| [FluSight weekly](flusight-weekly.md) | Flu admissions and ED share, states/DC/US, horizons 0–3 | Submitting | 7 November 2026, Bes with half-strength correction trees, PR 4011 open |
| [FluSight season peak](flusight-peak.md) | Flu peak size and peak week, states/DC/US | Submitting | 7 November 2026, Peak8, same file |
| [RSV Forecast Hub](rsv.md) | RSV admissions and ED share, states/DC/US, horizons 0–3 | Submitting | 21 November 2026, four-recipe mixture with half-strength correction trees, PR 738 merged |
| [Flu MetroCast](metrocast.md) | Local flu ED percentage, 103 locations, horizons 0–3 plus full season | Submitting | 7 November 2026, spliced 4-week and full-season models, PR 645 open |
| [COVID-19 Forecast Hub](covid.md) | COVID admissions and ED share, states/DC/US, horizons 0–3 | Submitting | 21 November 2026, four-recipe mixture, PR 2068 merged |
| [BDBV Modeling Hub (Ebola)](ebola.md) | DRC confirmed Ebola cases by onset week, country/provinces/health zones | Submitting | 14 November 2026, nowcast + 12-fit ensemble, PR 117 open |

The public model name is **ACCIDDA-Chromantis** on every Hub. It was submitted as
ACCIDDA-EpiLoom for the 10 October 2026 FluSight round and renamed on the Hub on 8 October
2026 (PR 3774); the file contents did not change. Hub metadata changes are deferred until the
recipe is settled, as decided on 8 October 2026.

## All submissions

| Hub | Reference date | Recipe | Recorded status |
| --- | --- | --- | --- |
| FluSight | 7 November 2026 | Bes with correction trees at half strength `bes-cs050` (the 10 fits of `bes-20261010`) weekly targets + Peak8 season-peak targets (6 fits) | PR 4011 opened 4 November with full-strength Bes, file replaced before the deadline |
| FluSight | 31 October 2026 | B7 refit `b7-20261009` weekly targets (30 fits) + Peak8 season-peak targets (6 fits) | PR 3943 merged 28 October |
| FluSight | 24 October 2026 | B7 refit `b7-20261009` weekly targets (30 fits) + Peak8 season-peak targets (6 fits) | PR 3895 merged 21 October |
| FluSight | 17 October 2026 | Bes weekly targets (10 fits) + Peak8 season-peak targets (6 fits) | Weekly file merged (PR 3804); peak targets added in PR 3815, merged 14 October |
| FluSight | 10 October 2026 | Three-recipe B7 mixture, 30 fits (submitted as ACCIDDA-EpiLoom) | Merged after the deadline; replaced the on-time eight-recipe forecast |
| Flu MetroCast | 7 November 2026 | Same two models as 31 October, same splice, cut at 12 June 2027 | PR 645 opened 4 November, validation passed |
| Flu MetroCast | 31 October 2026 | Same two models as 24 October, same splice | PR 629 merged 29 October |
| Flu MetroCast | 24 October 2026 | Season-CV winner `r010_c08` (5 fits) for horizons 0-3, spliced with full-season `full_season_finalist_1` (5 fits) to 12 June | First MetroCast submission; PR 609 opened after the deadline, merged 22 October |
| RSV | 21 November 2026 | Same 40 fits, trees at half strength `rsv-four-cs050` | PR 738 merged 18 November |
| RSV | 14 November 2026 | Same 40 fits, trees at half strength `rsv-four-cs050` | PR 721, opened 12 November after the window closed, merged by hand 12 November |
| RSV | 7 November 2026 | Four-recipe mixture rsv-four-20261014, 40 fits | PR 694 merged 4 November |
| RSV | 31 October 2026 | Four-recipe mixture rsv-four-20261014, 40 fits | PR 673 merged 28 October |
| RSV | 24 October 2026 | Four-recipe mixture rsv-four-20261014, 40 fits | PR 657 merged 21 October |
| RSV | 17 October 2026 | Four-recipe mixture rsv-four-20261014, 40 fits | First RSV submission; PR 641 merged 15 October |
| BDBV (Ebola) | 14 November 2026 | Same nowcast code and three recipes × four seeds, trained through 3 October, 8 November release | PR 117 opened 10 November, validation passed |
| BDBV (Ebola) | 7 November 2026 | Observed-onset nowcast + the same three recipes × four seeds, trained through 26 September | PR 96 merged 4 November |
| BDBV (Ebola) | 31 October 2026 | Negative-binomial nowcast + three recipes × four seeds (12 fits) | First submission; PR 71 merged 27 October |
| COVID-19 | 21 November 2026 | Four-recipe mixture covid-gru-four-candidate-20261103, 40 fits | PR 2068 merged 18 November |
| COVID-19 | 14 November 2026 | Four-recipe mixture covid-gru-four-candidate-20261103, 40 fits | PR 2049, opened 12 November after the window closed, merged by hand 12 November |
| COVID-19 | 7 November 2026 | Four-recipe mixture covid-gru-four-candidate-20261103, 40 fits | First COVID submission; metadata PR 2017 and forecast PR 2018 merged 4 November |

## Recording a submission

Each dated entry on a challenge page must state: the recipe and its exact fitted
checkpoints, the training seasons and training-input treatments, the prediction labels, the
operational input panel (with hash), the submitted file hash, and the Hub PR, validation and
merge record. Future recipes receive new entries; a change of model does not rename or
overwrite the submission history.

The local record of each issuance is `production/submissions/<reference date>/` (FluSight)
or `<reference date>/<hub>/` (other Hubs): the submitted file under its Hub name, its export
record (`.json`: release, sources, hashes), the interval PDFs and the peer-comparison PDF
drawn at submission time (`python -m chromantis.production record`); replaced versions are
in its `superseded/` subfolder. From 31 October, `production/submissions/<reference date>/shared-pdfs/`
collects every PDF of the submitted files in one folder for sharing. The Ebola record is
not yet in `production/submissions/` (see its page).

On 14 October 2026 (evening) every recorded peer comparison was redrawn to show every
same-week Hub model individually, plus open-PR submissions: FluSight Hub `50898478` (55
models for 10 October, 39 for 17 October) and RSV Hub `8dd45ebb` (12 models). The earlier
versions showed six fixed peers and a band over the rest. The 17 October flu comparison does
not repeat the model description because the submitted CSV now includes peak targets and no
longer matches its weekly-only export record.

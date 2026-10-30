# What we learned

These are the main lessons from building and running Chromantis, in plain language, each with
a link to its evidence. Most are about influenza, where the most work was done.

**How sure are we?** Apart from the [live results](#live-results-so-far) at the end, every
number comes from a retrospective comparison on past seasons. The same seasons were reused to
choose the models, so these are not untouched tests and tend to flatter the winners.

**How to read the scores.** WIS (weighted interval score) measures the error of a forecast
that comes with uncertainty intervals; **lower is better**. *Relative WIS* divides it by the
score of a reference on the same tasks, usually the Hub ensemble, so 1 means equal to the
ensemble and 0.8 about 20% lower error. Scores from different studies are not comparable.

**The two-season setup.** Unless a finding says otherwise, each model learned the finalized
future values of flu admissions and ED share for the next four weeks, and was fitted twice:
trained on 2022–23, 2023–24 and 2024–25 and evaluated on 2025–26, then trained on 2022–23,
2023–24 and 2025–26 and evaluated on 2024–25 (so that fold trains on a later season). It was
evaluated on the reports visible at each Wednesday deadline, with finalized values where no
report was archived. The *composite* score combines relative WIS over admissions (weight 1)
and ED share (weight 0.5), with 80% of the weight on states and DC and 20% on the US; 2024–25
has admissions only.

**Recipe A** and **Recipe B** are the two leading flu models of early October. A is a width-96
network that samples forecast paths, reads flu histories and national Kinsa, and trains on
artificially degraded histories corrected by trees. B is a width-96 network that predicts 23
quantiles directly, reads flu histories only, exchanges information with neighbouring states,
and trains on artificially degraded histories while also learning the final values of the
last four weeks.

## Late and revised reports

### Correcting the two newest reported weeks helps a little; correcting more does not

Recent weeks are reported low and revised up later. A model called C1 (separate networks per
pathogen, no covariates), trained on finalized histories of 2022–23 to 2024–25, scored 0.9285
relative to the Hub ensemble on 2025–26 reports, over flu, COVID and RSV. The same saved model, with half its forecast
samples read from admission histories corrected by small trees, scored 0.9183: a 1.1% gain, in
all three seeds. That is a real but small gain, not a solution to reporting delay.

Longer corrections did not help. Retrained in the two-season setup, Recipe B's composite was
0.7956 correcting two weeks and 0.7972 correcting eight. Recipe A went from 0.7799 to 0.9495,
though that change also retrains it on differently corrected histories. Every respiratory model
that corrects recent weeks now corrects two.

Evidence: [end-of-run summary](experiments/overnight-b2-results-20261005.md),
[flu study](experiments/b4-flu-study-20261006/index.md).

### Training on histories that look like early reports helps, depending on the model

A model trained only on finalized histories sees cleaner data than it will ever read in real
use. The first test did not support changing this: C1 scored 0.9398 on 2025–26 trained on
finalized histories and 0.9476 with half its training examples given half-strength reporting
errors.

Later tests were kinder. In the pilot, adding errors to the older training seasons and using
archived reports in the latest one took a two-season score over flu, COVID and RSV from 1.0656
to 0.9347 for separate pathogen networks and from 1.0156 to 0.9388 for separate target
networks. Much of that gain came from COVID admissions in 2024–25, not flu. On new seeds, in
the two-season setup, training on actual archived reports took Recipe B from 0.870 to 0.815
and left Recipe A about the same (0.797 to 0.795). All submitted flu and RSV models now train
on histories with reporting errors, artificial or archived; MetroCast and Ebola models do not.

Evidence: [end-of-run summary](experiments/overnight-b2-results-20261005.md),
[flu study](experiments/b4-flu-study-20261006/index.md),
[B4.polish and B5](experiments/b4-polish-b5-20261007/index.md).

### A correction can be too strong, and live reports exposed one

Bes is a single flu recipe (width-256, 23 quantiles, reporting errors at 1.5 times their
measured strength, trained on 2022–23 to 2025–26), submitted for 17 October. Its trees raised
the newest admission week 1.131–1.141 times, summed over states and DC. The B7 mixture's trees
raised it 1.095–1.104 times, and those weeks have so far been revised up 1.054–1.070 times.
Bes's US median for the week ending 17 October was 5,762 against 4,698 in the first report.

This is one week, and it conflicts with the retrospective record: over the held-out seasons of
the tree search, Bes scored better than B7 (state and DC log-admission WIS 0.2895 against
0.2976). Going back to B7 was a judgment that the correction looked too strong, not a proof.

Evidence: 24 and 31 October entries on [FluSight weekly](challenges/flusight-weekly.md#submission-log).

## Extra data

### More data is not automatically better

In a sweep of 309 configurations in the two-season splits, trained and evaluated on finalized
inputs and forecasting flu, COVID and RSV, adding every available covariate made scores worse
in 26 of 30 matched comparisons, although the uncertainty interval included no change. Outpatient claims alone hurt all three model families tested.

Other pathogens did not help flu either. Across 150 matched flu recipes retrained in the
two-season setup, adding COVID histories worsened the median composite by 4.38% and adding RSV
by 0.73%. This is not a general rule: the RSV search chose a mixture in which three of four
models read flu and COVID histories too. Pretraining on pre-2022 influenza-like illness data
gave at most a small gain (−1.1%, not significant, across 400 variations of the leading
recipes); one submitted flu model uses it. No submitted model reads wastewater.

Evidence: [B2 covariate sweep](experiments/b-2-t0/index.md),
[flu study](experiments/b4-flu-study-20261006/index.md),
[B4.polish and B5](experiments/b4-polish-b5-20261007/index.md).

### Kinsa helps one model, hurts another, and is a risk

Kinsa is a national influenza-like illness series. Retrained in the two-season setup with two
seeds, Recipe A's composite was 0.7799 with Kinsa and 0.9178 without, while Recipe B's was
0.7956 without and 1.0051 with. Yet on new seeds, Recipe A scored better when Kinsa was hidden
at evaluation (0.787 against 0.829, all five seeds), entirely because of 2024–25, and its ED
share forecasts got worse. The submitted flu mixture has two recipes with Kinsa and one
without.

Evidence: [flu study](experiments/b4-flu-study-20261006/index.md),
[B4.polish and B5](experiments/b4-polish-b5-20261007/index.md).

## Models

### Small, plain networks keep beating fancier ones

In the 309-configuration sweep, a multiscale convolutional network did worse than a plain
pathogen network in 90 of 103 matched comparisons, and attention and gated pooling did worse
than no spatial sharing in 11 of 12 each. In the 600-configuration flu search, the best shared
architectures scored 0.9155 and 1.0431 against 0.7799 for Recipe A, though these are the best
of different searches, not a controlled comparison. Autoencoder heads, masking, bottlenecks
and pretraining on extra series, tested on 24–26 October, did not help the weekly flu models.

Evidence: [B2 covariate sweep](experiments/b-2-t0/index.md),
[flu study](experiments/b4-flu-study-20261006/index.md),
[autoencoders and conditional VAEs](experiments/autoenc-20261024/index.md).

### Much of the difference between models is luck

Retraining with new random seeds is the best test of a leaderboard. In the two-season setup,
Recipe A went from 0.780 to 0.829 and Recipe B from 0.796 to 0.857 on new seeds, with
seed-to-seed spread of 0.04–0.10. The best of 400 random variations scored 0.768–0.780 and fell
to 0.797–1.078 when retrained. Small score differences therefore mean little, which is why
submitted models pool up to ten seeds per recipe and why seeds are never picked by their score.

Evidence: [B4.polish and B5](experiments/b4-polish-b5-20261007/index.md),
[saved ensembles](experiments/b6-saved-ensembles-20261007/index.md).

### Mixing models makes results steadier

In the two-season setup, single-seed pairs of Recipes A and B scored 0.805–0.831, while Recipe
A alone ranged 0.783–0.891. The mixture's best case is worse than A's, but its worst case is much
better. The submitted flu weekly and RSV forecasts are mixtures.

Evidence: [B4.polish and B5](experiments/b4-polish-b5-20261007/index.md).

### More training seasons help

With seeds 44–48, Recipe A scored 0.973 and Recipe B 0.986 when trained only on the two seasons
before the evaluated one, against 0.829 and 0.857 in the two-season setup, which trains on
three seasons, including a later one for the 2024–25 fold. Submitted models therefore train on all four completed seasons, with none held out, so
those exact fits have no retrospective score of their own.

Evidence: [B4.polish and B5](experiments/b4-polish-b5-20261007/index.md).

### Which model is "best" depends on the score

Counting admissions and counting them on a log scale reward different forecasts, because the
natural scale is dominated by large states. Of 600 flu configurations trained on 2022–23 to
2024–25 and evaluated on 2025–26 reports, 204 beat Google's FluSight model on counts and only
one on log counts, reading reports as published (174 and 11 with the newest weeks corrected).
In a separate comparison of two flu mixtures over 2024–25 and 2025–26, one was better on log
admissions (WIS 0.2673 against 0.2742) and the other on counts (60.67 against 64.50). Choosing
is a choice of goal: one review recommended the wide System2 mixture, and a later one preferred
B7, modestly, if season-long log admissions are the priority.

Evidence: [B4 versus Google](experiments/b4-google-check-20261006.md),
[B7 versus System2](experiments/b7-submission-comparison-20261007/index.md),
[why B7 replaced System2](experiments/submission-choice-review-20261007.md).

## Season peak

### Peak size is easier than peak timing

Peak8 is the submitted peak model. With each season held out in turn and replayed on archived
Wednesday reports, over 862 state and DC tasks in 2024–25 and 2025–26, it beat the FluSight ensemble on peak size (log-admission WIS
0.306 against 0.523) and lost to it on peak week (negative log score 2.81 against 2.58; lower
is better for both). Rolling Recipe A forward four weeks at a time gave timing errors in both directions
(3–7 weeks late in 2025–26, early in 2024–25), so no constant shift fixes it. A learned random
input (a conditional VAE) improved the peak-week score of the peak model from 2.854 to 2.700
across eight seeds, still behind the ensemble; it has not been submitted.

Evidence: [autoregressive rollout](experiments/peak-rollout-20261007/index.md),
[autoencoders and conditional VAEs](experiments/autoenc-20261024/index.md),
[FluSight season peak](challenges/flusight-peak.md).

## Other challenges

### Local flu forecasts did well without any reporting correction

The MetroCast 4-week model, trained on revised local histories of the other seasons to predict
future local flu ED percentages, with no reporting errors and no correction, scored 0.82 times the MetroCast ensemble's WIS when
2025–26 was replayed on the Hub's archived data (mean over 72 locations). It was the best of
about 270 recipes, so this is optimistic. In the first live check, the week ending 24 October
fell inside the 80% interval in 76 of 90 locations and below it in 10.

Evidence: [Flu MetroCast](challenges/metrocast.md).

### A recipe that works for one disease does not simply transfer

The flu recipe families were refitted to COVID-19 in two searches. The search record says ED
and national intervals came out too narrow, and that archive gaps and the evaluation design
were unresolved, so none of the six candidates was accepted and nothing has been submitted.

Evidence: [COVID-19](challenges/covid.md).

### Ebola forecasts borrow from past outbreaks

Besides BDBV weeks, the models train on the West Africa 2014–15 and Kivu 2018–20 outbreaks. Two
lessons came from building it: a fixed completion multiplier kept health
zones reporting zero at zero, which the negative-binomial nowcast fixes, and rescoring on five
windows across outbreaks favoured a three-recipe ensemble over one recipe. No live forecast
has been scored yet.

Evidence: [BDBV (Ebola)](challenges/ebola.md), history in `scripts/ebola_project.py`.

## Live results so far

These are real forecasts, scored at Hub horizon 0 (the week unreported when issued) against
the first report for that week, over the 51 state and DC tasks. The score is mean WIS divided by the Hub
baseline's, so lower is better and 1 equals the baseline; "ensemble" is that Hub's ensemble on
the same scale. The models were all trained on 2022–23 to 2025–26. Scores come from a one-off
script, not the research scorer.

| Forecast (reference date) | Target | Chromantis | Rank | Ensemble |
|---|---|---:|---:|---:|
| FluSight, Bes (17 October) | Log admissions | 0.76 | 37 of 56 | 0.65 |
| FluSight, Bes (17 October) | ED share | 1.21 | 16 of 16 | 0.76 |
| FluSight, B7 (24 October) | Log admissions | 0.66 | 13 of 58 | 0.66 |
| FluSight, B7 (24 October) | ED share | 0.68 | 10 of 17 | 0.59 |
| RSV, four-recipe mixture (17 October) | Log admissions | 0.75 | 1 of 10 | 0.81 |
| RSV, four-recipe mixture (17 October) | ED share | 0.82 | 3 of 6 | 0.71 |
| RSV, four-recipe mixture (24 October) | Log admissions | 0.94 | 5 of 11 | 0.87 |
| RSV, four-recipe mixture (24 October) | ED share | 1.24 | 3 of 3 | 1.00 |

Two scored weeks per Hub say very little. The FluSight ED share for 24 October covers the 48
states with an observation where the baseline forecast. MetroCast and Ebola have no WIS yet.
More detail is in each challenge's [submission log](challenges/index.md).

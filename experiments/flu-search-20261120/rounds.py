"""Recipe definitions of the flu search (flu-search-20261120); writes one study file per round and problem.

Every candidate is a parent recipe plus named changes, so a child's difference from its parent is explicit.
Main study files (round-NN.json) carry no error_reference: each fold draws artificial reporting errors and real
report pairs from its own latest training season (2024-25 for the 2025-26 fold, 2025-26 for the 2024-25 fold),
so the evaluated season's reporting never trains the model. Guard files (guard-NN.json) are the same recipes with
error_reference=2025-2026, required by the prescribed 2023-24 guard problem (its default donor is 2025-26 anyway).

    python3 experiments/flu-search-20261120/rounds.py 1
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
SEEDS = list(range(44, 52))


def parse(s):
    return dict(t.split('=', 1) for t in s.split(','))


def text(d):
    return ','.join(f'{k}={v}' for k, v in d.items())


def derive(parent, drop=(), **changes):
    d = parse(parent)
    for k in drop:
        d.pop(k, None)
    d.update({k: str(v) for k, v in changes.items()})
    return text(d)


def add_covariates(recipe, *sets):
    d = parse(recipe)
    have = [] if d.get('covariate_set', 'none') == 'none' else d['covariate_set'].split('+')
    d['covariate_set'] = '+'.join(have + [s for s in sets if s not in have])
    return text(d)


# B7's three recipes as submitted (experiments/b7-folds-20261007.json), without error_reference.
A = ('history_source=artificial,history_correction=1,error_signals=targets,input_set=target,correction_weeks=2,correction_ed=1,'
     'joint_weight=0.05,correction_penalty=30.0,reporting_missingness=0,reporting_method=synchronous_phase_log,count_transform=sqrt,'
     'ed_transform=logit,loss_weights=objective,decoder_blocks=3,width=96,epochs=160,patience=25,lr=0.002,fit_partition=pathogen,'
     'covariate_encoder=summary,covariate_set=kinsa,input_normalization=b0,log_loss_weight=0.5')
B5 = ('history_source=artificial,history_correction=1,error_signals=targets,input_set=target,ili_units=flu_scaled,ili_steps=1200,'
      'correction_weeks=2,correction_ed=1,ili_training=pretrain,joint_weight=0.05,correction_penalty=30.0,reporting_missingness=0,'
      'reporting_method=synchronous_phase_log,lookback=10,count_transform=sqrt,ed_transform=logit,loss_weights=objective,width=96,'
      'epochs=160,patience=25,batch_size=16,fit_partition=pathogen,covariate_encoder=summary,signal_features=multiscale,'
      'covariate_set=kinsa,input_normalization=b0,correction_realizations=2,uncorrected_share=0.1,log_loss_weight=0.5')
B = ('history_source=artificial,reconstruction_labels=1,error_signals=targets,input_set=target,correction_weeks=2,correction_ed=1,'
     'joint_weight=0.1,correction_penalty=3.0,reporting_missingness=0,reporting_method=synchronous_phase_log,reconstruction_weeks=4,'
     'ed_transform=logit,loss_weights=objective,spatial=neighbors,decoder=quantile,width=256,epochs=240,patience=25,lr=0.0005,'
     'fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,log_loss_weight=0.5')

R = {}      # name -> recipe
PARENT = {}  # name -> parent name


def put(name, recipe, parent=None):
    if name in R:
        raise ValueError(f'duplicate {name}')
    R[name] = recipe
    if parent:
        PARENT[name] = parent


# References: B7's members and Bes.
put('ref.A', A)
put('ref.B5', B5)
put('ref.B', B)
put('ref.Bes', derive(B, reporting_strength=1.5), 'ref.B')
# Roots. Bq: B with trees learned from real archived report -> value 12 weeks later pairs.
# Bh: B's network trained on tree-corrected histories (no final-value labels, so the correction is not counted twice),
#     trees and network read hospital coverage. Ar: A with real-pair trees.
put('Bq', derive(B, corrector_examples='real'), 'ref.B')
put('Bh', derive(B, drop=('reconstruction_labels', 'reconstruction_weeks'), history_correction=1, corrector_examples='real',
                 covariate_set='hosprep', error_signals='all'), 'Bq')
put('Ar', derive(A, corrector_examples='real'), 'ref.A')


def round1_children(root):
    r = R[root]
    d = parse(r)
    kids = {
        'nat': derive(r, spatial='national_broadcast'),                     # US-only summary instead of neighbours (RSV win)
        'll1': derive(r, log_loss_weight=1.0),                               # more weight on log-scale admission loss (COVID win)
        'lb8': derive(r, lookback=8),
        'lb16': derive(r, lookback=16),
        'ili': derive(r, ili_training='pretrain', ili_units='flu_scaled', ili_steps=1200),  # pre-2022 ILI pretraining (CMU/UMass idea)
        'cw1': derive(r, correction_weeks=1),                                # trees correct only the newest week
        'esall': derive(r, error_seasons='all'),                             # errors and real pairs from every archived season
        'act50': derive(r, actual_share=0.5),                                # half of training episodes from actual archived reports
        'clab': add_covariates(r, 'clinical_lab'),                           # NREVSS clinical-lab flu positivity
        'fsurv': add_covariates(r, 'flusurv'),
        'ilinet': add_covariates(r, 'ilinet'),
        'ww': add_covariates(r, 'ww_flu'),
    }
    if d.get('encoder', 'mlp') == 'mlp' and 'decoder_blocks' not in d:
        kids['gru'] = derive(r, encoder='gru')                               # GRU encoder (COVID win)
    if 'hosprep' in d.get('covariate_set', ''):
        kids['netcov0'] = derive(r, network_coverage=0)                      # coverage for the trees only
    else:
        kids['cov'] = derive(add_covariates(r, 'hosprep'), error_signals='all')  # trees and network read hospital coverage
    if 'kinsa' in d.get('covariate_set', ''):
        rest = [s for s in d['covariate_set'].split('+') if s != 'kinsa']
        kids['nokinsa'] = derive(r, covariate_set='+'.join(rest) or 'none')
    else:
        kids['kinsa'] = add_covariates(r, 'kinsa')
    kids['tr'] = derive(r, count_transform='fourth_root' if d.get('count_transform') == 'sqrt' else 'sqrt')
    if d.get('history_correction') == '1':
        kids['noise'] = derive(r, correction_noise=0.5, correction_noise_train=1)  # sampled nowcast errors in training and forecasting
    else:
        kids['noise'] = derive(r, correction_noise=0.5)
    for k, v in kids.items():
        put(f'{root}.{k}', v, root)


ROUNDS = {}
ROUNDS[1] = dict(description='Flu search round 1 (2026-11-20): B7 references and Bes, three roots (Bq, Bh, Ar) and one-factor children '
                             '(dynamics, nowcast, covariates, ideas from the best 2024-26 Hub models).',
                 build=lambda: [round1_children(r) for r in ('Bq', 'Bh', 'Ar')])


def round2():
    # Sampled (trajectory) recipes only, aimed at the peak weakness (every model is far too low near the peak).
    # Round-1 cw1 failed (20 Nov 17:40): with only the newest week corrected, the 2025-26 fold's donor season 2024-25 has
    # no archived ED pairs at that age, so the ED tree had none. cw1a corrects admissions only (correction_ed=0).
    for root in ('Bq', 'Bh', 'Ar'):
        put(f'{root}.cw1a', derive(R[root], correction_weeks=1, correction_ed=0), root)
    put('B5r', derive(B5, corrector_examples='real'), 'ref.B5')                 # second sampled root: B5 with real-pair trees
    for root in ('Ar', 'B5r'):
        r = R[root]
        put(f'{root}.path', derive(r, path_loss_weight=1.0), root)           # energy score of each location's whole path
        put(f'{root}.peak', derive(r, peak_loss_weight=1.0), root)           # CRPS of the path peak size and soft peak week
        put(f'{root}.sum', derive(r, sum_wis_weight=0.25), root)             # WIS of the four-week sum
        put(f'{root}.local', derive(r, noise='local'), root)                 # per-location latent noise
        put(f'{root}.anchor', derive(r, growth_anchor=1), root)              # damped recent growth added to the level anchor


ROUNDS[2] = dict(description='Flu search round 2 (2026-11-20): trajectory (sampled) recipes aimed at the peak weakness: path, '
                             'peak, four-week-sum losses, per-location noise and growth anchor on Ar and on B5 with real-pair trees.',
                 build=round2)
def round3():
    # Round 1 winners (20 Nov 19:40): Bq.gru and Bq.ll1 beat Bq; Ar beats ref.A. Combine and extend.
    g = R['Bq.gru']
    put('Bq.gru.ll1', derive(g, log_loss_weight=1.0), 'Bq.gru')
    put('Bq.gru.lb8', derive(g, lookback=8), 'Bq.gru')                       # Bq.lb8 was -1.6% (level)
    put('Bq.gru.nat', derive(g, spatial='national_broadcast'), 'Bq.gru')      # the COVID leader's pairing (GRU + US summary)
    put('Bq.gru.bes', derive(g, reporting_strength=1.5), 'Bq.gru')            # Bes's stronger errors (ref.Bes -3.5%, level)
    put('Bh.gru.ll1', derive(R['Bh.gru'], log_loss_weight=1.0), 'Bh.gru')     # Bh: best October scores; does ll1 help it with GRU?
    # Sampled GRU: the GRU encoder needs the plain decoder (decoder_blocks only exists for the MLP), so a control without it.
    put('Ar.flat', derive(R['Ar'], drop=('decoder_blocks',)), 'Ar')
    put('Ar.flat.gru', derive(R['Ar.flat'], encoder='gru'), 'Ar.flat')
    put('Ar.flat.gru.w192', derive(R['Ar.flat.gru'], width=192), 'Ar.flat.gru')


ROUNDS[3] = dict(description='Flu search round 3 (2026-11-20): combinations of the round-1 winners (Bq.gru, Bq.ll1) and a '
                             'sampled GRU on Ar.', build=round3)
def round4():
    # Round 2 (20 Nov 20:40): B5r.peak and B5r.local beat B5r; sampled recipes top out near 0.313 against 0.292 for the
    # quantile Bq.gru. Give the winning recipe a sampled (trajectory) head: same training, decoder legacy (fair CRPS).
    put('Bq.smp', derive(R['Bq'], drop=('decoder',)), 'Bq')
    put('Bq.gru.smp', derive(R['Bq.gru'], drop=('decoder',)), 'Bq.gru')
    put('Bq.gru.smp.peak', derive(R['Bq.gru.smp'], peak_loss_weight=1.0), 'Bq.gru.smp')
    put('Bq.gru.smp.local', derive(R['Bq.gru.smp'], noise='local'), 'Bq.gru.smp')
    put('B5r.peak.local', derive(R['B5r.peak'], noise='local'), 'B5r.peak')


ROUNDS[4] = dict(description='Flu search round 4 (2026-11-20): sampled (trajectory) head on the winning Bq.gru recipe; '
                             'B5r peak loss + per-location noise.', build=round4)
def round5():
    # 20 Nov 22:10: single-recipe gains vanish with the 2023-24 guard and 16 seeds; the robust core is the B family and
    # Bh (best guard, ~20% better in October of both seasons). Sampled (trajectory) heads on it, and a mechanism check:
    # Bq.hc = Bq's network trained on tree-corrected histories (no final-value labels) without coverage.
    put('Bh.smp', derive(R['Bh'], drop=('decoder',)), 'Bh')
    put('Bh.smp.peak', derive(R['Bh.smp'], peak_loss_weight=1.0), 'Bh.smp')
    put('Bh.smp.local', derive(R['Bh.smp'], noise='local'), 'Bh.smp')
    put('Bq.hc', derive(R['Bq'], drop=('reconstruction_labels', 'reconstruction_weeks'), history_correction=1), 'Bq')
    put('Bq.hc.smp', derive(R['Bq.hc'], drop=('decoder',)), 'Bq.hc')


ROUNDS[5] = dict(description='Flu search round 5 (2026-11-20): sampled heads on Bh; Bq trained on corrected histories '
                             'without coverage (where does Bh\'s October gain come from?).', build=round5)
def round6():
    # 20 Nov 22:45: the sampled head on Bq is level with quantile Bq (0.2993 vs 0.3046, 8 seeds); peak loss helps the
    # sampled A/B5 recipes at 16 seeds. Same options on the sampled B-family recipe.
    put('Bq.smp.peak', derive(R['Bq.smp'], peak_loss_weight=1.0), 'Bq.smp')
    put('Bq.smp.local', derive(R['Bq.smp'], noise='local'), 'Bq.smp')
    put('Bq.smp.ll1', derive(R['Bq.smp'], log_loss_weight=1.0), 'Bq.smp')


ROUNDS[6] = dict(description='Flu search round 6 (2026-11-20): peak loss, per-location noise and log-loss 1 on the sampled '
                             'B-family recipe Bq.smp.', build=round6)
def round7():
    # 21 Nov 00:45: Bq.hc.smp (sampled, network on corrected histories, no coverage) is level with Bq on all three seasons;
    # peak loss helped every sampled recipe so far.
    put('Bq.hc.smp.peak', derive(R['Bq.hc.smp'], peak_loss_weight=1.0), 'Bq.hc.smp')
    put('Bh.smp.peak.x', derive(R['Bh.smp'], peak_loss_weight=0.5), 'Bh.smp')     # half-weight peak loss on sampled Bh


ROUNDS[7] = dict(description='Flu search round 7 (2026-11-21): peak loss on the sampled B-family recipes.', build=round7)
def round8():
    # 21 Nov 01:45: Bq.smp.ll1 (sampled Bq, log-loss weight 1) beats Bq.smp on all three seasons and is level with
    # quantile Bq on 2023-24; the strongest sampled recipe so far. Same option on the other sampled B-family recipes.
    put('Bq.hc.smp.ll1', derive(R['Bq.hc.smp'], log_loss_weight=1.0), 'Bq.hc.smp')
    put('Bh.smp.ll1', derive(R['Bh.smp'], log_loss_weight=1.0), 'Bh.smp')
    put('Bq.smp.ll1.local', derive(R['Bq.smp.ll1'], noise='local'), 'Bq.smp.ll1')


ROUNDS[8] = dict(description='Flu search round 8 (2026-11-21): log-loss weight 1 on the sampled B-family recipes.', build=round8)
def round9():
    # 21 Nov 02:00: every model and mixture is far too low near the peak (bias about -0.38 on the log scale). With four
    # training seasons the networks may learn a typical epidemic size; amplitude augmentation (training/amplitude_sd)
    # rescales each training episode's inputs and labels by exp(N(0, sd)).
    for root in ('Bq', 'Bq.hc.smp', 'Bh.smp', 'Ar.peak'):
        put(f'{root}.amp3', derive(R[root], amplitude_sd=0.3), root)
    put('Ar.peak.amp5', derive(R['Ar.peak'], amplitude_sd=0.5), 'Ar.peak')


ROUNDS[9] = dict(description='Flu search round 9 (2026-11-21): amplitude augmentation (new option amplitude_sd) on the '
                             'candidate members and on Bq.', build=round9)
def round10():
    # 21 Nov 04:35: candidates Bq.smp.ll1 + Bh.smp + Ar.peak and Bq.smp.ll1 + ref.B + Ar.peak. Lookback diversity for the
    # sampled members (OHT_JHU averages lookback windows), and Ar.peak without Kinsa (a risky national feed).
    put('Bq.smp.ll1.lb8', derive(R['Bq.smp.ll1'], lookback=8), 'Bq.smp.ll1')
    put('Bq.smp.ll1.lb16', derive(R['Bq.smp.ll1'], lookback=16), 'Bq.smp.ll1')
    put('Ar.peak.nokinsa', derive(R['Ar.peak'], covariate_set='none'), 'Ar.peak')


ROUNDS[10] = dict(description='Flu search round 10 (2026-11-21): lookback variants of Bq.smp.ll1 for mixtures; Ar.peak without Kinsa.',
                  build=round10)
def round11():
    # 21 Nov 06:45: pre-2022 ILI pretraining on the sampled B recipe (it is part of B5's design).
    put('Bq.smp.ll1.ili', derive(R['Bq.smp.ll1'], ili_training='pretrain', ili_units='flu_scaled', ili_steps=1200), 'Bq.smp.ll1')


ROUNDS[11] = dict(description='Flu search round 11 (2026-11-21): ILI pretraining on Bq.smp.ll1.', build=round11)
def round12():
    # 21 Nov 07:45: continue the loss axes that helped sampled recipes (log-loss 1 on Bq.smp, peak loss on Ar).
    put('Bq.smp.ll2', derive(R['Bq.smp'], log_loss_weight=2.0), 'Bq.smp.ll1')
    put('Bq.smp.ll1.log1p', derive(R['Bq.smp.ll1'], count_transform='log1p'), 'Bq.smp.ll1')
    put('Bq.gru.smp.ll1', derive(R['Bq.gru.smp'], log_loss_weight=1.0), 'Bq.gru.smp')
    put('Ar.peak.nokinsa.pk2', derive(R['Ar.peak.nokinsa'], peak_loss_weight=2.0), 'Ar.peak.nokinsa')


ROUNDS[12] = dict(description='Flu search round 12 (2026-11-21): log-loss 2 and log1p counts on sampled Bq, sampled GRU with '
                              'log-loss 1, peak weight 2 on Ar.peak without Kinsa.', build=round12)
def round13():
    # 21 Nov 11:05: capacity check of candidate A's sampled members (never varied for these recipes).
    put('Bq.smp.ll1.w128', derive(R['Bq.smp.ll1'], width=128), 'Bq.smp.ll1')
    put('Bq.smp.ll1.w384', derive(R['Bq.smp.ll1'], width=384), 'Bq.smp.ll1')
    put('Ar.peak.nokinsa.w192', derive(R['Ar.peak.nokinsa'], width=192), 'Ar.peak.nokinsa')
    put('Ar.peak.nokinsa.flat', derive(R['Ar.peak.nokinsa'], drop=('decoder_blocks',)), 'Ar.peak.nokinsa')


ROUNDS[13] = dict(description='Flu search round 13 (2026-11-21): width of the candidate A sampled members.', build=round13)
def round14():
    # 21 Nov 14:45: every principled axis is closed; random search (seed 20261121) around candidate A's sampled members,
    # three settings changed at once, as the COVID search's last stage. A 'better' recipe must survive reseeding.
    import random
    rng = random.Random(20261121)
    menu = {'width': lambda d: str(int(int(d.get('width', 64)) * rng.choice([0.75, 1.25]))),
            'lr': lambda d: str(float(d.get('lr', 0.001)) * rng.choice([0.5, 2.0])),
            'epochs': lambda d: str(rng.choice([160, 320])),
            'patience': lambda d: str(rng.choice([15, 40])),
            'log_loss_weight': lambda d: str(rng.choice([0.75, 1.5])),
            'batch_size': lambda d: str(rng.choice([4, 16])),
            'weight_decay': lambda d: str(rng.choice([1e-5, 1e-4])),
            'lookback': lambda d: str(rng.choice([10, 14])),
            'reporting_strength': lambda d: str(rng.choice([0.75, 1.25])),
            'correction_penalty': lambda d: str(rng.choice([1.0, 10.0])),
            'members': lambda d: str(rng.choice([64, 256])),
            'latent': lambda d: str(rng.choice([8, 32]))}
    for root, extra in (('Bq.smp.ll1', {}), ('Ar.peak.nokinsa', {'peak_loss_weight': lambda d: str(rng.choice([0.5, 1.5]))})):
        options = dict(menu, **extra)
        for i in range(8):
            d = parse(R[root])
            keys = rng.sample(sorted(options), 3)
            changes = {k: options[k](d) for k in keys}
            if 'width' in changes and int(changes['width']) % 4:
                changes['width'] = str(int(changes['width']) // 4 * 4)
            if 'patience' in changes and int(changes['patience']) >= int(changes.get('epochs', d.get('epochs', 50))):
                changes['patience'] = '25'
            put(f'{root}.RS{i}', derive(R[root], **changes), root)


ROUNDS[14] = dict(description='Flu search round 14 (2026-11-21): random search, 8 recipes around each of Bq.smp.ll1 and '
                              'Ar.peak.nokinsa, three settings changed at once (rng seed 20261121).', build=round14)
def round15():
    # 21 Nov 16:45: ED share, the one target the search has not worked on (level with B7 in backtests; behind the Hub
    # ensemble in the November 2026 evaluation). Judged on ED WIS, admissions not worse.
    for root in ('Bq.smp.ll1', 'Ar.peak.nokinsa'):
        put(f'{root}.ed4', derive(R[root], ed_transform='fourth_root'), root)
        put(f'{root}.edlin', derive(R[root], ed_transform='linear'), root)
        put(f'{root}.edraw', derive(R[root], correction_ed=0), root)


ROUNDS[15] = dict(description='Flu search round 15 (2026-11-21): ED-share handling on candidate A\'s sampled members '
                              '(fourth-root or linear ED transform instead of logit; no tree correction of ED).', build=round15)
def round16():
    # 21 Nov 20:45: the spatial axis was never crossed for candidate A's members (B family exchanges with neighbouring
    # states, A does not).
    put('Ar.peak.nokinsa.nbr', derive(R['Ar.peak.nokinsa'], spatial='neighbors'), 'Ar.peak.nokinsa')
    put('Bq.smp.ll1.nosp', derive(R['Bq.smp.ll1'], spatial='none'), 'Bq.smp.ll1')


ROUNDS[16] = dict(description='Flu search round 16 (2026-11-21): neighbouring-state exchange crossed for candidate A members.',
                  build=round16)
def round17():
    # 22 Nov 00:45: random search around candidate A's quantile member ref.B (B_width256 as in B7), never searched here.
    import random
    rng = random.Random(20261122)
    menu = {'width': lambda d: str(int(int(d.get('width', 64)) * rng.choice([0.75, 1.25])) // 4 * 4),
            'lr': lambda d: str(float(d.get('lr', 0.001)) * rng.choice([0.5, 2.0])),
            'epochs': lambda d: str(rng.choice([160, 320])),
            'log_loss_weight': lambda d: str(rng.choice([0.25, 1.0])),
            'batch_size': lambda d: str(rng.choice([4, 16])),
            'weight_decay': lambda d: str(rng.choice([1e-5, 1e-4])),
            'lookback': lambda d: str(rng.choice([10, 14])),
            'reporting_strength': lambda d: str(rng.choice([0.75, 1.25])),
            'correction_penalty': lambda d: str(rng.choice([1.0, 10.0])),
            'joint_weight': lambda d: str(rng.choice([0.05, 0.2])),
            'reconstruction_weeks': lambda d: str(rng.choice([2, 6]))}
    for i in range(8):
        d = parse(R['ref.B'])
        changes = {k: menu[k](d) for k in rng.sample(sorted(menu), 3)}
        put(f'ref.B.RS{i}', derive(R['ref.B'], **changes), 'ref.B')


ROUNDS[17] = dict(description='Flu search round 17 (2026-11-22): random search around ref.B (rng seed 20261122).', build=round17)
def round18():
    # 22 Nov 05:00: with the newest admission week missing at the deadline (stress view 'delayed'), candidate A degrades
    # more than B7 (8 seeds: 0.387 vs 0.363). Teach robustness in training: random input-cell masking (autoencoder_mask,
    # acts in the network without the reconstruction loss) or transported donor missingness masks. All with stress views;
    # controls are the stress-view fits of flu-s-st01 (same seeds).
    for root in ('Bq.smp.ll1', 'ref.B', 'Ar.peak.nokinsa'):
        put(f'{root}.mask10', derive(R[root], autoencoder_mask=0.1, stress_views=1), root)
        put(f'{root}.miss', derive(R[root], reporting_missingness=1, stress_views=1), root)


ROUNDS[18] = dict(description='Flu search round 18 (2026-11-22): robustness to a missing newest week (input masking, donor '
                              'missingness) on candidate A members, with stress views.', build=round18)
def round19():
    # 22 Nov 05:50: 10% random masking makes A's members much more robust to a missing newest week (-7 to -13%) but costs
    # 2-5% on normal inputs. Targeted newest-week masking (new option newest_mask) and a lighter random mask.
    for root in ('Bq.smp.ll1', 'ref.B', 'Ar.peak.nokinsa'):
        put(f'{root}.nm10', derive(R[root], newest_mask=0.1, stress_views=1), root)
    for root in ('Bq.smp.ll1', 'ref.B'):
        put(f'{root}.mask03', derive(R[root], autoencoder_mask=0.03, stress_views=1), root)


ROUNDS[19] = dict(description='Flu search round 19 (2026-11-22): newest-week masking (new option newest_mask) and 3% random '
                              'masking on candidate A members, with stress views.', build=round19)
def round20():
    # 22 Nov 09:45: newest-week masking adopted at 0.1; is 0.1 on a plateau? 0.05 and 0.2 on the B-family members.
    for root in ('Bq.smp.ll1', 'ref.B'):
        for v, tag in ((0.05, 'nm05'), (0.2, 'nm20')):
            put(f'{root}.{tag}', derive(R[root], newest_mask=v, stress_views=1), root)


ROUNDS[20] = dict(description='Flu search round 20 (2026-11-22): newest-week masking rate 0.05 and 0.2 on the B-family members.',
                  build=round20)
def round21():
    # 22 Nov 13:45: is the gain from masking, from the new members, or both? Masked B7 (its other two members masked;
    # ref.B.nm10 exists) as the minimal-change alternative to masked candidate A.
    for root in ('ref.A', 'ref.B5'):
        put(f'{root}.nm10', derive(R[root], newest_mask=0.1, stress_views=1), root)


ROUNDS[21] = dict(description='Flu search round 21 (2026-11-22): newest-week masking on B7\'s A_blocks3 and B5 (masked B7).',
                  build=round21)
def round22():
    # 22 Nov 16:05, user: are covariates, hospital-reporting coverage or other data streams worth retrying? Round 1
    # tested them on the old roots (all level or worse). Retried on the final masked members, which now tolerate missing
    # inputs; with stress views (missing newest week) and the 2023-24 guard.
    for root in ('Bq.smp.ll1.nm10', 'ref.B.nm10', 'Ar.peak.nokinsa.nm10'):
        r = R[root]
        put(f'{root}.cov', derive(add_covariates(r, 'hosprep'), error_signals='all'), root)       # coverage: trees and network
        put(f'{root}.covtrees', derive(add_covariates(r, 'hosprep'), error_signals='all', network_coverage=0), root)
        for tag, cs in (('ww', 'ww_flu'), ('wwrank', 'ww_flu_pct_rank'), ('clab', 'clinical_lab'), ('fsurv', 'flusurv'),
                        ('ilinet', 'ilinet'), ('outp', 'outpatient_flu'), ('kinsa', 'kinsa')):
            put(f'{root}.{tag}', add_covariates(r, cs), root)


ROUNDS[22] = dict(description='Flu search round 22 (2026-11-22, user request): covariates and hospital-reporting coverage '
                              'retried on the final masked members, with stress views.', build=round22)
def round23():
    # 23 Nov 04:45: two options never tried here on the sampled members, aimed at the peak (every model ~0.36 log low
    # near the peak): a learned latent prior (conditional VAE, improved peak-week scores in autoenc-20261024) and a
    # shared national noise factor (coherent state trajectories, US total).
    for root in ('Bq.smp.ll1.nm10', 'Ar.peak.nokinsa.nm10'):
        put(f'{root}.cvae', derive(R[root], latent_model='cvae'), root)
        put(f'{root}.usf', derive(R[root], us_error='shared_factor'), root)


ROUNDS[23] = dict(description='Flu search round 23 (2026-11-23): conditional-VAE latent and shared national noise factor on '
                              'the masked sampled members.', build=round23)
GUARD = {'g03': ['Bq.gru', 'Bq.ll1', 'Bq.gru.ll1', 'Bq.gru.lb8', 'Bq.gru.nat', 'Bq.gru.bes', 'Bh.gru.ll1', 'Ar.flat',
                 'Ar.flat.gru', 'Ar.flat.gru.w192'],
         'g04': ['B5r', 'B5r.peak', 'B5r.local', 'Ar.peak', 'Bq.smp', 'Bq.gru.smp', 'Bq.gru.smp.peak', 'Bq.gru.smp.local',
                 'B5r.peak.local'],
         'g05': ['Bh.smp', 'Bh.smp.peak', 'Bh.smp.local', 'Bq.hc', 'Bq.hc.smp'],
         'g06': ['Bq.smp.peak', 'Bq.smp.local', 'Bq.smp.ll1'],
         'g07': ['Bq.hc.smp.peak', 'Bh.smp.peak.x'],
         'g08': ['Bq.hc.smp.ll1', 'Bh.smp.ll1', 'Bq.smp.ll1.local'],
         'g09': ['Bq.amp3', 'Bq.hc.smp.amp3', 'Bh.smp.amp3', 'Ar.peak.amp3', 'Ar.peak.amp5'],
         'g10': ['Bq.smp.ll1.lb8', 'Bq.smp.ll1.lb16', 'Ar.peak.nokinsa'],
         'g11': ['Bq.smp.ll1.ili'],
         'g12': ['Bq.smp.ll2', 'Bq.smp.ll1.log1p', 'Bq.gru.smp.ll1', 'Ar.peak.nokinsa.pk2'],
         'g13': ['Bq.smp.ll1.w128', 'Bq.smp.ll1.w384', 'Ar.peak.nokinsa.w192', 'Ar.peak.nokinsa.flat'],
         'g14': [f'{r}.RS{i}' for r in ('Bq.smp.ll1', 'Ar.peak.nokinsa') for i in range(8)],
         'g15': [f'{r}.{v}' for r in ('Bq.smp.ll1', 'Ar.peak.nokinsa') for v in ('ed4', 'edlin', 'edraw')],
         'g16': ['Ar.peak.nokinsa.nbr', 'Bq.smp.ll1.nosp'],
         'g17': [f'ref.B.RS{i}' for i in range(8)],
         'g21': ['ref.A.nm10', 'ref.B5.nm10'],
         'g22': [f'{r}.{t}' for r in ('Bq.smp.ll1.nm10', 'ref.B.nm10', 'Ar.peak.nokinsa.nm10')
                 for t in ('cov', 'covtrees', 'ww', 'wwrank', 'clab', 'fsurv', 'ilinet', 'outp', 'kinsa')],
         'g23': [f'{r}.{t}' for r in ('Bq.smp.ll1.nm10', 'Ar.peak.nokinsa.nm10') for t in ('cvae', 'usf')]}


def write_guard(tag):
    for n in sorted(ROUNDS):
        ROUNDS[n]['build']()
    names = GUARD[tag]
    study = dict(description=f'Flu search guard {tag} (2023-24 held out, artificial reports): {", ".join(names)}.', round=tag,
                 parents={k: PARENT[k] for k in names if k in PARENT},
                 candidates={k: derive(R[k], error_reference='2025-2026') for k in names}, seeds=SEEDS)
    (HERE / f'guard-{tag}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'guard {tag}: {len(names)} recipes x {len(SEEDS)} seeds')


RESEED = {'rs01': (['ref.A', 'ref.B5', 'ref.B', 'ref.Bes', 'Bq', 'Bh', 'Ar'], list(range(52, 60))),
          'rs02': (['Bq.gru', 'Bq.ll1', 'Ar.peak', 'B5r.peak', 'B5r.local'], list(range(52, 60))),
          'rs03': (['Bq.smp'], list(range(52, 60))),
          'rs04': (['Bq.hc.smp', 'Bh.smp'], list(range(52, 60))),
          'rs05': (['Bq.smp.ll1'], list(range(52, 60))),
          'rs06': (['ref.A', 'ref.B5', 'ref.B', 'Bq', 'Bh', 'Ar.peak', 'Bq.smp.ll1', 'Bh.smp'], list(range(60, 68))),
          'rs07': (['ref.A', 'ref.B5', 'ref.B', 'Ar.peak', 'Bq.smp.ll1', 'Bh.smp'], list(range(68, 76))),
          'rs08': (['Ar.peak.nokinsa'], list(range(52, 68)))}


def write_reseed(tag):
    for n in sorted(ROUNDS):
        ROUNDS[n]['build']()
    names, seeds = RESEED[tag]
    study = dict(description=f'Flu search reseed {tag}: {", ".join(names)} on seeds {seeds[0]}-{seeds[-1]}.', round=tag,
                 parents={}, candidates={k: R[k] for k in names}, seeds=seeds)
    (HERE / f'reseed-{tag}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'reseed {tag}: {len(names)} recipes x {len(seeds)} seeds')


def write(n):
    before = set(R)
    ROUNDS[n]['build']()
    names = [k for k in R if k not in before] if n > 1 else list(R)
    for kind, extra in (('round', {}), ('guard', {'error_reference': '2025-2026'})):
        study = dict(description=ROUNDS[n]['description'] + (' Guard: 2023-24 held out, artificial reports.' if extra else ''),
                     round=n, parents={k: PARENT[k] for k in names if k in PARENT},
                     candidates={k: derive(R[k], **extra) for k in names}, seeds=SEEDS)
        (HERE / f'{kind}-{n:02d}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'round {n}: {len(names)} recipes x {len(SEEDS)} seeds')


if __name__ == '__main__':
    if sys.argv[1] in GUARD:
        write_guard(sys.argv[1])
        sys.exit()
    if sys.argv[1] in RESEED:
        write_reseed(sys.argv[1])
        sys.exit()
    target = int(sys.argv[1])
    for n in sorted(ROUNDS):
        if n < target:
            ROUNDS[n]['build']()
    write(target)

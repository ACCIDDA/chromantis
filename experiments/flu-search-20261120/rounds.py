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
GUARD = {'g03': ['Bq.gru', 'Bq.ll1', 'Bq.gru.ll1', 'Bq.gru.lb8', 'Bq.gru.nat', 'Bq.gru.bes', 'Bh.gru.ll1', 'Ar.flat',
                 'Ar.flat.gru', 'Ar.flat.gru.w192'],
         'g04': ['B5r', 'B5r.peak', 'B5r.local', 'Ar.peak', 'Bq.smp', 'Bq.gru.smp', 'Bq.gru.smp.peak', 'Bq.gru.smp.local',
                 'B5r.peak.local'],
         'g05': ['Bh.smp', 'Bh.smp.peak', 'Bh.smp.local', 'Bq.hc', 'Bq.hc.smp'],
         'g06': ['Bq.smp.peak', 'Bq.smp.local', 'Bq.smp.ll1'],
         'g07': ['Bq.hc.smp.peak', 'Bh.smp.peak.x']}


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
          'rs04': (['Bq.hc.smp', 'Bh.smp'], list(range(52, 60)))}


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

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
RESEED = {'rs01': (['ref.A', 'ref.B5', 'ref.B', 'ref.Bes', 'Bq', 'Bh', 'Ar'], list(range(52, 60)))}


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
    if sys.argv[1] in RESEED:
        write_reseed(sys.argv[1])
        sys.exit()
    target = int(sys.argv[1])
    for n in sorted(ROUNDS):
        if n < target:
            ROUNDS[n]['build']()
    write(target)

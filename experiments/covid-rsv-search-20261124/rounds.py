"""Recipe definitions of the COVID and RSV search (covid-rsv-search-20261124), run with the flu search's practice
(experiments/flu-search-20261120): no 2026-27 data in any choice, leak-free reporting errors, a 2023-24 guard season,
eight seeds per recipe, pre-registered margins.

Every candidate is a parent recipe plus named changes, so a child's difference from its parent is explicit.
Main study files ({pathogen}-round-NN.json) carry no error_reference: each fold draws artificial reporting errors and
real report pairs from its own latest training season (2024-25 for the 2025-26 fold, 2025-26 for the 2024-25 fold).
Before (covid-rsv-coverage-20261118 and every earlier COVID/RSV study) recipes carried error_reference=2025-2026, so the
2025-26 fold trained on 2025-26's own reporting errors. Guard files ({pathogen}-guard-NN.json) are the same recipes with
error_reference=2025-2026, required by the prescribed 2023-24 guard problems.

    python3 experiments/covid-rsv-search-20261124/rounds.py covid 1
    python3 experiments/covid-rsv-search-20261124/rounds.py rsv g02     # a guard-only or reseed file (GUARD / RESEED)
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


def leak_free(recipe):
    return derive(recipe, drop=('error_reference',), stress_views=1)


# COVID. Production release covid-gru-four-candidate-20261103 (submitted since 7 Nov): four recipes, here without
# error_reference. Then the three members recommended on 20 Nov by covid-rsv-coverage-20261118 (chosen with a live gate on
# 2026-27 reports and with leaky errors; never submitted).
COVID = {
    'ref.Ah': 'history_source=artificial,history_correction=1,error_signals=all,input_set=target,correction_weeks=2,correction_ed=1,reporting_probability=0.5,joint_weight=0.05,correction_penalty=30.0,reporting_missingness=0,reporting_method=synchronous_phase_log,ed_transform=logit,width=192,epochs=160,patience=25,fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,log_loss_weight=1.0,spatial=neighbors',
    'ref.pN': 'history_source=artificial,reconstruction_labels=1,error_signals=all,input_set=target,correction_weeks=2,correction_ed=1,reporting_probability=0.25,joint_weight=0.1,correction_penalty=3.0,reporting_missingness=0,reporting_method=synchronous_phase_log,reconstruction_weeks=4,ed_transform=logit,spatial=national_broadcast,decoder=quantile,width=256,epochs=240,patience=25,lr=0.0005,fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,log_loss_weight=0.5,encoder=gru',
    'ref.N': 'error_signals=all,input_set=target,correction_weeks=2,correction_ed=1,joint_weight=0.1,correction_penalty=3.0,reporting_missingness=0,reporting_method=synchronous_phase_log,reconstruction_weeks=4,ed_transform=logit,spatial=national_broadcast,decoder=quantile,width=256,epochs=240,patience=25,lr=0.0005,fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,log_loss_weight=0.5,signal_features=multiscale',
    'ref.Bh': 'history_source=artificial,reconstruction_labels=1,error_signals=all,input_set=target,correction_weeks=2,correction_ed=1,reporting_probability=0.5,joint_weight=0.1,correction_penalty=3.0,reporting_missingness=0,reporting_method=synchronous_phase_log,reconstruction_weeks=4,ed_transform=logit,spatial=neighbors,decoder=quantile,width=256,epochs=240,patience=25,lr=0.0005,fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,log_loss_weight=0.5,weight_decay=0.0001',
}
# T = T.pN_gru.real (GRU quantile, US-only summary, trees from real report pairs); Tl = T.pN_gru.real.log_loss1;
# S = S.Ah.gru_national.real (sampled GRU, US summary, real-pair trees, network on corrected histories).
COVID['T'] = derive(COVID['ref.pN'], corrector_examples='real')
COVID['Tl'] = derive(COVID['T'], log_loss_weight=1.0)
COVID['S'] = derive(COVID['ref.Ah'], spatial='national_broadcast', encoder='gru', corrector_examples='real')
# RSV. Production release rsv-four-20261014 (submitted since 17 Oct, trees at half strength from 14 Nov), then the
# 20 Nov recommendation of covid-rsv-coverage-20261118: A4c0.national.rsvnet.calendar(.weeks1).
RSV = {
    'ref.Ball': 'history_source=artificial,reconstruction_labels=1,error_signals=targets,input_set=all,correction_weeks=2,correction_ed=1,joint_weight=0.1,correction_penalty=3.0,reporting_missingness=0,reporting_method=synchronous_phase_log,reconstruction_weeks=4,ed_transform=logit,spatial=neighbors,decoder=quantile,width=512,epochs=240,patience=25,lr=0.0005,fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,actual_share=1.0,log_loss_weight=0.75,annual_calendar=0',
    'ref.Bw': 'history_source=artificial,reconstruction_labels=1,error_signals=targets,input_set=all,correction_weeks=2,correction_ed=1,joint_weight=0.1,correction_penalty=3.0,reporting_missingness=0,reporting_method=synchronous_phase_log,reconstruction_weeks=4,ed_transform=logit,spatial=neighbors,decoder=quantile,width=256,epochs=240,patience=25,lr=0.0005,fit_partition=pathogen,covariate_encoder=summary,input_normalization=b0,log_loss_weight=0.5',
    'ref.A4c0': 'history_source=artificial,history_correction=1,error_signals=targets,input_set=target,correction_weeks=2,correction_ed=1,joint_weight=0.05,correction_penalty=30.0,reporting_missingness=0,reporting_method=synchronous_phase_log,ed_transform=logit,width=192,epochs=160,patience=25,fit_partition=pathogen,covariate_encoder=summary,covariate_set=kinsa,input_normalization=b0,log_loss_weight=1.0,annual_calendar=0',
    'ref.A4i': 'history_source=artificial,history_correction=1,error_signals=targets,input_set=all,correction_weeks=2,correction_ed=1,joint_weight=0.05,correction_penalty=30.0,reporting_missingness=0,reporting_method=synchronous_phase_log,ed_transform=logit,width=192,epochs=160,patience=25,fit_partition=pathogen,covariate_encoder=summary,covariate_set=kinsa,input_normalization=b0,log_loss_weight=1.0',
}
# Rc = A4c0.national.rsvnet.calendar (sampled MLP, US summary, Kinsa + RSV-NET, calendar); R1 = the same correcting the
# newest week only (A4c0.national.rsvnet.calendar.weeks1).
RSV['Rc'] = 'history_source=artificial,history_correction=1,error_signals=all,input_set=target,correction_weeks=2,correction_ed=1,joint_weight=0.05,correction_penalty=30.0,reporting_missingness=0,reporting_method=synchronous_phase_log,ed_transform=logit,width=192,epochs=160,patience=25,fit_partition=pathogen,covariate_encoder=summary,covariate_set=kinsa+rsvnet,input_normalization=b0,log_loss_weight=1.0,spatial=national_broadcast'
RSV['R1'] = derive(RSV['Rc'], correction_weeks=1)

R = {'covid': {}, 'rsv': {}}       # pathogen -> name -> recipe
PARENT = {'covid': {}, 'rsv': {}}  # pathogen -> name -> parent name


def put(p, name, recipe, parent=None):
    if name in R[p]:
        raise ValueError(f'duplicate {p} {name}')
    R[p][name] = recipe
    if parent:
        PARENT[p][name] = parent


ROUNDS = {'covid': {}, 'rsv': {}}


def covid1():
    for k, v in COVID.items():
        put('covid', k, leak_free(v), {'T': 'ref.pN', 'Tl': 'T', 'S': 'ref.Ah'}.get(k))
    r = R['covid']
    # The flu search's adopted change: hide each location's newest input week with probability 0.1 in training.
    for root in ('Tl', 'S', 'ref.Bh', 'ref.Ah'):
        put('covid', f'{root}.nm10', derive(r[root], newest_mask=0.1), root)
    # The flu search's best sampled member: B-family network with a sampled (trajectory) head and log-loss weight 1.
    put('covid', 'Tl.smp', derive(r['Tl'], drop=('decoder',)), 'Tl')
    # Peak loss (CRPS of each path's peak size and week) helped every sampled flu recipe.
    put('covid', 'S.peak', derive(r['S'], peak_loss_weight=1.0), 'S')
    # Data streams: hospital-reporting coverage (trees and network), wastewater, every archived season's report pairs.
    put('covid', 'Tl.cov', add_covariates(r['Tl'], 'hosprep_covid'), 'Tl')
    put('covid', 'Tl.ww', add_covariates(r['Tl'], 'ww_covid'), 'Tl')
    put('covid', 'S.ww', add_covariates(r['S'], 'ww_covid'), 'S')
    put('covid', 'Tl.esall', derive(r['Tl'], error_seasons='all'), 'Tl')


def rsv1():
    for k, v in RSV.items():
        put('rsv', k, leak_free(v), {'R1': 'Rc'}.get(k))
    r = R['rsv']
    for root in ('R1', 'Rc', 'ref.Bw', 'ref.A4c0'):
        put('rsv', f'{root}.nm10', derive(r[root], newest_mask=0.1), root)
    put('rsv', 'R1.peak', derive(r['R1'], peak_loss_weight=1.0), 'R1')
    put('rsv', 'R1.real', derive(r['R1'], corrector_examples='real'), 'R1')     # trees from real archived report pairs
    put('rsv', 'R1.nokinsa', derive(r['R1'], covariate_set='rsvnet'), 'R1')     # Kinsa dropped (flu: no loss, less risk)
    put('rsv', 'R1.ww', add_covariates(r['R1'], 'ww_rsv'), 'R1')
    put('rsv', 'R1.nrevss', add_covariates(r['R1'], 'nrevss_rsv'), 'R1')
    put('rsv', 'R1.cov', add_covariates(r['R1'], 'hosprep_rsv'), 'R1')
    put('rsv', 'Bwq', derive(r['ref.Bw'], corrector_examples='real', spatial='national_broadcast'), 'ref.Bw')  # flu Bq-like root
    put('rsv', 'Bwq.smp', derive(r['Bwq'], drop=('decoder',), log_loss_weight=1.0), 'Bwq')  # flu's Bq.smp.ll1 analogue


ROUNDS['covid'][1] = dict(description='COVID search round 1 (2026-11-24): production covid-gru-four members and the 20 Nov '
                                      'recommendation, leak-free; flu-search transfers (newest-week masking, sampled head, '
                                      'peak loss) and data streams (coverage, wastewater, all-season report pairs).',
                          build=covid1)
ROUNDS['rsv'][1] = dict(description='RSV search round 1 (2026-11-24): production rsv-four members and the 20 Nov '
                                    'recommendation, leak-free; flu-search transfers (newest-week masking, peak loss, '
                                    'real-pair trees, sampled B-family head) and data streams (wastewater, NREVSS, coverage).',
                        build=rsv1)

def covid2():
    # 24 Nov 13:30: Google Trends (pulled 24 Nov; gt_* = log of the week's search interest over the state's trailing 52-week
    # median). Run on the gt panel (problems/*-gt.json), same panel otherwise; parents are the round-1 fits on the plain panel.
    # The flu search found Trends level on 2024-25/2025-26 and worse on its 2023-24 guard.
    r = R['covid']
    put('covid', 'Tl.gt', add_covariates(r['Tl'], 'gt_covid'), 'Tl')
    put('covid', 'Tl.gtsym', add_covariates(r['Tl'], 'gt_covid_sym'), 'Tl')
    put('covid', 'S.gt', add_covariates(r['S'], 'gt_covid'), 'S')


def rsv2():
    r = R['rsv']
    put('rsv', 'R1.gt', add_covariates(r['R1'], 'gt_rsv'), 'R1')
    put('rsv', 'R1.gtterm', add_covariates(r['R1'], 'gt_rsv_term'), 'R1')
    put('rsv', 'ref.Bw.gt', add_covariates(r['ref.Bw'], 'gt_rsv'), 'ref.Bw')


ROUNDS['covid'][2] = dict(description='COVID search round 2 (2026-11-24): Google Trends covariates ("covid symptoms", "covid test"), '
                                      'gt panel.', build=covid2)
ROUNDS['rsv'][2] = dict(description='RSV search round 2 (2026-11-24): Google Trends covariates ("rsv", "rsv symptoms"), gt panel.',
                        build=rsv2)

def covid3():
    # 24 Nov 13:50, round 1 (8 seeds, leak-free): nothing 'better'. T (0.2417) is the best single recipe; log-loss 1 (Tl)
    # no longer helps once errors are leak-free (+2.0%, level); newest-week masking, sampled head, coverage and wastewater
    # are level to slightly worse on Tl. ref.N (network on finalized histories, no artificial errors; 0.2439) is second
    # and best on ED share: the trees do the whole nowcast and nothing is counted twice. Expand T and N.
    r = R['covid']
    put('covid', 'T.esall', derive(r['T'], error_seasons='all'), 'T')        # Tl.esall was -2.1% vs Tl
    put('covid', 'N.gru', derive(r['ref.N'], encoder='gru'), 'ref.N')        # GRU helped pN over the MLP B family
    put('covid', 'N.real', derive(r['ref.N'], corrector_examples='real'), 'ref.N')  # N's trees from real report pairs
    put('covid', 'N.smp', derive(r['ref.N'], drop=('decoder',)), 'ref.N')     # sampled (trajectory) N
    put('covid', 'N.ll1', derive(r['ref.N'], log_loss_weight=1.0), 'ref.N')
    # S trained on finalized histories (no artificial errors, no corrected training histories): a sampled GRU 'N'.
    put('covid', 'S.fin', derive(r['S'], drop=('history_source', 'history_correction', 'reporting_probability')), 'S')
    put('covid', 'T.ms', derive(r['T'], signal_features='multiscale'), 'T')


ROUNDS['covid'][3] = dict(description='COVID search round 3 (2026-11-24): children of the two best leak-free recipes, T (GRU '
                                      'quantile, real-pair trees) and ref.N (finalized training histories): GRU, real-pair trees, '
                                      'sampled head, log-loss 1, all-season pairs, multiscale; S on finalized histories.',
                          build=covid3)

def rsv3():
    # 24 Nov 14:50, round 1 (8 seeds, leak-free): Bwq (ref.Bw with real-pair trees and a US-only summary instead of
    # neighbouring states) 0.3278 vs ref.Bw 0.3521, -6.9%, lower in both seasons: 'better' on the main problem (guard
    # pending). Its sampled head with log-loss 1 (Bwq.smp, 0.3246) is level with it and preferred (trajectories).
    # Decompose Bwq's two changes, and expand the sampled B-family root. R1.real could not be fitted (newest week only:
    # no real ED pairs), so real-pair trees are tried on Rc (two weeks corrected).
    r = R['rsv']
    put('rsv', 'Bw.real', derive(r['ref.Bw'], corrector_examples='real'), 'ref.Bw')
    put('rsv', 'Bw.nat', derive(r['ref.Bw'], spatial='national_broadcast'), 'ref.Bw')
    put('rsv', 'Rc.real', derive(r['Rc'], corrector_examples='real'), 'Rc')
    b = r['Bwq.smp']
    put('rsv', 'Bwq.smp.nm10', derive(b, newest_mask=0.1), 'Bwq.smp')
    put('rsv', 'Bwq.smp.peak', derive(b, peak_loss_weight=1.0), 'Bwq.smp')
    put('rsv', 'Bwq.smp.tgt', derive(b, input_set='target'), 'Bwq.smp')        # RSV histories only (flu: other pathogens hurt)
    put('rsv', 'Bwq.smp.gru', derive(b, encoder='gru'), 'Bwq.smp')             # COVID's T/S use a GRU
    put('rsv', 'Bwq.smp.esall', derive(b, error_seasons='all'), 'Bwq.smp')
    put('rsv', 'Bwq.smp.hc', derive(b, drop=('reconstruction_labels', 'reconstruction_weeks'), history_correction=1), 'Bwq.smp')


ROUNDS['rsv'][3] = dict(description='RSV search round 3 (2026-11-24): decomposition of the round-1 winner Bwq (real-pair trees, '
                                    'US summary) and children of its sampled version Bwq.smp; real-pair trees on Rc.', build=rsv3)

# Guard-only files: recipes guarded after they pass the main problem (children are not guarded otherwise).
GUARD = {'covid': {'g01': ['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'Tl', 'S']},
         'rsv': {'g01': ['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Rc', 'R1'],
                 'g03': ['Bwq', 'Bwq.smp']}}
RESEED = {'covid': {'rs01': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'Tl', 'S'], list(range(52, 60)))},
          'rsv': {'rs01': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Rc', 'R1'], list(range(52, 60)))}}


def build_all(p, upto=None):
    for n in sorted(ROUNDS[p]):
        if upto is None or n < upto:
            ROUNDS[p][n]['build']()


def write_guard(p, tag):
    build_all(p)
    names = GUARD[p][tag]
    study = dict(description=f'{p} search guard {tag} (2023-24 held out, artificial reports): {", ".join(names)}.', round=tag,
                 parents={k: PARENT[p][k] for k in names if k in PARENT[p]},
                 candidates={k: derive(R[p][k], error_reference='2025-2026') for k in names}, seeds=SEEDS)
    (HERE / f'{p}-guard-{tag}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'{p} guard {tag}: {len(names)} recipes x {len(SEEDS)} seeds')


def write_reseed(p, tag):
    build_all(p)
    names, seeds = RESEED[p][tag]
    study = dict(description=f'{p} search reseed {tag}: {", ".join(names)} on seeds {seeds[0]}-{seeds[-1]}.', round=tag,
                 parents={}, candidates={k: R[p][k] for k in names}, seeds=seeds)
    (HERE / f'{p}-reseed-{tag}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'{p} reseed {tag}: {len(names)} recipes x {len(seeds)} seeds')


def write(p, n):
    build_all(p, upto=n)
    before = set(R[p])
    ROUNDS[p][n]['build']()
    names = [k for k in R[p] if k not in before]
    study = dict(description=ROUNDS[p][n]['description'], round=n, parents={k: PARENT[p][k] for k in names if k in PARENT[p]},
                 candidates={k: R[p][k] for k in names}, seeds=SEEDS)
    (HERE / f'{p}-round-{n:02d}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'{p} round {n}: {len(names)} recipes x {len(SEEDS)} seeds')


if __name__ == '__main__':
    p, tag = sys.argv[1], sys.argv[2]
    if tag in GUARD[p]:
        write_guard(p, tag)
    elif tag in RESEED[p]:
        write_reseed(p, tag)
    else:
        write(p, int(tag))

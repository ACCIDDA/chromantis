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

def rsv4():
    # 24 Nov 16:50: Google Trends helped ref.Bw on the main problem (ref.Bw.gt -5.4%, lower in both seasons; level on R1).
    # Same covariates on the round-1 winner Bwq and its sampled version (gt panel; parents on the plain panel).
    r = R['rsv']
    put('rsv', 'Bwq.gt', add_covariates(r['Bwq'], 'gt_rsv'), 'Bwq')
    put('rsv', 'Bwq.smp.gt', add_covariates(r['Bwq.smp'], 'gt_rsv'), 'Bwq.smp')


ROUNDS['rsv'][4] = dict(description='RSV search round 4 (2026-11-24): Google Trends ("rsv", "rsv symptoms") on Bwq and Bwq.smp, '
                                    'gt panel.', build=rsv4)

def rsv5():
    # 24 Nov 17:45, round 3: Bwq's gain is the US-only summary (Bw.nat -6.8% vs ref.Bw, lower in both seasons), not the
    # real-pair trees (Bw.real -0.5%). Same exchange on the other production members (Ball uses neighbouring states, the
    # A4 recipes no exchange); quantile Bwq with newest-week masking (flu's ref.B.nm10 member).
    r = R['rsv']
    put('rsv', 'Ball.nat', derive(r['ref.Ball'], spatial='national_broadcast'), 'ref.Ball')
    put('rsv', 'A4c0.nat', derive(r['ref.A4c0'], spatial='national_broadcast'), 'ref.A4c0')
    put('rsv', 'A4i.nat', derive(r['ref.A4i'], spatial='national_broadcast'), 'ref.A4i')
    put('rsv', 'Bwq.nm10', derive(r['Bwq'], newest_mask=0.1), 'Bwq')


ROUNDS['rsv'][5] = dict(description='RSV search round 5 (2026-11-24): US-only summary on the other production members; '
                                    'newest-week masking on quantile Bwq.', build=rsv5)

def rsv6():
    # 24 Nov 19:45, round 5: the US-only summary helps the recipes that read all six histories (A4i.nat -9.2%, Bw.nat -4.4%
    # at 16 seeds and better on the 2023-24 guard), not Ball (+3.2%) or A4c0 (+0.9%). Children of the sampled A4i.nat.
    r = R['rsv']
    a = r['A4i.nat']
    put('rsv', 'A4i.nat.nokinsa', derive(a, covariate_set='none'), 'A4i.nat')
    put('rsv', 'A4i.nat.real', derive(a, corrector_examples='real'), 'A4i.nat')
    put('rsv', 'A4i.nat.nm10', derive(a, newest_mask=0.1), 'A4i.nat')
    put('rsv', 'A4i.nat.peak', derive(a, peak_loss_weight=1.0), 'A4i.nat')
    put('rsv', 'A4i.nat.esall', derive(a, error_signals='all'), 'A4i.nat')   # coverage signals in the error model, as Rc


ROUNDS['rsv'][6] = dict(description='RSV search round 6 (2026-11-24): children of A4i.nat (production A4i with the US-only '
                                    'summary): no Kinsa, real-pair trees, newest-week masking, peak loss, all error signals.',
                        build=rsv6)

def covid4():
    # 24 Nov 20:40: COVID mixtures stall within about 2.5% of production. Structural ideas not tried on COVID yet:
    # every pathogen's admission/ED histories as inputs (helps RSV recipes with the US-only summary), the US-only summary on
    # the MLP Ah (S has GRU + summary + real trees together), T's network on tree-corrected histories (no double count),
    # lookback 8 and 16 on N.
    r = R['covid']
    put('covid', 'T.all', derive(r['T'], input_set='all'), 'T')
    put('covid', 'N.all', derive(r['ref.N'], input_set='all'), 'ref.N')
    put('covid', 'Ah.nat', derive(r['ref.Ah'], spatial='national_broadcast'), 'ref.Ah')
    put('covid', 'T.hc', derive(r['T'], drop=('reconstruction_labels', 'reconstruction_weeks'), history_correction=1), 'T')
    put('covid', 'N.lb8', derive(r['ref.N'], lookback=8), 'ref.N')
    put('covid', 'N.lb16', derive(r['ref.N'], lookback=16), 'ref.N')


ROUNDS['covid'][4] = dict(description='COVID search round 4 (2026-11-24): all-pathogen inputs on T and N, US-only summary on Ah, '
                                      'T on corrected histories, lookback 8/16 on N.', build=covid4)


def rsv7():
    # 24 Nov 20:40: the US-only summary helps the all-history recipes (Bw.nat, A4i.nat). Sampled Bw.nat (Bwq.smp without the
    # real-pair trees), RSV-NET rates on the national recipes (Rc reads them), and Rc with all six histories.
    r = R['rsv']
    put('rsv', 'Bw.nat.smp', derive(r['Bw.nat'], drop=('decoder',), log_loss_weight=1.0), 'Bw.nat')
    put('rsv', 'Bw.nat.rsvnet', add_covariates(r['Bw.nat'], 'rsvnet'), 'Bw.nat')
    put('rsv', 'A4i.nat.rsvnet', add_covariates(r['A4i.nat'], 'rsvnet'), 'A4i.nat')
    put('rsv', 'Rc.all', derive(r['Rc'], input_set='all'), 'Rc')


ROUNDS['rsv'][7] = dict(description='RSV search round 7 (2026-11-24): sampled Bw.nat, RSV-NET on the national all-history '
                                    'recipes, Rc with all six histories.', build=rsv7)

def rsv8():
    # 24 Nov 21:40: Bw.nat (production Bw with the US-only summary) passes every rule; A4i.nat is -8.7% on the main problem
    # but +4.6% on the 2023-24 ED guard (level); none of A4i.nat's children helps. One-change children of Bw.nat.
    r = R['rsv']
    b = r['Bw.nat']
    put('rsv', 'Bw.nat.nm10', derive(b, newest_mask=0.1), 'Bw.nat')
    put('rsv', 'Bw.nat.esall', derive(b, error_signals='all'), 'Bw.nat')
    put('rsv', 'Bw.nat.ll1', derive(b, log_loss_weight=1.0), 'Bw.nat')
    put('rsv', 'Bw.nat.w512', derive(b, width=512), 'Bw.nat')


ROUNDS['rsv'][8] = dict(description='RSV search round 8 (2026-11-24): children of Bw.nat (newest-week masking, all error '
                                    'signals, log-loss 1, width 512).', build=rsv8)

def covid5():
    # 25 Nov 02:40: the cross-location exchange is the axis that moved RSV most (US-only summary). Other exchanges on the
    # two best COVID recipes (both use the US-only summary): HHS-region attention, gated pooling, distance kernel.
    r = R['covid']
    for root in ('T', 'ref.N'):
        for tag, sp in (('region', 'region_attention'), ('gated', 'gated_pool'), ('dist', 'distance')):
            put('covid', f'{root}.{tag}', derive(r[root], spatial=sp), root)


ROUNDS['covid'][5] = dict(description='COVID search round 5 (2026-11-25): cross-location exchange (HHS-region attention, gated '
                                      'pooling, distance kernel) on T and ref.N.', build=covid5)


def rsv9():
    # Same exchanges on the RSV recipes whose gain came from the US-only summary.
    r = R['rsv']
    for root in ('Bw.nat', 'A4i.nat'):
        for tag, sp in (('region', 'region_attention'), ('gated', 'gated_pool'), ('dist', 'distance')):
            put('rsv', f'{root}.{tag}', derive(r[root], spatial=sp), root)


ROUNDS['rsv'][9] = dict(description='RSV search round 9 (2026-11-25): cross-location exchange (HHS-region attention, gated '
                                    'pooling, distance kernel) in place of the US-only summary on Bw.nat and A4i.nat.', build=rsv9)

def covid6():
    # 25 Nov 03:40: region attention cannot run (the location table has no state abbreviation). Unrestricted attention, and
    # half of the training episodes from actual archived reports instead of artificial errors (flu act50 idea).
    r = R['covid']
    put('covid', 'T.att', derive(r['T'], spatial='attention'), 'T')
    put('covid', 'N.att', derive(r['ref.N'], spatial='attention'), 'ref.N')
    put('covid', 'T.act50', derive(r['T'], actual_share=0.5), 'T')
    put('covid', 'S.act50', derive(r['S'], actual_share=0.5), 'S')


ROUNDS['covid'][6] = dict(description='COVID search round 6 (2026-11-25): attention exchange on T and ref.N; half of the training '
                                      'episodes from actual archived reports on T and S.', build=covid6)


def rsv10():
    # Ball (production) trains on actual archived reports only; same idea on the national recipes, and attention exchange.
    r = R['rsv']
    put('rsv', 'Bw.nat.att', derive(r['Bw.nat'], spatial='attention'), 'Bw.nat')
    put('rsv', 'A4i.nat.att', derive(r['A4i.nat'], spatial='attention'), 'A4i.nat')
    put('rsv', 'Bw.nat.act50', derive(r['Bw.nat'], actual_share=0.5), 'Bw.nat')
    put('rsv', 'Bw.nat.act100', derive(r['Bw.nat'], actual_share=1.0), 'Bw.nat')
    put('rsv', 'A4i.nat.act50', derive(r['A4i.nat'], actual_share=0.5), 'A4i.nat')


ROUNDS['rsv'][10] = dict(description='RSV search round 10 (2026-11-25): attention exchange on Bw.nat and A4i.nat; training '
                                     'episodes from actual archived reports (half or all) on the national recipes.', build=rsv10)

def covid7():
    # 25 Nov 04:45: one network for flu, COVID and RSV together (fit_partition=all on the joint problem
    # us-respiratory-joint-short-term-coverage: same folds, panel with RSV admissions unobserved before Nov 2024, all six
    # targets as labels); scored on its COVID rows. Mechanism: more epidemics per network.
    r = R['covid']
    for root in ('T', 'ref.N'):
        put('covid', f'{root}.joint', derive(r[root], fit_partition='all'), root)


ROUNDS['covid'][7] = dict(description='COVID search round 7 (2026-11-25): one network trained on flu, COVID and RSV (joint problem).',
                          build=covid7)


def rsv11():
    # Same joint network for RSV, which has only two seasons of admissions (2024-25, 2025-26) to learn from.
    r = R['rsv']
    for root in ('Bw.nat', 'A4i.nat'):
        put('rsv', f'{root}.joint', derive(r[root], fit_partition='all'), root)


def rsv12():
    # 25 Nov 06:40: a mixture cannot combine members of different problems, so an all-joint RSV mixture needs joint versions
    # of the other production members too.
    r = R['rsv']
    for root in ('ref.Ball', 'ref.A4c0'):
        put('rsv', f'{root}.joint', derive(r[root], fit_partition='all'), root)


ROUNDS['rsv'][12] = dict(description='RSV search round 12 (2026-11-25): joint (flu+COVID+RSV) versions of ref.Ball and ref.A4c0.',
                         build=rsv12)
ROUNDS['rsv'][11] = dict(description='RSV search round 11 (2026-11-25): one network trained on flu, COVID and RSV (joint problem).',
                         build=rsv11)

def covid8():
    # 25 Nov 11:40: the joint network helped RSV ED share; the opposite direction, one network per target (admissions and
    # ED share fitted separately), on the candidate members.
    r = R['covid']
    for root in ('T', 'ref.N', 'S'):
        put('covid', f'{root}.pt', derive(r[root], fit_partition='target'), root)


ROUNDS['covid'][8] = dict(description='COVID search round 8 (2026-11-25): one network per target on T, ref.N and S.', build=covid8)


def rsv13():
    r = R['rsv']
    for root in ('Bw.nat', 'A4i.nat'):
        put('rsv', f'{root}.pt', derive(r[root], fit_partition='target'), root)
        put('rsv', f'{root}.lb16', derive(r[root], lookback=16), root)


ROUNDS['rsv'][13] = dict(description='RSV search round 13 (2026-11-25): one network per target and 16-week lookback on Bw.nat and '
                                     'A4i.nat.', build=rsv13)

def covid9():
    # 25 Nov 12:40: structural search exhausted. Amplitude augmentation (each training episode's inputs and labels rescaled
    # by exp(N(0, 0.3))): COVID seasons differ in size and the mixtures are too low at peaks; per-location noise on S.
    r = R['covid']
    for root in ('T', 'S', 'ref.N'):
        put('covid', f'{root}.amp3', derive(r[root], amplitude_sd=0.3), root)
    put('covid', 'S.local', derive(r['S'], noise='local'), 'S')


ROUNDS['covid'][9] = dict(description='COVID search round 9 (2026-11-25): amplitude augmentation on T, S, ref.N; per-location noise '
                                      'on S.', build=covid9)


def rsv14():
    r = R['rsv']
    for root in ('Bw.nat', 'A4i.nat'):
        put('rsv', f'{root}.amp3', derive(r[root], amplitude_sd=0.3), root)
    put('rsv', 'A4i.nat.local', derive(r['A4i.nat'], noise='local'), 'A4i.nat')


ROUNDS['rsv'][14] = dict(description='RSV search round 14 (2026-11-25): amplitude augmentation on Bw.nat and A4i.nat; per-location '
                                     'noise on A4i.nat.', build=rsv14)

def covid10():
    # 25 Nov 14:45: stronger amplitude augmentation on the two members it helped.
    r = R['covid']
    for root in ('T', 'ref.N'):
        put('covid', f'{root}.amp5', derive(r[root], amplitude_sd=0.5), root)


ROUNDS['covid'][10] = dict(description='COVID search round 10 (2026-11-25): amplitude augmentation 0.5 on T and ref.N.', build=covid10)

# Guard-only files: recipes guarded after they pass the main problem (children are not guarded otherwise).
GUARD = {'covid': {'g01': ['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'Tl', 'S'],
                   'g02': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(52, 60))),  # guard seeds for mixtures
                   'g03': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(60, 68))),
                   'g04': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(68, 76))),
                   'g05': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(76, 84))),
                   'g06': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(84, 92))),
                   'g07': (['T.amp3', 'ref.N.amp3', 'S.amp3'], list(range(44, 68))),
                   'g08': (['T.amp3', 'ref.N.amp3', 'S.amp3'], list(range(68, 92))),
                   # 25 Nov 16:40: T+N+S guard margin is narrow (+0.71%, 2 SE 0.70% at 48 seeds); 64 guard seeds
                   'g09': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(92, 108)))},
         'rsv': {'g01': ['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Rc', 'R1'],
                 'g03': ['Bwq', 'Bwq.smp'],
                 'g04': ['ref.Bw.gt', 'Bwq.gt', 'Bwq.smp.gt'],
                 'g05': ['Bw.nat'],
                 'g06': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bwq', 'Bwq.smp', 'Rc', 'Rc.real'], list(range(52, 60))),
                 'g07': (['A4i.nat', 'Bw.nat'], list(range(44, 60))),
                 'g08': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'A4i.nat', 'Bw.nat'], list(range(60, 68))),
                 'g09': (['Bw.nat.smp'], list(range(44, 68))),
                 'g10': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bw.nat', 'A4i.nat'], list(range(68, 76))),
                 'g11': (['Bw.nat.joint', 'A4i.nat.joint'], list(range(44, 68))),  # joint guard problem
                 # 25 Nov 19:40: 48 guard seeds for the six-member blend
                 'g12': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bw.nat', 'A4i.nat'], list(range(76, 92)))}}  # gt guard problem (us-rsv-2023-24-prescribed-coverage-gt)
RESEED = {'covid': {'rs01': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'Tl', 'S'], list(range(52, 60))),
                    'rs02': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S', 'N.smp'], list(range(60, 68))),
                    # 24 Nov 18:40: mixture decisions are noise-limited; 32 main seeds for the finalists and production
                    'rs03': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(68, 76))),
                    'rel': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(42, 62))),
                    'rel2': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(62, 82))),
                    # 25 Nov 10:40: 80 all-season fits per member of the candidates (as the flu draft release)
                    'rel3': (['T', 'ref.N', 'S'], list(range(82, 122))),
                    'rel4': (['ref.Ah', 'ref.pN', 'ref.Bh'], list(range(82, 122))),  # 25 Nov 20:40: for a blended release
                    # 25 Nov 21:40: forward-only check of the blend members on problems/us-covid-forward-2024-25-coverage.json
                    # (2024-25 held out, trained on 2022-23 and 2023-24 only; the main problem's 2024-25 fold also trains on
                    # 2025-26). Not possible for RSV: no RSV admissions before Nov 2024.
                    'fwd': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(44, 60))),
                    'relamp': (['T.amp3', 'ref.N.amp3', 'S.amp3'], list(range(42, 82))),
                    # 25 Nov 07:40: 40 seeds for the borderline COVID mixtures (production + T at -0.96%, T+N+S guard +1.02%)
                    'rs04': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(76, 84))),
                    # 25 Nov 09:40: T+N+S passes at 40 seeds by a narrow guard margin (+0.88%); 48 seeds on both checks
                    'rs05': (['ref.Ah', 'ref.pN', 'ref.N', 'ref.Bh', 'T', 'S'], list(range(84, 92))),
                    # 25 Nov 13:40: amplitude augmentation lowers T and ref.N (level at 8 seeds, better ED and US); members of an
                    # amplitude-augmented T+N+S on 24 seeds
                    'rs06': (['T.amp3', 'ref.N.amp3', 'S.amp3'], list(range(52, 68))),
                    'rs07': (['T.amp3', 'ref.N.amp3', 'S.amp3'], list(range(68, 92)))},
          'rsv': {'rs01': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Rc', 'R1'], list(range(52, 60))),
                  'rs02': (['Bwq', 'Bwq.smp'], list(range(52, 60))),
                  'rs03': (['Rc.real', 'Bw.nat'], list(range(52, 60))),
                  'rs04': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bwq', 'Bwq.smp', 'Rc', 'Rc.real'], list(range(60, 68))),
                  'rs05': (['A4i.nat'], list(range(52, 68))),
                  'rs06': (['Bw.nat'], list(range(60, 68))),
                  'rs07': (['Bw.nat.smp'], list(range(52, 68))),
                  # 24 Nov 22:45: all-season release fits (production problem, trained on 2022-23..2025-26), seeds 42-61
                  'rel': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bw.nat', 'Bw.nat.smp', 'A4i.nat'], list(range(42, 62))),
                  'rel2': (['ref.Ball', 'ref.A4c0', 'Bw.nat', 'Bw.nat.smp', 'A4i.nat'], list(range(62, 82))),
                  'rel3': (['ref.Ball', 'Bw.nat', 'ref.A4c0', 'A4i.nat'], list(range(82, 122))),
                  'rel4': (['ref.Bw', 'ref.A4i'], list(range(62, 122))),  # 25 Nov 18:40: for a blended release
                  # 25 Nov 01:40: 32 main seeds for the final RSV comparison
                  'rs08': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bw.nat', 'A4i.nat'], list(range(68, 76))),
                  # 25 Nov 05:40: joint networks (joint problem) improve RSV ED share; seeds for a mixture check
                  'rs09': (['Bw.nat.joint', 'A4i.nat.joint'], list(range(52, 68))),
                  # 25 Nov 17:40: the candidate's peak-window loss (+3.7% at 32 seeds) is marginal; 48 main seeds
                  'rs10': (['ref.Ball', 'ref.Bw', 'ref.A4c0', 'ref.A4i', 'Bw.nat', 'A4i.nat'], list(range(76, 92))),
                  # all-season joint release fits (problems/us-respiratory-joint-production-coverage.json), the ED-share option
                  'reljoint': (['ref.Ball.joint', 'Bw.nat.joint', 'ref.A4c0.joint', 'A4i.nat.joint'], list(range(42, 62)))}}


def build_all(p, upto=None):
    for n in sorted(ROUNDS[p]):
        if upto is None or n < upto:
            ROUNDS[p][n]['build']()


def write_guard(p, tag):
    build_all(p)
    names, seeds = GUARD[p][tag] if isinstance(GUARD[p][tag], tuple) else (GUARD[p][tag], SEEDS)
    study = dict(description=f'{p} search guard {tag} (2023-24 held out, artificial reports): {", ".join(names)}.', round=tag,
                 parents={k: PARENT[p][k] for k in names if k in PARENT[p]},
                 candidates={k: derive(R[p][k], error_reference='2025-2026') for k in names}, seeds=seeds)
    (HERE / f'{p}-guard-{tag}.json').write_text(json.dumps(study, indent=1) + '\n')
    print(f'{p} guard {tag}: {len(names)} recipes x {len(seeds)} seeds')


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

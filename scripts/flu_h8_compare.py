"""8-week training test (flu search, 21 Nov 2026): candidate A members trained on 8 future weeks (flu-s-h8 / flu-s-h8g)
against the same recipes trained on 4 weeks, seeds 44-51, on common tasks (first 4 horizons, corrected view, Oct-May).
    .venv/bin/python scripts/flu_h8_compare.py main|guard
"""
import csv, numpy as np, pandas as pd, sys
from pathlib import Path
LEV=np.array([.01,.025,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9,.95,.975,.99])
def runs(exps, name, seeds):
    out={}
    for e in exps:
        for r in csv.DictReader(open(f'data/experiments/{e}/runs.csv')):
            if r['name']==name and r['status']=='complete' and int(r['seed']) in seeds and r['seed'] not in out:
                out[r['seed']]=Path('data/experiments')/e/r['attempt']
    return out
def tasks(run):
    rows=[]
    for f in run.glob('eval_*/corrected/forecasts.npz'):
        d=np.load(f); q=d['quantiles'][:, :, :4, 0, :]; t=d['truth'][:, :4, 0, :]; m=d['mask'][:, :4, 0, :]; locs=[str(l) for l in d['locations']]
        lq=np.log1p(np.maximum(q,0)); lt=np.log1p(np.maximum(t,0))
        w=2*np.where(lt[None]>=lq, LEV[:,None,None,None]*(lt[None]-lq),(1-LEV[:,None,None,None])*(lq-lt[None])).mean(0)
        for i,c in enumerate(d['context_end']):
            if 6<=int(str(c)[5:7])<=9: continue
            for h in range(4):
                for l,loc in enumerate(locs):
                    if loc!='US' and m[i,h,l]: rows.append((f.parent.parent.name,str(c),h,loc,w[i,h,l]))
    return pd.DataFrame(rows,columns=['season','ref','h','loc','wis'])
prob=sys.argv[1]
main=(['flu-s-r01','flu-s-r06','flu-s-r10'],'flu-s-h8') if prob=='main' else (['flu-s-g01','flu-s-g06','flu-s-g10'],'flu-s-h8g')
for name in ['Bq.smp.ll1','ref.B','Ar.peak.nokinsa']:
    a=runs(main[0],name,range(44,52)); b=runs([main[1]],name,range(44,52))
    res=[]
    for s in sorted(set(a)&set(b)):
        x=tasks(a[s]); y=tasks(b[s]); j=x.merge(y,on=['season','ref','h','loc'],suffixes=('_4w','_8w')); j['seed']=s; res.append(j)
    j=pd.concat(res)
    t=j.groupby('season')[['wis_4w','wis_8w']].mean(); t['change_%']=(t.wis_8w/t.wis_4w-1)*100
    sd=j.groupby('seed')[['wis_4w','wis_8w']].mean(); 
    print(f'== {name} ({prob}), {j.seed.nunique()} seeds, {len(j)//j.seed.nunique()} tasks/seed'); print(t.round(4).to_string())
    print('  per-seed change:', (sd.wis_8w-sd.wis_4w).round(4).tolist())
    print('  by horizon:', j.groupby('h')[['wis_4w','wis_8w']].mean().round(4).values.tolist())

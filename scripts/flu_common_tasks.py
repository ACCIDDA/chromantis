"""Compare two experiments on exactly the same scored tasks (seed, reference date, horizon, state): states/DC WIS of
log(1 + admissions) by reference month. Used on 21 Nov 2026 for the in-season retraining test, whose rolling-origin
windows score fewer tasks than a season fold. Run in the Longleaf campaign folder:
    .venv/bin/python scripts/flu_common_tasks.py EXP_A EXP_B [VIEW]   (VIEW: corrected, half, ...; default the raw files)
"""
import glob, numpy as np, pandas as pd, sys
LEV=np.array([.01,.025,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9,.95,.975,.99])
def load(exp, view=sys.argv[3] if len(sys.argv) > 3 else ''):
    rows=[]
    for f in glob.glob(f'data/experiments/{exp}/*/s*/attempt-001/eval_*/' + (view + '/' if view else '') + 'forecasts.npz'):
        seed=f.split('/s')[1].split('/')[0]
        d=np.load(f); q=d['quantiles'][...,0,:]; t=d['truth'][...,0,:]; m=d['mask'][...,0,:]; locs=[str(l) for l in d['locations']]
        lq=np.log1p(np.maximum(q,0)); lt=np.log1p(np.maximum(t,0))
        pin=np.where(lt[None]>=lq, LEV[:,None,None,None]*(lt[None]-lq),(1-LEV[:,None,None,None])*(lq-lt[None])); w=2*pin.mean(0)
        for i,c in enumerate(d['context_end']):
            for h in range(4):
                for l,loc in enumerate(locs):
                    if loc!='US' and m[i,h,l]: rows.append((seed,str(c),h,loc,w[i,h,l]))
    return pd.DataFrame(rows,columns=['seed','ref','h','loc','wis'])
a=load(sys.argv[1]); b=load(sys.argv[2])
k=['seed','ref','h','loc']; j=a.merge(b,on=k,suffixes=('_frozen','_inseason'))
j['month']=j.ref.str[:7]
print('common tasks per seed:', len(j)//j.seed.nunique())
t=j.groupby('month')[['wis_frozen','wis_inseason']].mean(); t['change_%']=(t.wis_inseason/t.wis_frozen-1)*100; print(t.round(4))
o=j[['wis_frozen','wis_inseason']].mean(); print('all common tasks', o.round(4).to_dict(), 'change %', round((o.wis_inseason/o.wis_frozen-1)*100,2))
s=j.groupby('seed')[['wis_frozen','wis_inseason']].mean(); s['d']=s.wis_inseason-s.wis_frozen; print('per-seed change', s.d.round(4).tolist())
print(j.groupby('h')[['wis_frozen','wis_inseason']].mean().round(4))

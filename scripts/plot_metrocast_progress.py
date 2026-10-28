"""Plot the development-season search; no confirmation outcomes enter this figure."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
from chromantis.model.scenario import Scenario

ROOT = Path('experiments/metrocast-20261019')
COLORS = {'Direct local training': '#277DA8', 'State ILI pretraining': '#A66A28',
          'State flu ED pretraining': '#2C8B67'}


def main():
    path = ROOT / 'selection.csv'
    if not path.exists():
        print('No complete four-seed candidates yet.')
        return
    table = pd.read_csv(path).head(12).iloc[::-1].copy()
    if table.empty:
        return
    labels, families = [], []
    for row in table.itertuples():
        s = Scenario.from_string(row.scenario)
        fam = ('State ILI pretraining' if s.ili_training != 'none' else
               'State flu ED pretraining' if s.state_pretrain_steps else 'Direct local training')
        families.append(fam)
        labels.append(f'{row.name}\n{s.encoder}, width {s.width}, {s.lookback} weeks, {s.ed_transform}; '
                      f'{"local + state inputs" if s.covariate_set == "state" else "local inputs"}\n'
                      f'{s.epochs} epochs; location embedding {s.location_embedding}; '
                      f'population features {"on" if s.geography else "off"}')
    fig, ax = plt.subplots(figsize=(13, max(6, .62 * len(table) + 3)))
    ax.barh(range(len(table)), table['mean'] * 100, xerr=table['std'] * 100,
            color=[COLORS[f] for f in families], capsize=3)
    ax.set_yticks(range(len(table)), labels, fontsize=9)
    ax.set_xlabel('Weighted interval score in percentage points; lower is better\nError bars: standard deviation across fitting seeds')
    ax.set_title('Chromantis MetroCast development search\nTrain on 2022–23 and 2023–24 local flu ED; evaluate 2024–25', loc='left')
    ax.legend(handles=[Patch(facecolor=c, label=f) for f, c in COLORS.items()],
              loc='lower right', fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    caption = ('All branches learn future local flu-ED proportions; evaluation uses latest revised histories, not archived real-time inputs.\n'
               'ILI: pretrain on 2010–11 through 2021–22 state ILI, scaled from fitting data, then fit local flu-ED labels.\n'
               'State ED: pretrain on 2022–23 and 2023–24 own-state flu-ED labels, then fit local flu-ED labels.\n'
               'Scores pool supported local and state jurisdictions, October–May, horizons 0–3. The 2025–26 season is reserved for confirmation.')
    fig.text(.02, .015, caption, fontsize=9, va='bottom')
    fig.tight_layout(rect=(0, .14, 1, 1))
    out = Path('output/metrocast')
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / 'development-search.png', dpi=150)
    table.assign(training='2022-23 and 2023-24 local flu ED', evaluation='2024-25, latest revised histories',
                 pretraining=families).to_csv(out / 'development-search.csv', index=False)
    print(out / 'development-search.png')


if __name__ == '__main__':
    main()

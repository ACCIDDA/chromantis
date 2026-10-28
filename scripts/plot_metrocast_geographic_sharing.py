"""Matched geographic message scopes on revised full-season development inputs."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

root = Path("output/metrocast")
individual = pd.read_csv(root / "full-season-geographic-sharing-long-horizon.csv")
mixtures = pd.read_csv(root / "full-season-geographic-sharing-seed-mixtures.csv")
scopes = [("none", "Shared weights; no messages"),
          ("attention", "Messages across all 90 locations"),
          ("state_attention", "Messages within the same state"),
          ("region_attention", "Messages within the same HHS region")]
names = [f"local_history_{scope}_lag{lag}" for lag in (0, 1) for scope, _ in scopes]
labels = [f"{label}\nLatest fitting week {'visible' if lag == 0 else 'hidden'}"
          for lag in (0, 1) for _, label in scopes]
fig, axes = plt.subplots(1, 2, figsize=(14, 9), sharey=True)
y = np.arange(len(names))
for ax, metric in zip(axes, ["WIS percentage points", "Path energy percentage points"]):
    d = individual[individual.horizons.eq("0-33") & individual.metric.eq(metric)]
    d = d.groupby("name").value.agg(["mean", "std", "count"]).loc[names]
    assert d["count"].eq(4).all()
    m = mixtures[mixtures.horizons.eq("0-33") & mixtures.metric.eq(metric)].set_index("name").loc[names]
    ax.errorbar(d["mean"], y - .12, xerr=d["std"], fmt="o", capsize=3,
                color="#7c8792", label="Mean individual score ± seed SD")
    ax.scatter(m.value, y + .12, marker="D", color="#087f70",
               label="Equal four-seed intact-path mixture")
    for i, value in enumerate(m.value):
        ax.annotate(f"{value:.3f}", (value, i + .12), xytext=(5, -3),
                    textcoords="offset points", fontsize=8)
    ax.axhline(3.5, color="#b0b0b0", linewidth=.8)
    ax.set_xlabel(metric + "; lower is better")
    ax.grid(axis="x", alpha=.2)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_yticks(y, labels, fontsize=9)
axes[0].invert_yaxis()
axes[1].legend(fontsize=8, loc="lower right")
fig.suptitle("Full-season development: restricting local-history messages by geography")
fig.text(.02, .025,
         "All models: shared-weight 52-week linear-output MLP, width 64, 320 epochs, batch 2, 16 training draws; native-path loss weight 1.\n"
         "No location embeddings or external covariates. Message scopes use 90 locations, 14 state groups, or 8 HHS-region groups.\n"
         "Train on revised 2022–23/2023–24 histories and unchanged future local influenza ED proportion labels.\n"
         "Hidden-week treatment masks only the latest target-history week during fitting/inner validation; evaluation inputs stay unchanged.\n"
         "Evaluate revised inputs at October 26 and November 2/9/16, 2024, through June 14, 2025; 34 future weeks, equal location weighting.\n"
         "Individual scores use 128 intact paths per origin; mixtures pool 128 per seed, 512 total. SD describes seed variability, not a significance test.\n"
         "WIS measures weekly predictive distributions; energy scores intact trajectories. Development only, not archived inputs or actual ensemble ratios.\n"
         "2025–26 remains reserved. All architectures share learned weights across locations; only the message boundaries differ.", fontsize=9)
fig.tight_layout(rect=(0, .22, 1, .95))
destination = root / "full-season-geographic-sharing.png"
fig.savefig(destination, dpi=150)
print(destination)

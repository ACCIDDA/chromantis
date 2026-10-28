"""Utah development comparisons using the separate proposed weekly targets."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

root = Path("output/metrocast")
individual = pd.concat([pd.read_csv(root / f"utah-{part}-long-horizon.csv")
                        for part in ("proposed", "refine")])
mixtures = pd.concat([pd.read_csv(root / f"utah-{part}-seed-mixtures.csv")
                      for part in ("proposed", "refine")])
names = ["mlp52_linear_320epochs_none_lag0", "utah_path1_lag0",
         "utah_global_noise_lag0", "utah_history26_lag0",
         "utah_pooled_context_lag0", "utah_global_noise_lag1"]
labels = ["52-week history, path weight 0.25, local noise\nLatest fitting week visible",
          "52-week history, path weight 1, local noise\nLatest fitting week visible",
          "52-week history, path weight 0.25, global noise\nLatest fitting week visible",
          "26-week history, path weight 0.25, local noise\nLatest fitting week visible",
          "52-week history, pooled cross-location context\nLatest fitting week visible",
          "52-week history, path weight 0.25, global noise\nLatest fitting week hidden"]
fig, axes = plt.subplots(1, 2, figsize=(14, 8), sharey=True)
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
                    textcoords="offset points", fontsize=9)
    ax.set_xlabel(metric + "; lower is better")
    ax.grid(axis="x", alpha=.2)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_yticks(y, labels, fontsize=9)
axes[0].invert_yaxis()
axes[1].legend(fontsize=8)
fig.suptitle("Provisional Utah weekly targets: full-season model refinements")
fig.text(.02, .025,
         "All models: shared-weight linear-output MLP, width 64, 320 epochs, batch 2, 16 training draws; no embeddings or external covariates.\n"
         "Pooled-context model uses path weight 0.25 and local noise. Global-noise models omit the additional location-specific noise component.\n"
         "Train on revised 2022–23/2023–24 Utah histories and unchanged future local influenza ED proportion labels.\n"
         "Hidden-week treatment changes only fitting/inner-validation history; future labels and evaluation inputs stay unchanged.\n"
         "Evaluate revised inputs at October 26 and November 2/9/16, 2024, through June 14, 2025; 34 future weeks, equal 14-location weighting.\n"
         "Statewide Utah overlaps its 13 districts. Individual scores use 128 intact paths; mixtures pool 128 per seed, 512 total.\n"
         "Source: proposed weekly targets from PR587, pinned head 747e910, recorded as unmerged. No archived-input or actual ensemble comparison.\n"
         "Development only; 2025–26 remains reserved. Selection continues to use individual four-seed means.", fontsize=9)
fig.tight_layout(rect=(0, .25, 1, .95))
destination = root / "utah-full-season-refinement.png"
fig.savefig(destination, dpi=150)
print(destination)

"""Display cached whole trajectories from a development-only direct model."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from metrocast_seed_mixture import combine

root = Path("output/metrocast")
paths = [root / "trajectory-cache" / f"direct-path1-seed{seed}.npz" for seed in range(42, 46)]
meta, draws = combine(paths, horizons=34)
refs = pd.to_datetime(meta["context_end"].astype(str)) + pd.Timedelta(days=7)
origin = int(np.flatnonzero(refs == pd.Timestamp("2024-10-26"))[0])
dates = pd.to_datetime(meta["target_dates"][origin].astype(str))
assert len(dates) == 34 and dates[-1] == pd.Timestamp("2025-06-14")
assert draws.shape[1] == 512
locations = list(meta["locations"].astype(str))
chosen_locations = ["austin", "baltimore", "boston", "clt-area"]
names = pd.read_csv("data/metrocast/locations.csv").set_index("location").location_name
# Fixed indices chosen before inspecting curves, equal contributions by seed.
# The same indices are retained at every week and every displayed location.
chosen_draws = np.concatenate([seed * 128 + np.linspace(0, 127, 10, dtype=int)
                              for seed in range(4)])
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for ax, location in zip(axes.flat, chosen_locations):
    index = locations.index(location)
    samples = draws[origin, :, :, index] * 100
    truth = meta["truth"][origin, :, 0, index] * 100
    mask = meta["mask"][origin, :, 0, index].astype(bool)
    low, median, high = np.quantile(samples, [.1, .5, .9], axis=0)
    ax.fill_between(dates, low, high, color="#73bfb5", alpha=.25,
                    label="Pointwise 10–90% interval, all 512 draws")
    ax.plot(dates, samples[chosen_draws].T, color="#66899b", alpha=.15, linewidth=.7)
    ax.plot([], [], color="#66899b", linewidth=1, label="40 intact paths, 10 per seed")
    ax.plot(dates, median, color="#007b70", linewidth=2, label="Pointwise median")
    ax.plot(dates, np.where(mask, truth, np.nan), color="#252525", linewidth=2,
            label="Observed revised flu-ED percentage")
    ax.set_title(str(names.loc[location]), fontsize=11)
    ax.set_ylabel("Influenza ED visits (%)")
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(alpha=.18)
    ax.spines[["top", "right"]].set_visible(False)
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .93), ncol=2, fontsize=9)
fig.suptitle("Intact 34-week development trajectories from October 26, 2024", fontsize=15)
fig.text(.02, .025,
         "Model: shared-weight 52-week linear-output MLP, width 64, 320 epochs, residual decoder depth 2, no location embeddings;\n"
         "original Hub own-state covariates, local latent noise, batch 2, 16 training draws, weekly + native-path loss weight 1.\n"
         "Train on revised 2022–23/2023–24 histories with latest fitting week visible, learning unchanged future local flu-ED proportion labels.\n"
         "Evaluation inputs: revised histories ending October 19, 2024. Future observations shown only for development evaluation, through June 14, 2025.\n"
         "Uniform mixture of four independently fitted seeds: 128 intact draws each. Thin lines keep their draw identity across all 34 weeks and locations.\n"
         "Median and interval are pointwise summaries, not individual trajectories. Locations and displayed draw indices were chosen before inspecting curves.\n"
         "These HSA/regional targets are not historical county targets. No archived operational or actual-ensemble claim; 2025–26 is reserved.", fontsize=9)
fig.tight_layout(rect=(0, .21, 1, .86))
destination = root / "full-season-joint-trajectories.png"
fig.savefig(destination, dpi=150)
print(destination)

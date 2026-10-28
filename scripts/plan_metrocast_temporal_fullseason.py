"""Compare temporal encoders using an existing 34-week development recipe."""
from dataclasses import replace
from datetime import datetime, timezone
import fcntl
import json
import subprocess

from chromantis.model.scenario import Scenario
import metrocast_tree as tree


def main():
    with (tree.ROOT / "tree.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        assert datetime.now(timezone.utc).timestamp() < tree.STOP - 8 * 3600
        state = tree.load_state()
        if state.get("temporal_fullseason_development"):
            print(state["temporal_fullseason_development"])
            return
        original = json.loads((tree.ROOT / "round-073-full-season-direct-refine.json").read_text())
        candidates, parents = {}, {}
        for lag in (0, 1):
            parent = original["candidates"][f"no_embedding_path1_lag{lag}"]
            for encoder in ("mlp", "conv", "multiscale_conv", "gru", "attention"):
                label = f"temporal_{encoder}_lag{lag}"
                candidates[label] = replace(Scenario.from_string(parent), encoder=encoder,
                                            decoder_blocks=0).scenario_string
                parents[label] = parent
        protocol = {key: value for key, value in original.items()
                    if key not in ("seeds", "candidates", "parents")}
        protocol["selection"] = (
            "Development only: replace the MLP history encoder by temporal convolution, "
            "multiscale convolution, GRU, or temporal attention. Use the original residual2 "
            "output head (decoder_blocks=0) for every encoder, including new matched MLP "
            "references: deeper decoder blocks require MLP encoders in the current implementation. "
            "Keep width64, 320 epochs, batch2, members16, path "
            "weight1, no geography embeddings, original Hub state covariates, 34 outputs. "
            "Compare mean four-seed whole-season WIS and path energy on four early2024 "
            "origins; uniform seed mixtures are separate. No 2025-26 outcomes.")
        name = tree.plan(state, candidates, parents, [42, 43, 44, 45],
                         stage="full-season-direct-refine",
                         problem="problems/metrocast-flu-full-season.json",
                         protocol=protocol)
        state["temporal_fullseason_development"] = name
        tree.save(tree.STATE, state)
        command = ["sbatch", f"--job-name={name}-score",
                   "scripts/metrocast_full_season_score.sbatch", name, "--wait"]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        with (tree.ROOT / "manager-commands.sh").open("a") as out:
            out.write("\n" + " ".join(command) + "\n# " + result.stdout.strip() + "\n")
        print(name)
        print(result.stdout.strip())


if __name__ == "__main__":
    main()

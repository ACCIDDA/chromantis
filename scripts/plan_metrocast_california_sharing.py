"""Plan matched California message-sharing fits on the existing winter split."""
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
        if state.get("california_sharing_development"):
            print(state["california_sharing_development"])
            return
        original = json.loads((tree.ROOT / "round-065-california-pilot.json").read_text())
        candidates, parents = {}, {}
        for pretrain in ("direct", "ILI_pretraining"):
            for lag in (0, 1):
                parent = original["candidates"][f"{pretrain}_historylag{lag}_path0"]
                for spatial in ("attention", "pooled"):
                    label = f"california_{pretrain}_{spatial}_lag{lag}"
                    candidates[label] = replace(Scenario.from_string(parent), spatial=spatial).scenario_string
                    parents[label] = parent
        protocol = {key: value for key, value in original.items()
                    if key not in ("seeds", "candidates", "parents")}
        protocol["inputs"] += (
            " New attention or pooled messages expose observed histories across the six regions "
            "and overlapping statewide location. No new external covariates; all model weights "
            "remain shared. Matched no-message fits already exist in r065.")
        name = tree.plan(state, candidates, parents, [42, 43, 44, 45],
                         stage="california-pilot",
                         problem="problems/metrocast-california-pilot.json",
                         protocol=protocol)
        state["california_sharing_development"] = name
        tree.save(tree.STATE, state)
        command = ["sbatch", f"--job-name={name}-score",
                   "scripts/metrocast_california_score.sbatch", name]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        with (tree.ROOT / "manager-commands.sh").open("a") as out:
            out.write("\n" + " ".join(command) + "\n# " + result.stdout.strip() + "\n")
        print(name)
        print(result.stdout.strip())


if __name__ == "__main__":
    main()

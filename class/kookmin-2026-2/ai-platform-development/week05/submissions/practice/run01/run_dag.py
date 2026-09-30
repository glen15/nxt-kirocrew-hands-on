"""DAG runner for the warehouse aggregation pipeline.

Encodes the dependency graph explicitly:

    warehouse_a ─┐
    warehouse_b ─┼──▶ integrate
    warehouse_c ─┘

The three warehouse nodes (A, B, C) are mutually independent and run in
PARALLEL (one worker process each). The integration node depends on all three
and runs only after every warehouse node has completed successfully.

Each node is one of the standalone task scripts in this directory, invoked in a
fresh subprocess (python3 <script>) so a node's failure is isolated and its
stdout/stderr is captured. Running as subprocesses (rather than importing the
modules) keeps each node a true independent unit of work, matching the task
scripts' "run standalone" contract.

Run:  python3 run_dag.py
Exit code is 0 only when the whole DAG succeeds.
"""
from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent

# Explicit dependency graph: node -> (script, list of prerequisite node names).
# A/B/C have no prerequisites (independent); integrate depends on all three.
DAG: dict[str, tuple[str, list[str]]] = {
    "warehouse_a": ("task_warehouse_a.py", []),
    "warehouse_b": ("task_warehouse_b.py", []),
    "warehouse_c": ("task_warehouse_c.py", []),
    "integrate": ("task_integrate.py", ["warehouse_a", "warehouse_b", "warehouse_c"]),
}


def run_node(name: str, script: str) -> tuple[str, int, str]:
    """Run one DAG node as a subprocess. Returns (name, returncode, output)."""
    proc = subprocess.run(
        [sys.executable, script],
        cwd=RUN_DIR,
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return name, proc.returncode, output.strip()


def run_group(names: list[str]) -> None:
    """Run a set of independent nodes in parallel; raise if any node fails."""
    with ThreadPoolExecutor(max_workers=len(names)) as pool:
        futures = [pool.submit(run_node, n, DAG[n][0]) for n in names]
        failures: list[str] = []
        for fut in futures:
            name, code, output = fut.result()
            status = "OK" if code == 0 else f"FAILED(exit={code})"
            print(f"[{name}] {status}")
            if output:
                for line in output.splitlines():
                    print(f"    {line}")
            if code != 0:
                failures.append(name)
    if failures:
        raise RuntimeError(f"DAG node(s) failed: {', '.join(failures)}")


def topological_layers() -> list[list[str]]:
    """Return execution layers via Kahn's algorithm; nodes in a layer are
    independent and run in parallel. Also validates the graph is acyclic."""
    remaining = {name: set(deps) for name, (_, deps) in DAG.items()}
    layers: list[list[str]] = []
    while remaining:
        ready = sorted(n for n, deps in remaining.items() if not deps)
        if not ready:
            raise RuntimeError(f"cycle detected in DAG among: {sorted(remaining)}")
        layers.append(ready)
        for n in ready:
            del remaining[n]
        for deps in remaining.values():
            deps.difference_update(ready)
    return layers


def main() -> int:
    layers = topological_layers()
    print("DAG execution plan (parallel within each layer):")
    for i, layer in enumerate(layers, 1):
        print(f"  layer {i}: {', '.join(layer)}")
    print()

    for i, layer in enumerate(layers, 1):
        print(f"== running layer {i}: {', '.join(layer)} ==")
        run_group(layer)
        print()

    print("DAG completed successfully.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f"DAG failed: {exc}", file=sys.stderr)
        sys.exit(1)

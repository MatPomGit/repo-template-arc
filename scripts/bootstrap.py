"""Convenience entrypoint: pinned submodule checkout or read-only live audit."""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(argv:list[str]|None=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--mode",choices=("reproduce","audit-live"),required=True)
    p.add_argument("--require-current",action="store_true")
    a=p.parse_args(argv)
    root=a.root.resolve()
    if a.mode=="audit-live":
        try:
            from check_freshness import run
        except ImportError:
            from scripts.check_freshness import run
        return run(root,a.require_current)
    if not (root/".gitmodules").is_file():
        print("NO_SUBMODULES: programme registry uses links only; nothing to fetch")
        return 0
    if not (root/".git").exists():
        print("BLOCKED: requires an actual Git checkout for submodules")
        return 2
    env=os.environ.copy()
    env["GIT_TERMINAL_PROMPT"]="0"
    try:
        r=subprocess.run(["git","-C",str(root),"submodule","update","--init","--recursive"],
            env=env,check=False,timeout=120)
    except (FileNotFoundError,OSError,subprocess.TimeoutExpired):
        print("UNAVAILABLE: git or credentials inaccessible")
        return 3
    if r.returncode != 0:
        print("UNAVAILABLE: submodule checkout failed; check approved GitHub App access")
        return 3
    print("PINNED_OK: submodules fetched at commits recorded by parent Git")
    return 0

if __name__=="__main__": sys.exit(main())

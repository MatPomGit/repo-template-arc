"""Compare registered programme snapshots with remote default branches, read-only."""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from validate_repository import github_repo_url
except ImportError:
    from scripts.validate_repository import github_repo_url


def inspect_project(project: dict, timeout: int = 15) -> dict:
    """No checkout, branch update, credential access or code execution."""
    result = {"project_id": project.get("id"), "repository":project.get("repository"),
              "snapshot_sha":project.get("snapshot_sha"), "remote_head_sha":None,
              "status":"UNAVAILABLE"}
    url = project.get("url", "")
    if not github_repo_url(project.get("repository", ""),url):
        result["reason"] = "invalid_github_url"; return result
    branch = project.get("default_branch", "")
    if not isinstance(branch,str) or not re.fullmatch(r"[A-Za-z0-9._/-]{1,100}",branch) or ".." in branch or branch.startswith("-"):
        result["reason"] = "invalid_ref"; return result
    env=os.environ.copy()
    env["GIT_TERMINAL_PROMPT"]="0"
    env["GIT_OPTIONAL_LOCKS"]="0"
    try:
        r=subprocess.run(["git","ls-remote","--exit-code",url,"refs/heads/"+branch],
             text=True,capture_output=True,timeout=timeout,env=env,check=False)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        result["reason"]="git_unavailable_or_timeout"; return result
    if r.returncode != 0:
        # Never emit stderr: it could contain credential or private-repo details.
        result["reason"]="access_or_remote_error"; return result
    m=re.fullmatch(r"([0-9a-f]{40})\trefs/heads/"+re.escape(branch)+r"\n?",r.stdout)
    if not m:
        result["reason"]="unexpected_remote_response"; return result
    sha=m.group(1)
    result["remote_head_sha"]=sha
    snapshot=project.get("snapshot_sha")
    if not snapshot:
        result["status"]="UNPINNED"
    elif sha == snapshot:
        result["status"]="CURRENT"
    else:
        result["status"]="STALE"
    return result


def run(root:Path,require_current:bool=False,timeout:int=15) -> int:
    manifest=json.loads((root/"portfolio/projects.json").read_text(encoding="utf-8"))
    items=manifest.get("projects",[])
    if not items:
        print("NO_PROJECTS: registry contains no projects; this is not a complete live audit")
        return 2 if require_current else 0
    results=[inspect_project(p,timeout) for p in items]
    for r in results:
        print(f"{r['project_id']}: {r['status']} snapshot={r['snapshot_sha'] or 'NONE'} remote={r['remote_head_sha'] or 'UNKNOWN'}")
    if any(r["status"]=="UNAVAILABLE" for r in results): return 3
    if require_current and any(r["status"]!="CURRENT" for r in results): return 2
    return 0

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-current",action="store_true")
    parser.add_argument("--timeout",type=int,default=15)
    args=parser.parse_args()
    sys.exit(run(args.root,args.require_current,max(1,min(args.timeout,60))))

"""Conservative ARC v1 to v2 migration: inventory, plan, explicit apply."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from _generator_io import write_batch
from validate_registry_v2 import MSC, safe_path, validate_registry_v2
from validate_repository import safe_public_page_url, validate

ALLOWED_STAGES={"concept","protocol","preregistered","collection","analysis",
                "draft","submitted","accepted","published","archived","withdrawn"}
ALLOWED_RESEARCH={"planned","active","paused","completed","deferred","archived"}
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA=re.compile(r"^[a-f0-9]{40}$")


def load(root: Path, name: str) -> dict:
    path=root/name
    if path.is_symlink() or not path.is_file() or path.stat().st_size>2_000_000:
        raise ValueError("Unsafe or missing source file: "+name)
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise ValueError("Expected JSON object: "+name)
    return obj


def source_files(root: Path) -> list[str]:
    result=[]
    for dirname in ("papers","manuscripts"):
        directory=root/dirname
        if directory.is_symlink():
            raise ValueError("Unsafe manuscript root: "+dirname)
        if not directory.is_dir():
            continue
        for item in directory.rglob("main.tex"):
            if (item.is_symlink() or not item.is_file() or
                    not item.resolve().is_relative_to(root.resolve())):
                raise ValueError("Unsafe manuscript source")
            path=item.relative_to(root).as_posix()
            if not safe_path(path):
                raise ValueError("Invalid manuscript source path")
            result.append(path)
            if len(result)>5000:
                raise ValueError("Too many manuscript sources")
    return sorted(result)


def inventory(root: Path) -> dict:
    root=root.absolute()
    meta=load(root,"program.json")
    reg=load(root,"portfolio/papers.json")
    paths=source_files(root)
    return {"schema_version":meta.get("schema_version"),
            "programme":meta.get("programme"),
            "registered_papers":len(reg.get("papers",[])),
            "local_sources":paths,"local_source_count":len(paths)}


def _convert(root: Path, repository: str, mapping: dict):
    """Derive v2 content without modifying the target."""
    meta=load(root,"program.json")
    projects=load(root,"portfolio/projects.json")
    papers=load(root,"portfolio/papers.json")
    deps=load(root,"portfolio/dependencies.json")
    areas=load(root,"areas/index.json")
    problems=[]
    if meta.get("schema_version")!=1:
        raise ValueError("Migration requires schema_version 1")
    if any(obj.get("schema_version")!=1 for obj in (projects,papers,deps)):
        raise ValueError("Mixed registry schema versions")
    if not REPO.fullmatch(repository) or repository.split("/")[-1]!=meta.get("programme"):
        raise ValueError("Repository identity differs from programme")
    if meta.get("repository_visibility") not in ("public","private"):
        raise ValueError("Repository visibility not configured")
    if mapping.get("schema_version")!=1 or set(mapping)-{"schema_version","articles","sources"}:
        raise ValueError("Invalid migration mapping schema")
    article_map=mapping.get("articles",{})
    source_map=mapping.get("sources",{})
    if not isinstance(article_map,dict) or not isinstance(source_map,dict):
        raise ValueError("Migration mapping must contain objects")
    if not isinstance(projects.get("projects"),list) or not isinstance(papers.get("papers"),list):
        raise ValueError("Missing project/paper arrays")
    project_lookup={p.get("id"):p for p in projects["projects"] if isinstance(p,dict)}
    valid_areas={a.get("id") for a in areas.get("lines",[]) if isinstance(a,dict)}
    sources=source_files(root)
    local_roots={source.split("/")[0] for source in sources}
    if len(local_roots)>1:
        problems.append("Mixed papers/ and manuscripts/ roots; migrate layouts first")
    manuscript_root=next(iter(local_roots)) if local_roots else "manuscripts"
    out=[]
    consumed=set()
    old_ids=set()
    for old in papers["papers"]:
        if not isinstance(old,dict) or not isinstance(old.get("id"),str):
            problems.append("Invalid legacy paper")
            continue
        old_id=old["id"]
        if old_id in old_ids:
            problems.append("Duplicate legacy ID: "+old_id)
            continue
        old_ids.add(old_id)
        spec=article_map.get(old_id,{})
        if not isinstance(spec,dict):
            problems.append("Invalid map entry: "+old_id)
            continue
        ident=spec.get("new_id",old_id)
        if not isinstance(ident,str) or not MSC.fullmatch(ident):
            problems.append("MSC identity mapping required: "+old_id)
            continue
        stage=spec.get("publication_stage",old.get("stage"))
        if stage not in ALLOWED_STAGES:
            problems.append("Invalid stage: "+old_id)
            continue
        status=spec.get("research_state","planned" if stage=="concept" else None)
        if status not in ALLOWED_RESEARCH:
            problems.append("Research state needs explicit mapping: "+old_id)
            continue
        mode=spec.get("mode","external")
        if mode=="external":
            project=project_lookup.get(old.get("owner_project_id"))
            if project is None or old.get("canonical_repository")!=project.get("repository"):
                problems.append("External canonical project mismatch: "+old_id)
                continue
            owner={"mode":"external","repository":project["repository"],
                   "project_id":project["id"]}
            line=spec.get("area",project.get("line"))
            role=project.get("role","primary")
            old_path=old.get("manuscript_path")
            manuscript={"path":old_path,"format":"latex"} if old_path else None
        elif mode=="local":
            local_path=spec.get("path")
            if local_path not in sources:
                problems.append("Local source missing for: "+old_id)
                continue
            consumed.add(local_path)
            owner={"mode":"local","repository":repository,"project_id":None}
            line=spec.get("area")
            role="primary"
            manuscript={"path":local_path,"format":"latex"}
        else:
            problems.append("Invalid canonical ownership: "+old_id)
            continue
        if line not in valid_areas:
            problems.append("Unknown area for: "+old_id)
            continue
        if spec.get("public_listing") is True:
            problems.append("Migration cannot automatically approve public listing: "+old_id)
        out.append({"id":ident,"title":old.get("title"),"area":line,
                    "research_state":status,"publication_stage":stage,"relation":role,
                    "owner":owner,"manuscript":manuscript,"study_plan":None,
                    "public_listing":False,"public_summary":None,
                    "doi":old.get("doi"),"preprint_url":old.get("preprint_url"),
                    "preregistration_url":old.get("preregistration_url"),
                    "publication_url":old.get("publication_url"),
                    "stage_evidence":old.get("stage_evidence")})

    for path in sources:
        if path in consumed:
            continue
        spec=source_map.get(path)
        parent=Path(path).parent.name
        if spec is None:
            # Existing external manuscript may coexist with a local, noncanonical plan.
            ident=parent
            linked=next((x for x in out if x["id"]==ident),None)
            marker=article_map.get(ident,{})
            if (linked and linked["owner"]["mode"]=="external" and
                    isinstance(marker,dict) and
                    marker.get("local_source_role")=="noncanonical_plan"):
                consumed.add(path)
                continue
            problems.append("Unmapped local source: "+path)
            continue
        if not isinstance(spec,dict) or spec.get("mode")!="local":
            problems.append("Explicit local source mapping required: "+path)
            continue
        ident=spec.get("id",parent)
        if not isinstance(ident,str) or not MSC.fullmatch(ident):
            problems.append("Valid new MSC ID required: "+path)
            continue
        if ident in {x["id"] for x in out}:
            problems.append("Colliding local MSC ID: "+ident)
            continue
        title=spec.get("title")
        area=spec.get("area")
        status=spec.get("research_state","planned")
        stage=spec.get("publication_stage","concept")
        if not isinstance(title,str) or not title.strip() or area not in valid_areas:
            problems.append("Verified title and area required: "+path)
            continue
        if status not in ALLOWED_RESEARCH or stage not in ALLOWED_STAGES:
            problems.append("Invalid local research/publication state: "+path)
            continue
        if spec.get("public_listing") is True:
            problems.append("Migration cannot grant public listing: "+path)
        plan=path.rsplit("/",1)[0]+"/study.yaml"
        if not (root/plan).is_file():
            plan=None
        out.append({"id":ident,"title":title,"area":area,
                    "research_state":status,"publication_stage":stage,"relation":"primary",
                    "owner":{"mode":"local","repository":repository,"project_id":None},
                    "manuscript":{"path":path,"format":"latex"},
                    "study_plan":plan,"public_listing":False,"public_summary":None,
                    "doi":None,"preprint_url":None,"preregistration_url":None,
                    "publication_url":None,"stage_evidence":None})
        consumed.add(path)
    for key in article_map:
        if key not in old_ids:
            problems.append("Unknown legacy ID in mapping: "+key)
    for key in source_map:
        if key not in sources:
            problems.append("Unknown manuscript path in mapping: "+key)

    meta2=dict(meta)
    # The data schema changes; the provenance version of the template does not.
    meta2.update(schema_version=2,
                 repository_full_name=repository,manuscript_root=manuscript_root)
    projects2={"schema_version":2,"projects":projects["projects"]}
    papers2={"schema_version":2,"papers":sorted(out,key=lambda x:x["id"])}
    deps2=dict(deps)
    deps2["schema_version"]=2
    if len(out)!=len({p["id"] for p in out}):
        problems.append("Duplicate MSC IDs in conversion")
    projects_map={p["id"]:p["repository"] for p in projects["projects"]
                  if isinstance(p,dict) and "id" in p and "repository" in p}
    problems.extend(validate_registry_v2(
        root,meta2,papers2["papers"],deps2,projects_map,valid_areas,
        safe_public_page_url))
    state_path=root/"PROJECT_STATE.yaml"
    state=state_path.read_text(encoding="utf-8")
    for old,new in (("schema_version: 1","schema_version: 2"),):
        if old not in state:
            problems.append("State migration marker missing: "+old)
        else:
            state=state.replace(old,new,1)
    count=re.search(r"^papers_registered: (\d+)$",state,re.M)
    if count is None or int(count.group(1))!=len(papers["papers"]):
        problems.append("Legacy paper count inconsistent with PROJECT_STATE")
    else:
        state=state.replace(count.group(0),"papers_registered: "+str(len(out)),1)
    if out and "phase: scaffold" in state:
        state=state.replace("phase: scaffold","phase: planned",1)
    payload={
        root/"program.json":json.dumps(meta2,ensure_ascii=False,indent=2)+"\n",
        root/"portfolio/projects.json":json.dumps(projects2,ensure_ascii=False,indent=2)+"\n",
        root/"portfolio/papers.json":json.dumps(papers2,ensure_ascii=False,indent=2)+"\n",
        root/"portfolio/dependencies.json":json.dumps(deps2,ensure_ascii=False,indent=2)+"\n",
        root/"PROJECT_STATE.yaml":state,
    }
    return payload,sorted(set(problems)),len(sources),len(out)


def _check_git(root: Path, expected: str):
    if not SHA.fullmatch(expected):
        raise ValueError("An exact expected 40-character SHA is required")
    try:
        actual=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                      text=True,timeout=10).strip()
        dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain",
                                       "--untracked-files=no"],text=True,timeout=10).strip()
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
        raise ValueError("Git HEAD could not be verified") from error
    if actual!=expected or dirty:
        raise ValueError("Git SHA mismatch or tracked working tree modified")
    # The tracked working tree may be clean while source_files() discovers
    # untracked main.tex files. Require every migrated source in expected HEAD.
    sources = source_files(root)
    if sources:
        try:
            tree = subprocess.run(
                ["git", "-C", str(root), "ls-tree", "-r", "-z", expected,
                 "--", "papers", "manuscripts"],
                capture_output=True, timeout=15, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValueError("Git manuscript tree could not be verified") from error
        if tree.returncode:
            raise ValueError("Git manuscript tree could not be verified")
        committed = set()
        for entry in tree.stdout.split(b"\0"):
            if not entry:
                continue
            header, separator, name = entry.partition(b"\t")
            if separator and re.fullmatch(rb"100(?:644|755) blob [0-9a-f]{40}", header):
                committed.add(name.decode("utf-8"))
        missing = sorted(set(sources) - committed)
        if missing:
            raise ValueError("Uncommitted manuscript source absent from expected SHA: "
                             + ", ".join(missing[:5]))


def execute(root: Path,mode: str,repository: str | None=None,
            mapping: dict | None=None,expected_sha: str | None=None,
            confirm_public_sources: bool=False) -> dict:
    root=root.absolute()
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Invalid ARC root")
    report=inventory(root)
    if mode=="inventory":
        return {"status":"INVENTORY",**report}
    if mode not in ("plan","apply"):
        raise ValueError("Unsupported migration mode")
    if report["schema_version"]==2:
        # A schema marker does not certify a completed migration.
        # Fail closed when registries, state, sources or publication boundaries disagree.
        issues=validate(root)
        if issues:
            return {"status":"BLOCKED",**report,"blockers":issues}
        return {"status":"ALREADY_V2",**report}
    if not repository:
        raise ValueError("Canonical repository is required")
    payload,blockers,files,papers=_convert(root,repository,mapping or {"schema_version":1})
    result={"status":"BLOCKED" if blockers else "READY",
            "source_count":files,"article_count":papers,
            "files_to_update":sorted(str(path.relative_to(root)) for path in payload),
            "blockers":blockers}
    if mode=="plan" or blockers:
        return result
    _check_git(root,expected_sha or "")
    if (load(root,"program.json").get("repository_visibility")=="public" and
            files>0 and not confirm_public_sources):
        raise ValueError("Public local sources require explicit approval")
    old={path:path.read_text(encoding="utf-8") for path in payload}
    write_batch(root,payload)
    issues=validate(root)
    if issues:
        write_batch(root,old)
        raise ValueError("Post-migration validation failed; restored original records: "+
                         "; ".join(issues[:4]))
    result["status"]="APPLIED"
    result["source_sha"]=expected_sha
    return result


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mode",required=True,choices=("inventory","plan","apply"))
    parser.add_argument("--repository")
    parser.add_argument("--map",dest="mapping",type=Path)
    parser.add_argument("--expected-sha")
    parser.add_argument("--confirm-public-sources",action="store_true")
    args=parser.parse_args(argv)
    try:
        mapping=None
        if args.mapping is not None:
            if args.mapping.is_symlink() or args.mapping.stat().st_size>1_000_000:
                raise ValueError("Unsafe mapping file")
            mapping=json.loads(args.mapping.read_text(encoding="utf-8"))
        result=execute(args.root,args.mode,repository=args.repository,mapping=mapping,
                       expected_sha=args.expected_sha,
                       confirm_public_sources=args.confirm_public_sources)
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,"MIGRATION BLOCKED: "+str(error)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"] in ("INVENTORY","READY","APPLIED","ALREADY_V2") else 1


if __name__=="__main__":
    raise SystemExit(main())

"""Pure offline ARC registry v2 checks. The v1 validator is retained for migration."""
from __future__ import annotations
import re
from pathlib import Path

MSC=re.compile(r"^MSC-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA40=re.compile(r"^[a-f0-9]{40}$")
SHA256=re.compile(r"^[a-f0-9]{64}$")
DOI=re.compile(r"^10\.\d{4,9}/\S+$")
DATE=re.compile(r"^\d{4}-\d{2}-\d{2}$")
STAGES={"concept","protocol","preregistered","collection","analysis","draft","submitted",
        "accepted","published","archived","withdrawn"}
STATES={"planned","active","paused","completed","deferred","archived"}
EVIDENCE={"submitted":"submission_receipt","accepted":"editorial_decision",
          "published":"publication_record"}
PAPER_FIELDS={"id","title","area","research_state","publication_stage","relation","owner",
              "manuscript","study_plan","public_listing","doi","preprint_url",
              "preregistration_url","publication_url","stage_evidence"}
OWNER_FIELDS={"mode","repository","project_id"}
MANUSCRIPT_FIELDS={"path","format","commit_sha","blob_sha"}
DEP_FIELDS={"paper_id","project_id","ref","version","sha","role","contract_path",
            "validation_status","notes"}


def is_in(value, choices):
    return isinstance(value,str) and value in choices


def safe_path(value):
    return (isinstance(value,str) and bool(value) and "\\" not in value
            and not value.startswith("/") and not Path(value).is_absolute()
            and all(x not in ("", ".", "..") for x in value.split("/"))
            and all(ord(x)>=32 for x in value))


def file_inside(root, path):
    if not safe_path(path):
        return False
    current=root
    for part in path.split("/"):
        current=current/part
        if current.is_symlink():
            return False
    return current.is_file()


def validate_registry_v2(root,meta,papers,dependencies,project_repos,lines,safe_url):
    issues=[]
    paper_ids=set()
    for p in papers:
        if not isinstance(p,dict):
            issues.append("Invalid v2 paper record type")
            continue
        ident=p.get("id")
        name=ident if isinstance(ident,str) else "?"
        if set(p)!=PAPER_FIELDS:
            issues.append(f"Undeclared paper metadata or missing v2 fields: {name}")
        if not isinstance(ident,str) or not MSC.fullmatch(ident) or ident in paper_ids:
            issues.append(f"Invalid or duplicate MSC paper id: {name}")
        if isinstance(ident,str):
            paper_ids.add(ident)
        if not isinstance(p.get("title"),str) or not p["title"].strip():
            issues.append(f"Missing paper title: {name}")
        if not isinstance(p.get("area"),str) or p["area"] not in lines:
            issues.append(f"Unknown paper research area: {name}")
        if not is_in(p.get("research_state"),STATES):
            issues.append(f"Unknown paper research state: {name}")
        stage=p.get("publication_stage")
        if not is_in(stage,STAGES):
            issues.append(f"Unknown paper publication stage: {name}")
        if p.get("relation") not in ("primary","related"):
            issues.append(f"Invalid paper relation: {name}")
        if not isinstance(p.get("public_listing"),bool):
            issues.append(f"Invalid paper public_listing: {name}")
        elif p["public_listing"] and meta.get("repository_visibility")!="public":
            issues.append(f"Public paper listing requires public ARC source: {name}")

        owner=p.get("owner")
        mode=None
        if not isinstance(owner,dict) or set(owner)!=OWNER_FIELDS:
            issues.append(f"Invalid paper canonical owner: {name}")
        else:
            mode=owner.get("mode")
            r=owner.get("repository")
            pid=owner.get("project_id")
            if not isinstance(r,str) or not REPO.fullmatch(r):
                issues.append(f"Invalid canonical repository: {name}")
            if mode=="local":
                if pid is not None or p.get("relation")!="primary":
                    issues.append(f"Invalid local ownership: {name}")
                programme=meta.get("programme")
                if not isinstance(programme,str) or programme=="arc-REPLACE" or (
                    not isinstance(r,str) or not r.endswith("/"+programme)):
                    issues.append(f"Local owner must match configured ARC programme: {name}")
                if meta.get("repository_visibility")=="unconfigured":
                    issues.append(f"Configure ARC visibility before local manuscript: {name}")
            elif mode=="external":
                if not isinstance(pid,str) or project_repos.get(pid)!=r:
                    issues.append(f"Unknown canonical project for paper: {name}")
            else:
                issues.append(f"Unknown manuscript ownership mode: {name}")
        manuscript=p.get("manuscript")
        if manuscript is None:
            if mode=="local":
                issues.append(f"Local paper requires manuscript path: {name}")
        elif not isinstance(manuscript,dict) or set(manuscript)-MANUSCRIPT_FIELDS:
            issues.append(f"Invalid manuscript metadata: {name}")
        else:
            path=manuscript.get("path")
            form=manuscript.get("format")
            if not safe_path(path) or form not in ("latex","markdown"):
                issues.append(f"Invalid manuscript path/format: {name}")
            elif mode=="local":
                if form!="latex" or not path.startswith("manuscripts/") or not path.endswith("/main.tex"):
                    issues.append(f"Local manuscript path is not standard: {name}")
                elif not file_inside(root,path):
                    issues.append(f"Local manuscript file missing or symlinked: {name}")
            for field in ("commit_sha","blob_sha"):
                val=manuscript.get(field)
                if val is not None and (not isinstance(val,str) or not SHA40.fullmatch(val)):
                    issues.append(f"Invalid manuscript {field}: {name}")
        plan=p.get("study_plan")
        if plan is not None and (not safe_path(plan) or not plan.endswith(".yaml")
                                  or not file_inside(root,plan)):
            issues.append(f"Invalid or missing study plan: {name}")
        doi=p.get("doi")
        if doi is not None and (not isinstance(doi,str) or not DOI.fullmatch(doi)):
            issues.append(f"Invalid DOI syntax: {name}")
        for field in ("preprint_url","preregistration_url","publication_url"):
            value=p.get(field)
            if value is not None and not safe_url(value):
                issues.append(f"Invalid public paper URL {field}: {name}")
        evidence=p.get("stage_evidence")
        if is_in(stage,EVIDENCE):
            if (not isinstance(evidence,dict) or set(evidence)!={"kind","sha256","checked_on"}
                    or evidence.get("kind")!=EVIDENCE[stage]
                    or not isinstance(evidence.get("sha256"),str)
                    or not SHA256.fullmatch(evidence["sha256"])
                    or not isinstance(evidence.get("checked_on"),str)
                    or not DATE.fullmatch(evidence["checked_on"])):
                issues.append(f"Missing or invalid status evidence: {name}")
            if stage=="published" and doi is None and p.get("publication_url") is None:
                issues.append(f"Published paper lacks DOI/publication URL: {name}")
        elif evidence is not None:
            issues.append(f"Unexpected status evidence: {name}")

    for group in ("tools","equipment","datasets"):
        rows=dependencies.get(group)
        for item in rows if isinstance(rows,list) else []:
            if not isinstance(item,dict):
                issues.append(f"Invalid {group} dependency record")
                continue
            if set(item)-DEP_FIELDS:
                issues.append(f"Undeclared {group} dependency fields")
            pid=item.get("project_id")
            mid=item.get("paper_id")
            if (pid is None)==(mid is None):
                issues.append(f"Dependency requires exactly one owner: {group}")
            elif pid is not None and (not isinstance(pid,str) or pid not in project_repos):
                issues.append(f"Unknown dependency project: {group}")
            elif mid is not None and (not isinstance(mid,str) or mid not in paper_ids):
                issues.append(f"Unknown dependency paper: {group}")
            if not isinstance(item.get("ref"),str) or not item["ref"].strip():
                issues.append(f"Invalid {group} dependency reference")
            sha=item.get("sha")
            if sha is not None and (not isinstance(sha,str) or not SHA40.fullmatch(sha)):
                issues.append(f"Invalid {group} dependency SHA")
    return sorted(set(issues))

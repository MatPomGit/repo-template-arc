"""Strict stdlib parser for the limited flat PROJECT_STATE.yaml contract."""
from __future__ import annotations
import json
import re
from pathlib import Path
KEY = re.compile(r"^([a-z][a-z0-9_]*):(?:[ ]*(.*))?$")
FIELDS = {"schema_version","repository_type","template_version","programme",
          "scientific_owner","updated","phase","projects_registered","papers_registered",
          "public_catalog_status","pages_status","hardware_validation_status",
          "last_live_audit","known_blockers","next_action"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$")


def read_state(path: Path) -> tuple[dict, list[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return {}, ["PROJECT_STATE.yaml unreadable"]
    state, errors, active = {}, [], False
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and active:
            item = line[4:].strip()
            if not item or item.startswith(("#","-","!","{","[")):
                errors.append("PROJECT_STATE.yaml invalid blocker")
            else:
                state["known_blockers"].append(item)
            continue
        active = False
        match = KEY.fullmatch(line)
        if not match:
            errors.append("PROJECT_STATE.yaml unsupported YAML syntax")
            continue
        key, value = match.groups()
        if key not in FIELDS or key in state:
            errors.append("PROJECT_STATE.yaml unknown or duplicate field: " + key)
            continue
        if key == "known_blockers":
            if value == "[]":
                state[key] = []
            elif value == "":
                state[key] = []
                active = True
            else:
                errors.append("PROJECT_STATE.yaml invalid known_blockers list")
            continue
        if not value or value.startswith(("!","&","*","[","{")) or "#" in value:
            errors.append("PROJECT_STATE.yaml unsupported scalar: " + key)
            continue
        if key == "scientific_owner" and value.startswith('"'):
            # JSON double-quoted strings are valid YAML scalars; keep legacy
            # plain owner names readable without interpreting booleans.
            try:
                owner = json.loads(value)
            except ValueError:
                errors.append("PROJECT_STATE.yaml invalid quoted scientific_owner")
                continue
            if not isinstance(owner, str) or not owner.strip():
                errors.append("PROJECT_STATE.yaml invalid scientific_owner")
                continue
            state[key] = owner
        else:
            state[key] = None if value == "null" else value
    if set(state) != FIELDS:
        errors.append("PROJECT_STATE.yaml missing mandatory field")
    return state, sorted(set(errors))


def check_state(root: Path, meta: dict, projects: list, papers: list) -> list[str]:
    state, issues = read_state(root / "PROJECT_STATE.yaml")
    if issues:
        return issues
    expected = {"schema_version":str(meta.get("schema_version",1)),"repository_type":"research_program",
                "template_version":meta.get("template_version"),
                "programme":meta.get("programme"),"scientific_owner":meta.get("owner"),
                "projects_registered":str(len(projects)),
                "papers_registered":str(len(papers)),
                "pages_status":meta.get("pages_status")}
    for key, value in expected.items():
        if state.get(key) != value:
            issues.append("PROJECT_STATE mismatch: " + key)
    for key in ("projects_registered","papers_registered"):
        if not re.fullmatch(r"0|[1-9]\d*", str(state.get(key,""))):
            issues.append("PROJECT_STATE invalid counter: " + key)
    if state["phase"] not in {"scaffold","planned","active","paused","archived"}:
        issues.append("PROJECT_STATE invalid phase")
    for key in ("public_catalog_status","pages_status"):
        if state[key] not in {"not_configured","planned","approved","published"}:
            issues.append("PROJECT_STATE invalid status: " + key)
    if state["hardware_validation_status"] not in {"not_run","not_applicable","passed","failed"}:
        issues.append("PROJECT_STATE invalid hardware status")
    for key in ("updated","last_live_audit"):
        if state[key] is not None and not DATE.fullmatch(str(state[key])):
            issues.append("PROJECT_STATE invalid date: " + key)
    if not isinstance(state["next_action"],str) or not state["next_action"]:
        issues.append("PROJECT_STATE missing next action")
    if projects and state["phase"]=="scaffold":
        issues.append("PROJECT_STATE scaffold cannot contain projects")
    return sorted(set(issues))

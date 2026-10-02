#!/usr/bin/env python3
"""Check Astra worker config against the Codex model catalog and for drift.

Usage: python3 scripts/check-config.py [--home ~/.codex] [--catalog PATH]

Checks the project (.codex/) and, when present, the global home. Exit 1 on any failure.
"""
import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def fail(where, msg):
    errors.append(f"{where}: {msg}")


def load_agents(codex_dir):
    return {p.stem: tomllib.loads(p.read_text()) for p in sorted((codex_dir / "agents").glob("*.toml"))}


def check_target(label, codex_dir, catalog):
    config = tomllib.loads((codex_dir / "config.toml").read_text())
    agents = load_agents(codex_dir)
    section = config.get("agents", {})
    tables = {k: v for k, v in section.items() if isinstance(v, dict)}

    for stem, a in agents.items():
        where = f"{label} agents/{stem}.toml"
        for key in ("name", "description", "developer_instructions"):
            if not str(a.get(key, "")).strip():
                fail(where, f"missing {key}")
        if "model_reasoning_effort" in a:
            fail(where, "pins model_reasoning_effort; Astra sets effort per packet")
        if a.get("model") not in catalog:
            fail(where, f"model {a.get('model')!r} not in catalog")

    # [agents.<name>] tables are optional; when present they must match the files.
    by_name = {a.get("name"): (stem, a) for stem, a in agents.items()}
    for name, t in tables.items():
        where = f"{label} config.toml [agents.{name}]"
        cf = codex_dir / t.get("config_file", "")
        if not cf.is_file():
            fail(where, f"config_file {t.get('config_file')!r} not found")
            continue
        if name not in by_name:
            fail(where, "no agent file with this name")
            continue
        stem, a = by_name[name]
        if Path(t["config_file"]).stem != stem:
            fail(where, f"config_file points at {t['config_file']}, agent file is {stem}.toml")
        if t.get("description") != a.get("description"):
            fail(where, "description differs from the agent file")
    if tables:
        for name in by_name:
            if name not in tables:
                fail(f"{label} config.toml", f"agent {name} has a file but no [agents.{name}] table")

    # Primary model and the unnamed-subagent fallback must be valid for the catalog.
    main = config.get("model")
    if main and main in catalog:
        eff = config.get("model_reasoning_effort")
        if eff and eff not in catalog[main]:
            fail(f"{label} config.toml", f"model_reasoning_effort {eff!r} not allowed for {main}")
    elif main:
        fail(f"{label} config.toml", f"model {main!r} not in catalog")

    sub_model = section.get("default_subagent_model")
    if sub_model and sub_model not in catalog:
        fail(f"{label} config.toml", f"default_subagent_model {sub_model!r} not in catalog")
    sub_eff = section.get("default_subagent_reasoning_effort")
    if sub_eff:
        for m in {sub_model, *(a.get("model") for a in agents.values())} - {None}:
            if m in catalog and sub_eff not in catalog[m]:
                fail(f"{label} config.toml", f"default_subagent_reasoning_effort {sub_eff!r} not allowed for {m}")
    return agents


def check_agents_md(catalog):
    text = (ROOT / "AGENTS.md").read_text()
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Agent | Model | Allowed"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if in_table and not line.startswith("| ---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            model = cells[1].strip("`")
            allowed = set(re.findall(r"`([a-z]+)`", cells[2]))
            if model not in catalog:
                fail("AGENTS.md effort table", f"model {model!r} not in catalog")
            elif not allowed <= set(catalog[model]):
                fail("AGENTS.md effort table", f"{model}: {sorted(allowed - set(catalog[model]))} not in catalog")
    if not in_table:
        fail("AGENTS.md", "effort table not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default="~/.codex")
    ap.add_argument("--catalog")
    args = ap.parse_args()
    home = Path(args.home).expanduser()
    cat_path = Path(args.catalog).expanduser() if args.catalog else home / "model-catalogs" / "custom-models.json"
    catalog = {
        m["slug"]: [r["effort"] for r in m.get("supported_reasoning_levels", [])]
        for m in json.loads(cat_path.read_text())["models"]
    }

    proj = check_target("project", ROOT / ".codex", catalog)
    check_agents_md(catalog)
    if (home / "config.toml").is_file() and (home / "agents").is_dir():
        glob = check_target("global", home, catalog)
        for stem, a in proj.items():
            g = glob.get(stem)
            if g is None:
                fail("drift", f"{stem}.toml is in the project but not in {home}/agents")
                continue
            for key in ("name", "model", "description", "developer_instructions", "sandbox_mode"):
                if a.get(key) != g.get(key):
                    fail("drift", f"{stem}.toml {key} differs between project and global")

    if errors:
        print("FAIL")
        print("\n".join(f"  - {e}" for e in errors))
        sys.exit(1)
    print("OK: config, agent files, catalog and AGENTS.md effort table are consistent.")


if __name__ == "__main__":
    main()

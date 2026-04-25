#!/usr/bin/env python3
"""
Generate a human-readable summary and JSON summary for the repo.

Usage:
  python /home/polakovs/PhpstormProjects/pp-task-runner-mcp/scripts/generate_repo_summary.py \
    --repo /home/polakovs/PhpstormProjects/pp-task-runner-mcp \
    --out-dir /home/polakovs/PhpstormProjects/pp-task-runner-mcp/out
"""
import os
import sys
import json
import ast
import argparse
from datetime import datetime

# tomllib on py3.11+, fall back to tomli for py3.10
try:
    import tomllib as toml
except Exception:
    try:
        import tomli as toml
    except Exception:
        toml = None


def read_pyproject(path):
    p = os.path.join(path, "pyproject.toml")
    if not os.path.exists(p) or toml is None:
        return {}
    with open(p, "rb") as f:
        return toml.load(f)


def read_requirements(path):
    p = os.path.join(path, "requirements.txt")
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    return lines


def read_readme(path):
    p = os.path.join(path, "README.md")
    if not os.path.exists(p):
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def find_decorated_functions(src_root):
    tools, prompts, resources = [], [], []
    modules = 0
    other_fns = 0
    for root, _, files in os.walk(src_root):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            modules += 1
            full = os.path.join(root, fn)
            try:
                src = open(full, "r", encoding="utf-8").read()
                tree = ast.parse(src)
            except Exception:
                continue
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    dec_names = []
                    for d in node.decorator_list:
                        try:
                            if isinstance(d, ast.Attribute):
                                name = d.attr
                            elif isinstance(d, ast.Call):
                                if isinstance(d.func, ast.Attribute):
                                    name = d.func.attr
                                elif isinstance(d.func, ast.Name):
                                    name = d.func.id
                                else:
                                    name = getattr(d, 'id', '')
                            elif isinstance(d, ast.Name):
                                name = d.id
                            else:
                                name = ""
                        except Exception:
                            name = ""
                        dec_names.append(name.lower())
                    doc = ast.get_docstring(node) or ""
                    if any("tool" in dn for dn in dec_names):
                        tools.append({"name": node.name, "file": os.path.relpath(full, src_root), "doc": (doc.splitlines()[0] if doc else "")})
                    elif any("prompt" in dn for dn in dec_names):
                        prompts.append({"name": node.name, "file": os.path.relpath(full, src_root), "doc": (doc.splitlines()[0] if doc else "")})
                    elif any("resource" in dn for dn in dec_names):
                        resources.append({"name": node.name, "file": os.path.relpath(full, src_root), "doc": (doc.splitlines()[0] if doc else "")})
                    else:
                        other_fns += 1
    return {"modules": modules, "tools": tools, "prompts": prompts, "resources": resources, "other_functions_count": other_fns}


def find_entrypoint(pyproject, repo_path):
    entry = {}
    try:
        scripts = pyproject.get("project", {}).get("scripts", {})
        for k, v in scripts.items():
            if ":" in v:
                module, attr = v.split(":", 1)
                entry = {"name": k, "module": module, "attr": attr, "source": os.path.join(repo_path, "pyproject.toml")}
                break
    except Exception:
        pass
    if not entry:
        candidate = os.path.join(repo_path, "src", "main.py")
        if os.path.exists(candidate):
            entry = {"name": None, "module": "src.main", "attr": "main", "source": candidate}
    return entry


def collect_tests(repo_path):
    tests_dir = os.path.join(repo_path, "tests")
    files = []
    if os.path.exists(tests_dir):
        for fn in os.listdir(tests_dir):
            if fn.endswith(".py"):
                files.append(os.path.join("tests", fn))
    return {"files": len(files), "examples": files}


def build_human_summary(meta, pyproject, reqs, readme_snippet, src_info, tests_info):
    lines = []
    lines.append(f"Repository: {meta.get('repo_name')}")
    lines.append(f"Description: {meta.get('description')}")
    lines.append("")
    lines.append("Entrypoint:")
    ep = meta.get("entrypoint")
    if ep:
        lines.append(f"  module: {ep.get('module')} attr: {ep.get('attr')} (source: {ep.get('source')})")
    lines.append("")
    lines.append("Dependencies:")
    if reqs:
        for d in reqs:
            lines.append(f"  - {d}")
    else:
        lines.append("  (none detected in requirements.txt)")
    lines.append("")
    lines.append("Detected MCP artifacts:")
    for t in src_info.get("tools", []):
        lines.append(f"  tool: {t['name']} ({t['file']}) — {t['doc']}")
    for p in src_info.get("prompts", []):
        lines.append(f"  prompt: {p['name']} ({p['file']}) — {p['doc']}")
    for r in src_info.get("resources", []):
        lines.append(f"  resource: {r['name']} ({r['file']}) — {r['doc']}")
    lines.append("")
    lines.append("Tests:")
    lines.append(f"  files: {tests_info['files']}")
    lines.append("")
    lines.append("Run instructions (README excerpt):")
    lines.append(readme_snippet.strip()[:1000])
    return "\n".join(lines)


def build_markdown_summary(meta, readme_snippet, src_info, tests_info):
    lines = []
    lines.append(f"# {meta.get('repo_name')}")
    if meta.get('description'):
        lines.append("")
        lines.append(meta.get('description'))

    lines.append("")
    lines.append("## Entrypoint")
    ep = meta.get("entrypoint")
    if ep:
        lines.append("")
        lines.append(f"- module: `{ep.get('module')}`")
        lines.append(f"- function: `{ep.get('attr')}`")
        lines.append(f"- source: `{ep.get('source')}`")

    lines.append("")
    lines.append("## Dependencies")
    lines.append("")
    if meta.get('dependencies'):
        for d in meta.get('dependencies'):
            lines.append(f"- `{d}`")
    else:
        lines.append("- None detected")

    lines.append("")
    lines.append("## Detected MCP artifacts")
    lines.append("")
    if src_info.get('tools'):
        lines.append("### Tools")
        for t in src_info.get('tools'):
            lines.append(f"- **{t['name']}** — `{t['file']}` — {t['doc']}")
        lines.append("")
    if src_info.get('prompts'):
        lines.append("### Prompts")
        for p in src_info.get('prompts'):
            lines.append(f"- **{p['name']}** — `{p['file']}` — {p['doc']}")
        lines.append("")
    if src_info.get('resources'):
        lines.append("### Resources")
        for r in src_info.get('resources'):
            lines.append(f"- **{r['name']}** — `{r['file']}` — {r['doc']}")
        lines.append("")

    lines.append("## Tests")
    lines.append("")
    lines.append(f"- files: {tests_info.get('files')}")
    for ex in tests_info.get('examples', []):
        lines.append(f"- `{ex}`")

    lines.append("")
    lines.append("## Run instructions (excerpt from README)")
    lines.append("")
    lines.append("```")
    # include a trimmed excerpt
    excerpt = readme_snippet.strip()
    lines.append(excerpt[:10000])
    lines.append("```")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=False, default=os.getcwd(), help="Repository root")
    parser.add_argument("--out-dir", required=False, default=None, help="Output directory")
    args = parser.parse_args()
    repo = os.path.abspath(args.repo)
    out_dir = args.out_dir or os.path.join(repo, "out")
    os.makedirs(out_dir, exist_ok=True)

    pyproject = read_pyproject(repo)
    reqs = read_requirements(repo)
    readme = read_readme(repo)
    src_root = os.path.join(repo, "src")
    src_info = find_decorated_functions(src_root) if os.path.exists(src_root) else {"modules":0, "tools":[], "prompts":[], "resources":[], "other_functions_count":0}
    entry = find_entrypoint(pyproject, repo)
    tests_info = collect_tests(repo)

    meta = {
        "repo_name": pyproject.get("project", {}).get("name", os.path.basename(repo)),
        "description": pyproject.get("project", {}).get("description", "") or "",
        "python_requires": pyproject.get("project", {}).get("requires-python", ""),
        "dependencies": reqs,
        "entrypoint": entry,
        "cli_scripts": [{"name": k, "target": v} for k, v in pyproject.get("project", {}).get("scripts", {}).items()] if pyproject.get("project") else [],
        "frameworks": ["mcp (FastMCP)"] if any("mcp" in d for d in reqs) else [],
        "src_summary": src_info,
        "tests": tests_info,
        "run_instructions": (readme.split("## Run")[-1] if "## Run" in readme else readme)[:2000],
        "build_files": [f for f in ["pyproject.toml", "requirements.txt"] if os.path.exists(os.path.join(repo, f))],
        "files_examined": [os.path.join(repo, "pyproject.toml"), os.path.join(repo, "requirements.txt"), os.path.join(repo, "README.md"), os.path.join(repo, "src"), os.path.join(repo, "tests")],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    human = build_human_summary(meta, pyproject, reqs, readme[:2000], src_info, tests_info)
    md = build_markdown_summary(meta, readme[:2000], src_info, tests_info)
    txt_out = os.path.join(out_dir, "repo_summary.txt")
    md_out = os.path.join(out_dir, "repo_summary.md")
    json_out = os.path.join(out_dir, "repo_summary.json")
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write(human)
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(md)
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Wrote", txt_out)
    print("Wrote", md_out)
    print("Wrote", json_out)


if __name__ == "__main__":
    main()


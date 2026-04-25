Summary generator usage

1. Install dependency (if on Python 3.10):

```bash
python3 -m pip install --user tomli
```

2. Run generator:

```bash
python3 /home/polakovs/PhpstormProjects/pp-task-runner-mcp/scripts/generate_repo_summary.py \
  --repo /home/polakovs/PhpstormProjects/pp-task-runner-mcp \
  --out-dir /home/polakovs/PhpstormProjects/pp-task-runner-mcp/out
```

3. Outputs:
  - /home/polakovs/PhpstormProjects/pp-task-runner-mcp/out/repo_summary.txt
  - /home/polakovs/PhpstormProjects/pp-task-runner-mcp/out/repo_summary.json
  - /home/polakovs/PhpstormProjects/pp-task-runner-mcp/out/repo_summary.md

Notes:
- The script will try to use the standard library tomllib on Python 3.11+. For Python 3.10 install tomli.
- The generator now emits a Markdown summary (`repo_summary.md`) suitable for passing as context to Perplexity or other LLM tools.

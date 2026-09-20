#!/usr/bin/env python3
"""Replace the open CI gap section in CURRENT_WORK.md with CLOSED."""
from pathlib import Path
import re

path = Path("CURRENT_WORK.md")
t = path.read_text()
if "## CI gap — CLOSED" in t or "## CI gap - CLOSED" in t:
    print("already closed")
    raise SystemExit(0)

new = (
    "## CI gap — CLOSED (Grok C)\n\n"
    "`GITHUB_TOKEN` pushes still cannot re-trigger other workflows (GitHub\n"
    "loop guard). Closed by option 2: after a successful CDI commit+push in\n"
    "`build-dreamcast.yml`, a step runs `gh workflow run deploy-pages.yml`\n"
    "with `permissions: actions: write`. Pages re-packages\n"
    "`ports/dreamcast/crymon.cdi` into the download slot without a PAT or\n"
    "manual re-run.\n\n"
    "If deploy-pages ever fails to start, check the Build Dreamcast CDI job\n"
    "log for the \"Trigger Pages deploy\" step and the Actions tab for a\n"
    "queued Deploy CryMon Web run.\n"
)

m = re.search(r"## CI gap \(still open\):.*?(?=\n---\n)", t, flags=re.S)
if not m:
    raise SystemExit("CI gap open section not found")
t = t[: m.start()] + new + t[m.end() :]
t = t.replace(
    "confirm the Pages deploy actually re-ran for that commit (see\n  the CI gap note below — it does **not** happen automatically off a\n  bot-only CDI commit, currently)",
    "confirm the Pages deploy actually re-ran for that commit (bot CDI\n  pushes now `workflow_dispatch` deploy-pages — see CI gap CLOSED note)",
)
path.write_text(t)
print("ok", len(t))

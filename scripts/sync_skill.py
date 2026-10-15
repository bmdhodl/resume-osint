"""Keep skills/resume-osint/SKILL.md equal to the published skill file.

The skill is written and published at https://bmdpat.com/tools/resume-osint.
This repository carries a copy so that Claude Code and Codex can install it
from GitHub. Do not edit the copy by hand; run this script instead.

    python scripts/sync_skill.py          # write the published file into the repo
    python scripts/sync_skill.py --check  # exit 1 when the copy differs or breaks a rule

Standard library only, so it runs on any Python 3.9+ without an install step.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

PUBLISHED_URL = "https://bmdpat.com/tools/resume-osint/SKILL.md"
SKILL_NAME = "resume-osint"
# Codex rejects a description over 500 characters; Claude Code allows 1,024.
MAX_DESCRIPTION_CHARS = 500
EM_DASH = chr(0x2014)

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "skills" / SKILL_NAME / "SKILL.md"
PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
PROSE_PATHS = [ROOT / "README.md", SKILL_PATH, PLUGIN_PATH, MARKETPLACE_PATH]


def fetch_published(url: str = PUBLISHED_URL) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "resume-osint-sync (+https://github.com/bmdhodl/resume-osint)"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("text/markdown"):
            raise RuntimeError(f"{url} returned {content_type!r}, expected text/markdown")
        return response.read()


def frontmatter_problems(text: str) -> list[str]:
    """Return the reasons Claude Code or Codex would reject the skill header."""
    if not text.startswith("---\n"):
        return ["SKILL.md must start with a '---' frontmatter line"]
    end = text.find("\n---\n", 4)
    if end == -1:
        return ["SKILL.md frontmatter has no closing '---' line"]

    fields: dict[str, str] = {}
    for line in text[4:end].split("\n"):
        key, separator, value = line.partition(": ")
        if not separator:
            return [f"frontmatter line is not 'key: value': {line!r}"]
        fields[key] = value

    problems = []
    if sorted(fields) != ["description", "name"]:
        problems.append(f"frontmatter keys must be name and description only, found {sorted(fields)}")
    if fields.get("name") != SKILL_NAME:
        problems.append(f"frontmatter name must be {SKILL_NAME!r}, found {fields.get('name')!r}")
    description = fields.get("description", "")
    if not description:
        problems.append("frontmatter description is empty")
    if len(description) > MAX_DESCRIPTION_CHARS:
        problems.append(
            f"frontmatter description is {len(description)} characters; Codex allows {MAX_DESCRIPTION_CHARS}"
        )
    # An unquoted YAML value cannot hold ': ' or ' #'. Codex parses the header as YAML.
    if ": " in description or " #" in description:
        problems.append("frontmatter description must be a plain YAML value without ': ' or ' #'")
    return problems


def drift_problems(local: bytes, published: bytes) -> list[str]:
    if local == published:
        return []
    return [
        f"skills/{SKILL_NAME}/SKILL.md differs from {PUBLISHED_URL}. "
        "Run 'python scripts/sync_skill.py' and commit the result."
    ]


def manifest_problems(plugin: dict, marketplace: dict) -> list[str]:
    problems = []
    entries = marketplace.get("plugins", [])
    if len(entries) != 1:
        return [f"marketplace.json must list exactly one plugin, found {len(entries)}"]
    entry = entries[0]
    if plugin.get("name") != SKILL_NAME or entry.get("name") != SKILL_NAME:
        problems.append(f"plugin.json name and the marketplace entry name must both be {SKILL_NAME!r}")
    if entry.get("source") != "./":
        problems.append("the marketplace entry source must be './' (the plugin is the repository root)")
    # Without a version, installs follow new commits. A fixed version would hold
    # every user on the first copy until someone remembers to bump it.
    if "version" in plugin or "version" in entry:
        problems.append("remove 'version' from plugin.json and marketplace.json so installs follow new commits")
    return problems


def em_dash_problems(paths: list[Path]) -> list[str]:
    return [f"{path.relative_to(ROOT)} contains an em dash" for path in paths if EM_DASH in path.read_text("utf-8")]


def check() -> list[str]:
    published = fetch_published()
    plugin = json.loads(PLUGIN_PATH.read_text("utf-8"))
    marketplace = json.loads(MARKETPLACE_PATH.read_text("utf-8"))
    return (
        drift_problems(SKILL_PATH.read_bytes(), published)
        + frontmatter_problems(SKILL_PATH.read_text("utf-8"))
        + manifest_problems(plugin, marketplace)
        + em_dash_problems(PROSE_PATHS)
    )


def sync() -> list[str]:
    published = fetch_published()
    problems = frontmatter_problems(published.decode("utf-8"))
    if problems:
        return [f"refusing to write the published file: {problem}" for problem in problems]
    SKILL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SKILL_PATH.write_bytes(published)
    print(f"wrote {SKILL_PATH.relative_to(ROOT)} from {PUBLISHED_URL}")
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail when the copy differs or breaks a rule")
    args = parser.parse_args()

    problems = check() if args.check else sync()
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if args.check and not problems:
        print(f"OK: SKILL.md matches {PUBLISHED_URL} and the manifests pass")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

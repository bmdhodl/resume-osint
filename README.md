# Resume OSINT

An agent skill for Claude Code and Codex. It checks the claims on a resume against public sources before you spend an interview on them.

Give it a resume. It checks employers, dates, tech stack, education, links and LinkedIn. It finds employment gaps and overlapping jobs. It flags copied job text, cloned bullets, tools that did not exist yet and hidden prompts aimed at AI screeners. Every finding cites a source and turns into a neutral interview question. A person still makes the hiring decision.

Page, checklist and example report: https://bmdpat.com/tools/resume-osint

## Install as a Claude Code plugin

In a Claude Code session:

```
/plugin marketplace add bmdhodl/resume-osint
/plugin install resume-osint@resume-osint
```

Or from your shell:

```bash
claude plugin marketplace add bmdhodl/resume-osint
claude plugin install resume-osint@resume-osint
```

## Install the file

Each command saves one file into your skills folder as `resume-osint/SKILL.md`. Read [the file](skills/resume-osint/SKILL.md) before you install it.

Claude Code (macOS / Linux):

```bash
mkdir -p ~/.claude/skills/resume-osint && curl -fsSL https://bmdpat.com/tools/resume-osint/SKILL.md -o ~/.claude/skills/resume-osint/SKILL.md
```

Codex (macOS / Linux):

```bash
mkdir -p ~/.codex/skills/resume-osint && curl -fsSL https://bmdpat.com/tools/resume-osint/SKILL.md -o ~/.codex/skills/resume-osint/SKILL.md
```

Claude Code (Windows PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills\resume-osint" | Out-Null; Invoke-WebRequest https://bmdpat.com/tools/resume-osint/SKILL.md -OutFile "$HOME\.claude\skills\resume-osint\SKILL.md"
```

## Use it

Start a new session, then ask:

> Use the resume-osint skill on candidate.pdf. The job description is job.md. Our products are Acme Sync and Acme Vault.

Only the resume is required. Without the job description, the product names or other resumes from the same pipeline, the skill marks those checks Not checked and runs the rest.

The skill needs web search or a browser to check public sources. Without one, it marks each web check Not checked.

## What it checks

Six groups: employers, education, timeline, links and contact details, copied or generated text, and big-company moves. [SKILL.md](skills/resume-osint/SKILL.md) lists every check, the sources for each one, the severity levels and the report format.

Each flag is a question for the candidate, not a verdict. This is not a background check and not legal advice. Read the Rules section of SKILL.md before you use it on real candidates.

## Where the text comes from

`skills/resume-osint/SKILL.md` is a copy of https://bmdpat.com/tools/resume-osint/SKILL.md. Do not edit it here. A daily check fails when the two differ. To update the copy:

```bash
python scripts/sync_skill.py
```

`python scripts/sync_skill.py --check` runs the same comparison as CI, plus the frontmatter and manifest rules.

## License

MIT. See [LICENSE](LICENSE).

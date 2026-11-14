---
name: pr
description: Creates a GitHub pull request from the current state of the local Git repo (create branch, commit, push, gh pr create). Only on explicit invocation via /pr.
argument-hint: "[draft] [base=<branch>] [milestone=<pattern>] [label=<p1,p2,...>] [notes on content]"
model: sonnet
disable-model-invocation: true
---

# /pr – pull request from the current situation

Invoking `/pr` is the explicit authorization to push the feature branch and create the PR.
Do not ask again – only stop in the cases listed under "Stop rules".

Arguments (`$ARGUMENTS`, all optional):
- `draft` → create the PR as a draft
- `base=<branch>` → override the target branch
- `milestone=<pattern>` → set a milestone in the target repo. The value is a case-insensitive
  regex (e.g. `milestone=5.0.*` or `milestone=rel.*4`) that is searched in the titles of the
  **open** milestones only (see "Pattern matching"); a plain number is the milestone number.
  Quote values containing spaces: `milestone="Release 4.15"`
- `label=<p1,p2,...>` (also `labels=`) → set labels in the target repo, comma-separated; every entry
  is a case-insensitive regex that is searched in the label names (e.g. `label=enh,bug,break`)
- any other text → hints for title/description

## 1. Provide gh

`gh` is not installed globally. Order:
1. `command -v gh` → use it directly
2. otherwise run every call as `nix-shell -p gh --run '<gh command>'`
   (fallback: `nix-shell /home/tbr/git/ansible-oracle/shell.nix --run '…'`, but this starts the venvs)

Login lives in `~/.config/gh/hosts.yml` (account `Rendanic`), no `gh auth login` needed.

## 2. Assess the situation (in parallel)

- `git status --porcelain`, `git branch --show-current`, `git remote -v`
- `git log --oneline -10` (adopt the style and language of the commit messages)
- Determine the target repo:
  - remote `upstream` exists → PR against **upstream** (fork workflow), head = `<origin-owner>:<branch>`
  - otherwise against `origin`
- Base branch: `base=` from the arguments, otherwise the default branch of the target repo
  (`gh repo view <owner/repo> --json defaultBranchRef -q .defaultBranchRef.name`)
- Is there already a PR for the branch? `gh pr list --repo <target> --head <branch> --state open`
  → if so: commit + push; add `milestone=`/`label=` (resolved as described under "Pattern matching") via
  `gh pr edit <nr> --repo <target> --milestone … --add-label …`; report the URL, done.
- Resolve `milestone=`/`label=` against the **target repo** before pushing (see "Pattern matching").
  The result is the exact milestone title and the exact label names; `gh` expects these, not the
  pattern. Never create anything automatically.

### Pattern matching (milestone and labels)

Candidates (never use anything else; closed milestones are not considered):
- labels: `gh label list --repo <target> --limit 200 --json name -q '.[].name'`
- milestones, **open only**:
  `gh api --paginate "repos/<target>/milestones?state=open&per_page=100" --jq '.[] | "\(.number)\t\(.title)"'`

Matching per value (milestone: the one value; labels: each comma-separated entry separately):
1. milestone only: a value consisting only of digits = milestone number → must be one of the open
   milestones, otherwise "unknown".
2. Exact match of the whole name/title (case-insensitive) → take it, done.
3. Otherwise search the value as an extended regex (`grep -iE -- "<value>"`, unanchored, so
   `enh` finds `enhancement` and `5.0` finds `5.0.0`) in the candidate names. Pass the value
   quoted, no shell expansion of `*`. Invalid regex → treat the value literally (`grep -iF`).
4. Exactly one hit → take it. Mention in the final output which pattern resolved to which name.
5. No hit → stop, list all candidates (milestone: only the open ones).
6. Several hits → stop, list the hits for this value and ask for a more precise pattern. Do not
   guess. Exception: several hits for a **label** entry are not resolved by choosing the first one,
   it is the same stop.

Different entries of `label=` must resolve to different labels; duplicates are removed.

## 3. Branch

- On the default branch (main/master/devel) or detached HEAD: create a new branch,
  name derived briefly from the change (kebab-case, prefix such as `fix/`, `feature/` if it matches
  existing branch names). Local commits not yet on the base move along into the new branch.
- Otherwise use the current branch.

## 4. Commit

- Commit uncommitted changes that belong to the topic. Message in the style of the existing
  commits (repo language, e.g. `<area>: <what>` as in ansible-oracle).
- The commit message ends with the attribution from the system reminder.
- No blind `git add -A`: add files explicitly; never commit obvious foreign objects
  (`.venv`, secrets, temporary files).

## 5. Repo-specific checks

- If `changelogs/fragments/` exists and the branch contains no new/changed fragment
  (`git diff --name-only <base>...HEAD -- changelogs/fragments`): create a matching fragment in the
  style of the existing files and commit it.
- `.github/pull_request_template.md` (or variants) exists → use it as the structure for the description.
- Do not trigger builds/tests that memory reserves for the user (e.g. molecule converge).

## 6. Push & PR

```bash
git push -u origin <branch>
gh pr create --repo <target-owner/repo> --base <base> --head <origin-owner>:<branch> \
  --title "<title>" --body-file <scratchpad>/pr-body.md [--draft] \
  [--milestone "<milestone-title>"] [--label "<l1>,<l2>"]
```

- If only setting label/milestone fails (missing triage permission upstream) but the PR was
  created: report the PR URL and state clearly what could not be set.

- Title: short, in the repo's language (commit history), no trailing period.
- Body (write the file to the scratchpad, do not quote inline):
  - **Summary** – what and why (1–3 sentences)
  - **Changes** – bullet points
  - **Testing** – what was actually tested; honestly "not tested" if nothing was
  - Closing: PR attribution from the system reminder
- Output to the user: PR URL, branch, target (`repo:base`), milestone/labels, list of commits.

## Stop rules (only ask here)

- A force push would be required (branch diverges from the remote)
- The push would go directly to the default branch
- Uncommitted changes clearly belong to different topics
- Merge conflicts / rebase required
- No changes compared to the base → report, do nothing
- A given label or milestone pattern matches nothing (milestone: no open milestone) or is ambiguous
  in the target repo

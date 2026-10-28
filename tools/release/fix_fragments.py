#!/usr/bin/env python3
"""Add pull request references to changelog fragments.

Every entry in changelogs/fragments/*.yml should reference the pull request
that introduced it, e.g.:

  - "As of GI 19.31 blanks are not allowed around commas ... (oravirt#599)"

The pull request is determined from the last commit that touched the
fragment file. GitHub is asked for the pull requests containing that commit.
If the last commit is not part of any pull request (e.g. a local release
commit), older commits of the fragment are tried.

The PR reference is appended to every entry that does not end with it,
even if the entry already contains another reference (e.g. an issue number).

Set GITHUB_TOKEN (or GH_TOKEN) to avoid the API rate limit for
unauthenticated requests (60 requests/hour). Without these variables the
token stored by gh (GitHub CLI) is used, when all fragments are processed.

This script was generated with AI assistance (Claude Code, Anthropic).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_REPO = "oravirt/ansible-oracle"
ITEM_RE = re.compile(r"^(?P<indent>\s*-\s+)(?P<value>.*?)(?P<trail>\s*)$")

_pr_cache = {}
_token = None


def git(*args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def github_prs_for_commit(repo, sha):
    """Return the pull requests in repo that contain the commit."""
    if sha in _pr_cache:
        return _pr_cache[sha]

    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/commits/{sha}/pulls",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if _token:
        req.add_header("Authorization", f"Bearer {_token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            prs = json.load(resp)
    except urllib.error.HTTPError as err:
        # 404/422: commit unknown on GitHub (not pushed yet)
        if err.code in (404, 422):
            prs = []
        else:
            sys.exit(f"GitHub API error for {sha}: {err.code} {err.reason}")

    _pr_cache[sha] = prs
    return prs


def gh_config_token():
    """Read the token for github.com from the config of gh (hosts.yml)."""
    config_dir = os.environ.get("GH_CONFIG_DIR") or Path(
        os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    ) / "gh"
    hosts = Path(config_dir) / "hosts.yml"
    if not hosts.is_file():
        return None
    in_github = False
    for line in hosts.read_text().splitlines():
        if line and not line[0].isspace():
            in_github = line.rstrip() == "github.com:"
            continue
        match = re.match(r"^\s+oauth_token:\s*(\S+)", line)
        if in_github and match:
            return match[1]
    return None


def stored_token():
    """Token stored by gh: 'gh auth token' (keyring) or gh's hosts.yml."""
    if shutil.which("gh"):
        result = subprocess.run(
            ["gh", "auth", "token", "--hostname", "github.com"],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return gh_config_token()


def github_token(all_fragments):
    """Token from environment, the stored one of gh only for all fragments."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token or not all_fragments:
        return token
    token = stored_token()
    if not token:
        print("no GitHub token found, API rate limit for unauthenticated "
              "requests applies", file=sys.stderr)
    return token


def select_pr(repo, prs):
    """Prefer merged pull requests, then open ones. Closed unmerged are ignored."""
    prs = [p for p in prs if p["base"]["repo"]["full_name"].lower() == repo.lower()]
    merged = [p for p in prs if p.get("merged_at")]
    if merged:
        return min(merged, key=lambda p: p["number"])
    opened = [p for p in prs if p["state"] == "open"]
    if opened:
        return min(opened, key=lambda p: p["number"])
    return None


def find_pr(repo, fragment, repo_root):
    """Return (pr, commit) for the newest commit of fragment that belongs to a PR."""
    commits = git(
        "log", "--format=%H", "--", str(fragment.relative_to(repo_root)),
        cwd=repo_root,
    ).split()
    for sha in commits:
        pr = select_pr(repo, github_prs_for_commit(repo, sha))
        if pr:
            return pr, sha, sha == commits[0]
    return None, commits[0] if commits else None, False


def add_reference(value, ref):
    """Insert ' (ref)' at the end of a YAML scalar. Returns None if not possible."""
    for quote in ('"', "'"):
        if len(value) >= 2 and value.startswith(quote) and value.endswith(quote):
            return f"{value[:-1]} ({ref}){quote}"
    if value[:1] in ('"', "'") or value[-1:] in ('"', "'"):
        # broken quoting, needs manual fix
        return None
    return f"{value} ({ref})"


def fix_fragment(fragment, prefix, pr_number):
    ref = f"{prefix}#{pr_number}"
    # the PR reference must be the last thing in the entry
    end_ref_re = re.compile(rf"\({re.escape(ref)}\)[\"']?$")
    lines = fragment.read_text().splitlines(keepends=True)
    messages = []
    changed = False

    for idx, line in enumerate(lines):
        match = ITEM_RE.match(line.rstrip("\n"))
        if not match:
            continue
        value = match["value"]
        nxt = lines[idx + 1] if idx + 1 < len(lines) else ""
        if nxt.strip() and not nxt.lstrip().startswith("-") and \
                len(nxt) - len(nxt.lstrip()) > len(line) - len(line.lstrip()):
            messages.append(f"  line {idx + 1}: multi-line entry, please fix manually")
            continue

        if end_ref_re.search(value):
            continue

        new_value = add_reference(value, ref)
        if new_value is None:
            messages.append(f"  line {idx + 1}: broken quoting, please fix manually")
            continue
        lines[idx] = f"{match['indent']}{new_value}{match['trail']}" + (
            "\n" if line.endswith("\n") else ""
        )
        messages.append(f"  line {idx + 1}: {new_value}")
        changed = True

    return lines, changed, messages


def resolve_fragment(name, fragment_dir):
    """Accept a path or a plain filename from changelogs/fragments."""
    for candidate in (Path(name), fragment_dir / name):
        if candidate.is_file():
            return candidate.resolve()
    sys.exit(f"fragment not found: {name}")


def main():
    repo_root = Path(
        git("rev-parse", "--show-toplevel", cwd=Path(__file__).resolve().parent).strip()
    )

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-f", "--fragment", action="append", default=[],
                        metavar="FILE",
                        help="check only this fragment, path or filename in "
                             "changelogs/fragments (can be repeated, "
                             "default: all fragments)")
    parser.add_argument("--repo", default=DEFAULT_REPO,
                        help="GitHub repository with the pull requests "
                             f"(default: {DEFAULT_REPO})")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="only show what would be changed, "
                             "exit code 1 if a fragment needs to be updated")
    args = parser.parse_args()

    global _token
    _token = github_token(all_fragments=not args.fragment)

    prefix = args.repo.split("/")[0]
    fragment_dir = repo_root / "changelogs" / "fragments"
    fragments = [resolve_fragment(f, fragment_dir) for f in args.fragment] or sorted(
        fragment_dir.glob("*.y*ml")
    )

    problems = 0
    for fragment in fragments:
        name = fragment.relative_to(repo_root)
        pr, sha, from_last = find_pr(args.repo, fragment, repo_root)
        if sha is None:
            print(f"{name}: not committed yet - skipped")
            problems += 1
            continue
        if pr is None:
            print(f"{name}: no pull request found for commit {sha[:10]} - skipped")
            problems += 1
            continue

        lines, changed, messages = fix_fragment(fragment, prefix, pr["number"])
        note = "" if from_last else f" (from older commit {sha[:10]})"
        status = "updated" if changed else "ok"
        if changed and args.dry_run:
            status = "would be updated"
            problems += 1
        print(f"{name}: {prefix}#{pr['number']} \"{pr['title']}\"{note} - {status}")
        for msg in messages:
            print(msg)
        problems += sum("manually" in m for m in messages)

        if changed and not args.dry_run:
            fragment.write_text("".join(lines))

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

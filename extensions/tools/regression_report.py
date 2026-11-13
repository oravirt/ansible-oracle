#!/usr/bin/env python3
"""Report of a regression run (tools/regression.sh).

Usage: regression_report.py <run directory>

Reads run.env, steps.jsonl, module_tests/<scenario>.json and the logfiles of the failed
steps and writes <run directory>/summary.md (also printed to stdout).
The report can be created while the run is still in progress.
"""
import json
import re
import sys
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")
# molecule wraps the ansible output in a box: '  │ ', '  ├─', '  └─'
BOX = re.compile(r"^\s*[│├└┌]\s?")
MAX_ERRORS = 3


def read_env(run_dir):
    env = {}
    path = run_dir / "run.env"
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env[key] = value
    return env


def read_steps(run_dir):
    steps = {}
    path = run_dir / "steps.jsonl"
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                step = json.loads(line)
                steps[(step["scenario"], step["step"])] = step
    return steps


def clean_lines(path):
    lines = []
    for line in path.read_text(errors="replace").splitlines():
        lines.append(BOX.sub("", ANSI.sub("", line)).rstrip())
    return lines


def join_wrapped(lines, start):
    """Join an entry wrapped by molecule over several lines (until an empty line)."""
    parts = []
    for line in lines[start:]:
        if not line.strip():
            break
        parts.append(line.strip())
    return " ".join(parts)


def task_header(lines, start):
    """Task header wrapped by molecule over several lines (ends with '***')."""
    parts = []
    for line in lines[start:start + 4]:
        parts.append(line.strip())
        if line.rstrip().endswith("*") or not line.strip():
            break
    return " ".join(p for p in parts if p)


def log_errors(path):
    """Failed tasks of a logfile: (task, message, fatal).

    Rescued failures are included.
    """
    if not path.exists():
        return [], []
    lines = clean_lines(path)
    errors = []
    task = ""
    for i, line in enumerate(lines):
        if line.startswith("TASK [") or line.startswith("RUNNING HANDLER ["):
            task = re.sub(r"\s*\*+$", "", task_header(lines, i))
        elif line.startswith("fatal:") or re.match(r"^failed: \[", line):
            msg = join_wrapped(lines, i)
            found = re.search(r'"msg": "(.*?)(?<!\\)"', msg)
            errors.append((task, (found.group(1) if found else msg)[:300],
                           line.startswith("fatal:")))
    recap = [ln.strip() for ln in lines if re.search(r"\bok=\d+\s+changed=\d+", ln)]
    return errors, recap


def idempotence_tasks(path):
    """Tasks reported by 'molecule idempotence' as changed."""
    if not path.exists():
        return []
    lines = clean_lines(path)
    tasks = []
    for i, line in enumerate(lines):
        if "Idempotence test failed because of the following tasks" in line:
            for task_line in lines[i + 1:]:
                if task_line.strip().startswith("*"):
                    tasks.append(task_line.strip().lstrip("* "))
                elif tasks:
                    break
    return tasks


def fmt_duration(seconds):
    return "%d:%02d" % (seconds // 3600, (seconds % 3600) // 60)


def main():
    run_dir = Path(sys.argv[1]).resolve()
    env = read_env(run_dir)
    steps = read_steps(run_dir)
    scenarios = [s for s in env.get("SCENARIOS", "").split(",") if s]
    step_names = [t for t in env.get("STEPS", "").split(",") if t]

    out = []
    out.append("# Regression run %s" % env.get("RUN_ID", run_dir.name))
    out.append("")
    out.append("- Commit: `%s` %s (branch `%s`)%s" % (
        env.get("COMMIT", "")[:10], env.get("SUBJECT", ""), env.get("BRANCH", ""),
        ", **uncommitted changes** (git-status.txt)" if env.get("DIRTY") else ""))
    out.append("- Start: %s, end: %s" % (
        env.get("START", ""), env.get("END", "still running")))
    if env.get("MODULES"):
        out.append("- Module tests: %s" % env["MODULES"])
    out.append("")

    # overview: scenario x step
    out.append("## Overview")
    out.append("")
    out.append("| Scenario | " + " | ".join(step_names) + " |")
    out.append("|---" * (len(step_names) + 1) + "|")
    for s in scenarios:
        cells = []
        stopped = False
        for t in step_names:
            step = steps.get((s, t))
            if step:
                state = "ok" if step["rc"] == 0 else "**FAILED** (rc=%s)" % step["rc"]
                cells.append("%s %s" % (state, fmt_duration(step["duration_s"])))
                if step["rc"] != 0 and t in ("create", "converge"):
                    stopped = True
            elif stopped:
                cells.append("skipped")
            elif (run_dir / ("%s-%s.log" % (s, t))).exists() and not env.get("END"):
                cells.append("running")
            else:
                cells.append("-")
        out.append("| %s | %s |" % (s, " | ".join(cells)))
    out.append("")

    # module tests
    results = sorted((run_dir / "module_tests").glob("*.json"))
    if results:
        out.append("## Module tests")
        out.append("")
        out.append("| Scenario | checks | passed | failed | known bugs"
                   " | known bugs not reproduced |")
        out.append("|---|---|---|---|---|---|")
        failed_checks = []
        for path in results:
            checks = json.loads(path.read_text())
            count = {}
            for check in checks:
                count[check.get("status")] = count.get(check.get("status"), 0) + 1
                if check.get("status") in ("failed", "fixed"):
                    failed_checks.append((path.stem, check))
            out.append("| %s | %d | %d | %d | %d | %d |" % (
                path.stem, len(checks), count.get("passed", 0), count.get("failed", 0),
                count.get("known", 0), count.get("fixed", 0)))
        out.append("")
        for scenario, check in failed_checks:
            out.append("- %s `%s` (%s): expected %s, actual %s: %s" % (
                scenario, check.get("id"), check.get("status"), check.get("expect"),
                check.get("actual"), str(check.get("msg", ""))[:300]))
        if failed_checks:
            out.append("")

    # runtime per module of the module tests, slowest first
    durations = sorted((run_dir / "module_durations").glob("*.json"))
    if durations:
        out.append("## Module test durations")
        out.append("")
        out.append("| Scenario | module | duration | share |")
        out.append("|---|---|---|---|")
        for path in durations:
            entries = json.loads(path.read_text())
            total = sum(e.get("duration_s", 0) for e in entries) or 1
            entries.sort(key=lambda e: e.get("duration_s", 0), reverse=True)
            for entry in entries:
                seconds = int(entry.get("duration_s", 0))
                out.append("| %s | %s | %dm%02ds | %d%% |" % (
                    path.stem, entry.get("module"), seconds // 60, seconds % 60,
                    round(100 * entry.get("duration_s", 0) / total)))
            out.append("| %s | **total** | **%dm%02ds** | 100%% |" % (
                path.stem, int(total) // 60, int(total) % 60))
        out.append("")

    # idempotence
    idem = [(s, idempotence_tasks(run_dir / ("%s-idempotence.log" % s)))
            for s in scenarios if (s, "idempotence") in steps]
    if any(tasks for _, tasks in idem):
        out.append("## Idempotence: changed tasks")
        out.append("")
        for s, tasks in idem:
            for task in tasks:
                out.append("- %s: %s" % (s, task))
        out.append("")

    # failed steps
    failed = [st for st in steps.values() if st["rc"] != 0]
    if failed:
        out.append("## Failed steps")
        out.append("")
        for st in sorted(failed, key=lambda x: (x["scenario"], x["step"])):
            out.append("### %s %s (rc=%s, log: %s)" % (
                st["scenario"], st["step"], st["rc"], st["log"]))
            out.append("")
            errors, recap = log_errors(run_dir / st["log"])
            # 'fatal:' stops the play, 'failed: [host] (item=...)' is often rescued
            # (e.g. negative tests) => show the last fatal errors,
            # otherwise the last failures
            fatal = [e for e in errors if e[2]] or errors
            shown = fatal[-MAX_ERRORS:]
            for task, msg, _ in shown:
                out.append("- %s" % task)
                out.append("  `%s`" % msg.replace("`", "'"))
            if len(errors) > len(shown):
                out.append("- %d more failures in the logfile"
                           " (rescued failures included)"
                           % (len(errors) - len(shown)))
            for line in recap:
                out.append("- recap: `%s`" % line)
            out.append("")

    text = "\n".join(out) + "\n"
    (run_dir / "summary.md").write_text(text)
    sys.stdout.write(text)


if __name__ == "__main__":
    main()

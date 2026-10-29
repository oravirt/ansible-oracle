#!/usr/bin/env python3
"""Check requires_ansible of the collection dependencies in galaxy.yml.

Renovate does not know about requires_ansible of a collection, so it
proposes versions which need a newer ansible-core than ansible-oracle
supports. This script asks Ansible Galaxy for every dependency in
galaxy.yml and compares requires_ansible of each version with the minimum
version from requires_ansible in meta/runtime.yml.

For every dependency the following is shown:
- CURRENT:    the newest version matching the version in galaxy.yml
- REQUIRES:   requires_ansible of CURRENT
- COMPATIBLE: the newest version which can be installed with the minimum
              ansible-core version
- LATEST:     the newest version on Galaxy with its requires_ansible

Exit code 1, when CURRENT needs a newer ansible-core than the minimum.
"""

import json
import sys
import urllib.request
from pathlib import Path

import yaml
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parents[2]
GALAXY_URL = "https://galaxy.ansible.com"
VERSIONS_PATH = (
    "/api/v3/plugin/ansible/content/published/collections/index/"
    "{namespace}/{name}/versions/?limit=100"
)


def min_ansible_version():
    runtime = yaml.safe_load((ROOT / "meta" / "runtime.yml").read_text())
    for spec in SpecifierSet(runtime["requires_ansible"]):
        if spec.operator in (">=", "=="):
            return Version(spec.version)
    sys.exit("No minimum version in requires_ansible of meta/runtime.yml")


def galaxy_versions(collection):
    """Return [(Version, requires_ansible)] of all releases, newest first."""
    namespace, name = collection.split(".", 1)
    url = GALAXY_URL + VERSIONS_PATH.format(namespace=namespace, name=name)
    versions = []
    while url:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.load(response)
        for entry in data["data"]:
            try:
                version = Version(entry["version"])
            except InvalidVersion:
                continue
            if not version.is_prerelease:
                versions.append((version, entry.get("requires_ansible")))
        next_link = data["links"]["next"]
        url = GALAXY_URL + next_link if next_link else None
    return sorted(versions, reverse=True)


def to_specifier(value):
    """Version from galaxy.yml as SpecifierSet ('1.2.3' means '==1.2.3')."""
    value = str(value).strip()
    if value in ("", "*"):
        return SpecifierSet()
    if value[0].isdigit():
        value = "==" + value
    return SpecifierSet(value)


def is_compatible(requires_ansible, ansible_version):
    if not requires_ansible:
        return True
    try:
        return ansible_version in SpecifierSet(requires_ansible)
    except InvalidSpecifier:
        return True


def main():
    ansible_version = min_ansible_version()
    galaxy = yaml.safe_load((ROOT / "galaxy.yml").read_text())
    dependencies = galaxy.get("dependencies") or {}

    print(f"Minimum ansible-core from meta/runtime.yml: {ansible_version}\n")
    rows = [("COLLECTION", "GALAXY.YML", "CURRENT", "REQUIRES", "COMPATIBLE", "LATEST")]
    failed = []
    for collection, value in dependencies.items():
        versions = galaxy_versions(collection)
        specifier = to_specifier(value)
        current = next(((v, r) for v, r in versions if v in specifier), None)
        compatible = next(
            (v for v, r in versions if is_compatible(r, ansible_version)), None
        )
        latest = versions[0] if versions else None

        if current and not is_compatible(current[1], ansible_version):
            failed.append(collection)
        rows.append(
            (
                collection,
                str(value),
                str(current[0]) if current else "-",
                (current[1] or "-") if current else "-",
                str(compatible or "-"),
                f"{latest[0]} ({latest[1]})" if latest else "-",
            )
        )

    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    for row in rows:
        print("  ".join(col.ljust(widths[i]) for i, col in enumerate(row)).rstrip())

    if failed:
        print(
            f"\nNot installable with ansible-core {ansible_version}: "
            f"{', '.join(failed)}"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

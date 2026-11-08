#!/usr/bin/env python3
"""Check requires_ansible and dependencies of the collections in galaxy.yml.

Renovate does not know about requires_ansible of a collection, so it
proposes versions which need a newer ansible-core than ansible-oracle
supports. This script asks Ansible Galaxy for every dependency in
galaxy.yml and compares requires_ansible of each version with the minimum
version from requires_ansible in meta/runtime.yml.

Renovate does not check the dependencies of a collection either, e.g.
a collection which needs community.crypto >=3.0.0, while
galaxy.yml allows only community.crypto <3.0.0. The dependencies of a version
must be installable with the version ranges in galaxy.yml and the minimum
ansible-core version (only one level, dependencies of dependencies are not
checked).

For every dependency the following is shown:
- CURRENT:    the newest version matching the version in galaxy.yml
- REQUIRES:   requires_ansible of CURRENT
- COMPATIBLE: the newest version which can be installed with the minimum
              ansible-core version and the version ranges in galaxy.yml
- LATEST:     the newest version on Galaxy with its requires_ansible

Exit code 1, when CURRENT needs a newer ansible-core than the minimum or
a dependency of CURRENT conflicts with galaxy.yml.
"""

import json
import sys
import urllib.request
from functools import cache
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
VERSION_PATH = (
    "/api/v3/plugin/ansible/content/published/collections/index/"
    "{namespace}/{name}/versions/{version}/"
)


def min_ansible_version():
    runtime = yaml.safe_load((ROOT / "meta" / "runtime.yml").read_text())
    for spec in SpecifierSet(runtime["requires_ansible"]):
        if spec.operator in (">=", "=="):
            return Version(spec.version)
    sys.exit("No minimum version in requires_ansible of meta/runtime.yml")


@cache
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


@cache
def galaxy_dependencies(collection, version):
    """Return the dependencies {collection: version range} of one release."""
    namespace, name = collection.split(".", 1)
    url = GALAXY_URL + VERSION_PATH.format(
        namespace=namespace, name=name, version=version
    )
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)
    return data["metadata"].get("dependencies") or {}


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


def conflicts(collection, version, requires_ansible, ansible_version, ranges):
    """Return the reasons, why a release is not installable (empty: installable)."""
    reasons = []
    if not is_compatible(requires_ansible, ansible_version):
        reasons.append(f"requires_ansible {requires_ansible}")
    for dependency, value in galaxy_dependencies(collection, str(version)).items():
        specifier = to_specifier(value) & ranges.get(dependency, SpecifierSet())
        if not any(
            v in specifier and is_compatible(r, ansible_version)
            for v, r in galaxy_versions(dependency)
        ):
            reason = f"{dependency}{to_specifier(value)}"
            if dependency in ranges:
                reason += f" (galaxy.yml: {ranges[dependency]})"
            reasons.append(reason)
    return reasons


def main():
    ansible_version = min_ansible_version()
    galaxy = yaml.safe_load((ROOT / "galaxy.yml").read_text())
    dependencies = galaxy.get("dependencies") or {}
    ranges = {c: to_specifier(v) for c, v in dependencies.items()}

    print(f"Minimum ansible-core from meta/runtime.yml: {ansible_version}\n")
    rows = [("COLLECTION", "GALAXY.YML", "CURRENT", "REQUIRES", "COMPATIBLE", "LATEST")]
    failed = []
    for collection, value in dependencies.items():
        versions = galaxy_versions(collection)
        specifier = ranges[collection]
        current = next(((v, r) for v, r in versions if v in specifier), None)
        compatible = next(
            (
                v
                for v, r in versions
                if not conflicts(collection, v, r, ansible_version, ranges)
            ),
            None,
        )
        latest = versions[0] if versions else None

        if current:
            reasons = conflicts(
                collection, current[0], current[1], ansible_version, ranges
            )
            if reasons:
                failed.append(f"{collection} {current[0]}: {', '.join(reasons)}")
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
        print(f"\nNot installable with ansible-core {ansible_version}:")
        for line in failed:
            print(f"  {line}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

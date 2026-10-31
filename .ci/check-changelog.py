# noqa: INP001


import argparse
import re
import subprocess
import sys
from typing import Set, Tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changelog", type=str, help="Path to the changelog file", required=True)
    args = parser.parse_args()
    git_versions = get_git_minor_versions()
    changelog_versions = get_changelog_versions(args.changelog)
    missing_versions = git_versions - changelog_versions
    if missing_versions:
        print("The following versions are missing from the changelog:")  # noqa: T201
        for version in sorted(missing_versions, key=version_to_tuple):
            print(f"- v{version}")  # noqa: T201
        sys.exit(1)
    changelog_extras = changelog_versions - git_versions
    if changelog_extras:
        print("The following versions are in the changelog but not in git tags:")  # noqa: T201
        for version in sorted(changelog_extras, key=version_to_tuple):
            print(f"- v{version}")  # noqa: T201
        sys.exit(1)
    print("All versions are present in the changelog.")  # noqa: T201


def get_git_minor_versions() -> Set[str]:
    """
    Get all major/minor versions (but not patch versions) from git tags.
    """
    tags = subprocess.check_output(["git", "tag", "--list"]).decode().splitlines()  # noqa: S607
    major_minor_re = re.compile(r"^v(\d+\.\d+)\.\d+$")
    versions: Set[str] = set()
    for tag in tags:
        m = major_minor_re.match(tag)
        if m:
            versions.add(m.group(1))
    return versions


def get_changelog_versions(changelog_path: str) -> Set[str]:
    """
    Get all versions listed in the changelog.
    """
    with open(changelog_path) as f:
        changelog = f.read()
    version_re = re.compile(r"^- v(\d+\.\d+)$", re.MULTILINE)
    return {m.group(1) for m in version_re.finditer(changelog)}


def version_to_tuple(version: str) -> Tuple[int, ...]:
    """
    Convert a version string without the "v" prefix to a tuple.
    """
    return tuple(int(i) for i in version.split("."))


if __name__ == "__main__":
    main()

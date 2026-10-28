#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for managing releases in ansible-oracle
#
# - set the collection version in galaxy.yml from the current branch
#   (pr/<version>) and update all requirements.yml with galaxy_version.sh
# - commit the new version as initial commit for the release pull request
# - push the branch to origin and create the release pull request
# - add pull request references to the changelog fragments
# - create the changelog and write the new release notes into the pull request
#
# Usage: build_release.sh [-i] [-r <owner/repo>]
#
#   -i  ignore changelog fragments without pull request reference
#       (useful for tests against a fork)
#   -r  GitHub repository for the pull request (default: oravirt/ansible-oracle)
#
# Needs gh (GitHub CLI) with a valid login.

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

galaxy="galaxy.yml"
repo="oravirt/ansible-oracle"
remote="origin"
antsibull=".venv/antsibull/bin/antsibull-changelog"
ignore_fragments=false
pr_url=""

function usage() {
  echo "Usage: $0 [-i] [-r <owner/repo>]"
  exit 2
}

function branch_version() {
  if [[ ! "${branch}" =~ ^pr/([0-9]+\.[0-9]+\.[0-9]+)$ ]] ; then
    echo "Branch '${branch}' does not match pr/<major>.<minor>.<patch>" >&2
    return 1
  fi
  echo "${BASH_REMATCH[1]}"
}

function set_galaxy_version() {
  echo "Using version from branch: ${version}"
  sed -i -E "s/^version:.*/version: ${version}/" "${galaxy}"
  grep -E "^version:" "${galaxy}"
}

# owner of the remote repository, e.g. Rendanic for git@github.com:Rendanic/ansible-oracle.git
function remote_owner() {
  git remote get-url "${remote}" | sed -E 's#.*[:/]([^/]+)/[^/]+$#\1#'
}

# only galaxy.yml and requirements.yml are committed, other changes are kept
function commit_version() {
  local files
  files=$(git ls-files -- "${galaxy}" '*requirements.yml')

  # shellcheck disable=SC2086
  if git diff --quiet HEAD -- ${files} ; then
    echo "Version ${version} already committed"
    return
  fi
  echo "Committing version ${version}"
  # shellcheck disable=SC2086
  git commit --only -m "Release ${version}" -- ${files}
}

function push_branch() {
  echo "Pushing ${branch} to ${remote}"
  git push --set-upstream "${remote}" "${branch}"
}

function create_pull_request() {
  local head
  head="$(remote_owner):${branch}"

  pr_url=$(gh pr list --repo "${repo}" --head "${branch}" --state open \
    --json url --jq '.[0].url // empty')
  if [ -n "${pr_url}" ] ; then
    echo "Pull request already exists: ${pr_url}"
    return
  fi

  echo "Creating pull request in ${repo} for ${head}"
  pr_url=$(gh pr create --repo "${repo}" --head "${head}" \
    --title "Release ${version}" \
    --body "Release ${version} of opitzconsulting.ansible_oracle")
  echo "${pr_url}"
}

function fix_fragments() {
  echo "Adding pull request references to changelog fragments"
  if ! tools/release/fix_fragments.py --repo "${repo}" ; then
    if [ "${ignore_fragments}" = true ] ; then
      echo "Ignoring problems with changelog fragments"
    else
      echo "Problems with changelog fragments found, use -i to ignore them" >&2
      return 1
    fi
  fi
}

function make_changelog() {
  echo "Starting antsibull-changelog release"
  "${antsibull}" release
}

# release notes of the new version only, as pull request description
function update_pull_request() {
  local notes
  notes=$(mktemp)
  trap 'rm -f "${notes}"' RETURN

  "${antsibull}" generate --output "${notes}" --only-latest --output-format md
  echo "Updating description of ${pr_url}"
  gh pr edit "${pr_url}" --body-file "${notes}"
}

while getopts "ir:" opt ; do
  case "${opt}" in
    i) ignore_fragments=true ;;
    r) repo="${OPTARG}" ;;
    *) usage ;;
  esac
done
shift $((OPTIND - 1))
[ $# -eq 0 ] || usage

branch=$(git branch --show-current)
version=$(branch_version)

set_galaxy_version
tools/release/galaxy_version.sh fix
commit_version
push_branch
create_pull_request
fix_fragments
make_changelog
update_pull_request

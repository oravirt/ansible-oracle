#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for managing releases in ansible-oracle
#
# Mode pr:
# - set the collection version in galaxy.yml from the current branch
#   (pr/<version>) and update all requirements.yml with galaxy_version.sh
# - commit the new version as initial commit for the release pull request
# - push the branch to origin and create the release pull request
# - add pull request references to the changelog fragments
# - create the changelog and write the new release notes into the pull request
#
# Mode release:
# - create the tag v<version> for the release pull request
#   (merge commit, or last commit of the pull request when it is still open)
# - create a draft release with the description of the pull request
# - update the website with tools/release/build_website.sh -m push
#   (only for oravirt/ansible-oracle, skipped for tests against a fork)
#
# Mode galaxy:
# - sync master of the fork of the gh user with master of the upstream
#   repository at once, to take over a release merged in upstream without
#   waiting (only on GitHub, nothing is changed locally)
# - when the last commit is a release commit (Release <version>), check that
#   the latest release of the upstream repository points to this commit
# - in this case start the workflow 'Deploy Collection' in the fork and
#   watch it, when the version is not on Ansible Galaxy yet
#
# Mode docs:
# - update the website with tools/release/build_website.sh -m push, like the
#   last step of mode release (no release branch needed)
#
# Usage: build_release.sh -m pr|release|galaxy|docs [-i] [-r <owner/repo>]
#
#   -m  pr: create the release pull request, release: create the draft release,
#       galaxy: sync master of the fork with the upstream repository,
#       docs: update the website
#   -i  ignore changelog fragments without pull request reference
#       (useful for tests against a fork)
#   -r  GitHub repository for the pull request and release, source for the
#       sync of the fork (default: oravirt/ansible-oracle)
#
# Needs gh (GitHub CLI) with a valid login, jq and curl.

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

galaxy="galaxy.yml"
upstream_repo="oravirt/ansible-oracle"
repo="${upstream_repo}"
remote="origin"
antsibull=".venv/antsibull/bin/antsibull-changelog"
collection="opitzconsulting/ansible_oracle"
deploy_workflow="Deploy Collection"
ignore_fragments=false
mode=""
pr_url=""

function usage() {
  echo "Usage: $0 -m pr|release|galaxy|docs [-i] [-r <owner/repo>]"
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

# git remote for the GitHub repository, e.g. upstream for oravirt/ansible-oracle
function repo_remote() {
  local name
  for name in $(git remote) ; do
    if git remote get-url "${name}" | grep -qiE "[:/]${repo}(\.git)?$" ; then
      echo "${name}"
      return
    fi
  done
  echo "No git remote found for ${repo}" >&2
  return 1
}

# pull request of the branch from our fork as JSON, empty when not existing
# $1: open or merged
function find_pull_request() {
  local states
  case "$1" in
    open)   states='["OPEN"]' ;;
    merged) states='["OPEN", "MERGED"]' ;;
  esac

  gh pr list --repo "${repo}" --head "${branch}" --state all \
    --json number,url,state,body,headRefOid,mergeCommit,headRepositoryOwner \
    | jq -c --arg owner "$(remote_owner)" --argjson states "${states}" \
      '[.[] | select(.headRepositoryOwner.login == $owner)
            | select(.state as $s | $states | index($s))] | .[0] // empty'
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

  pr_url=$(find_pull_request open | jq -r '.url // empty')
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

# $1: commit for the tag, $2: pull request number
function create_tag() {
  local commit=$1 number=$2 tag_remote existing
  tag_remote=$(repo_remote)

  if ! git cat-file -e "${commit}^{commit}" 2>/dev/null ; then
    git fetch --quiet "${tag_remote}"
  fi
  if ! git cat-file -e "${commit}^{commit}" 2>/dev/null ; then
    git fetch --quiet "${tag_remote}" "refs/pull/${number}/head"
  fi

  existing=$(git rev-parse --quiet --verify "refs/tags/${tag}^{commit}" || true)
  if [ -z "${existing}" ] ; then
    echo "Creating tag ${tag} for commit ${commit}"
    git tag "${tag}" "${commit}"
  elif [ "${existing}" != "${commit}" ] ; then
    echo "Tag ${tag} already exists for commit ${existing}, expected ${commit}" >&2
    return 1
  else
    echo "Tag ${tag} already exists for commit ${commit}"
  fi

  echo "Pushing tag ${tag} to ${tag_remote}"
  git push "${tag_remote}" "refs/tags/${tag}"
}

function create_release() {
  local pr commit number is_draft notes
  pr=$(find_pull_request merged)
  if [ -z "${pr}" ] ; then
    echo "No open or merged pull request found for ${branch} in ${repo}" >&2
    return 1
  fi

  number=$(jq -r '.number' <<< "${pr}")
  if [ "$(jq -r '.state' <<< "${pr}")" = "MERGED" ] ; then
    commit=$(jq -r '.mergeCommit.oid' <<< "${pr}")
  else
    commit=$(jq -r '.headRefOid' <<< "${pr}")
    echo "Pull request $(jq -r '.url' <<< "${pr}") is not merged, using its last commit"
  fi

  create_tag "${commit}" "${number}"

  notes=$(mktemp)
  trap 'rm -f "${notes}"' RETURN
  jq -j '.body' <<< "${pr}" > "${notes}"

  is_draft=$(gh release view "${tag}" --repo "${repo}" --json isDraft --jq '.isDraft' 2>/dev/null || true)
  case "${is_draft}" in
    true)
      echo "Updating draft release ${tag} in ${repo}"
      gh release edit "${tag}" --repo "${repo}" --notes-file "${notes}"
      ;;
    false)
      echo "Release ${tag} is already published in ${repo}" >&2
      return 1
      ;;
    *)
      echo "Creating draft release ${tag} in ${repo}"
      gh release create "${tag}" --repo "${repo}" --draft --verify-tag \
        --title "Release ${version}" --notes-file "${notes}"
      ;;
  esac
}

# the website is built from the local checkout and published at once
function update_website() {
  if [ "${repo,,}" != "${upstream_repo,,}" ] ; then
    echo "Website is only updated for ${upstream_repo}, skipped for ${repo}"
    return
  fi
  echo "Updating the website"
  tools/release/build_website.sh -m push
}

# without --force: gh refuses the sync, when master of the fork has own commits
function sync_fork() {
  local fork
  fork="$(gh api user --jq '.login')/${repo#*/}"

  if [ "${fork,,}" = "${repo,,}" ] ; then
    echo "Fork ${fork} and source ${repo} are the same repository" >&2
    return 1
  fi

  echo "Syncing master of ${fork} with ${repo}"
  gh repo sync "${fork}" --source "${repo}" --branch master
  check_release "${fork}"
}

# $1: fork with the synced master
function check_release() {
  local fork=$1 commit subject release_tag release_commit
  commit=$(gh api "repos/${fork}/commits/master" --jq '.sha')
  subject=$(gh api "repos/${fork}/commits/master" --jq '.commit.message | split("\n")[0]')
  echo "master of ${fork}: ${commit:0:8} ${subject}"

  if [[ ! "${subject}" =~ ^Release\ [0-9]+\.[0-9]+\.[0-9]+$ ]] ; then
    echo "Last commit is not a release commit"
    return
  fi

  # latest published release, drafts and pre-releases are ignored by GitHub
  release_tag=$(gh release view --repo "${repo}" --json tagName --jq '.tagName' 2>/dev/null || true)
  if [ -z "${release_tag}" ] ; then
    echo "No published release found in ${repo}"
    return
  fi
  release_commit=$(gh api "repos/${repo}/commits/${release_tag}" --jq '.sha')

  if [ "${release_commit}" = "${commit}" ] ; then
    echo "Latest release ${release_tag} of ${repo} is the last commit of ${fork}"
    deploy_collection "${fork}" "${release_tag#v}"
  else
    echo "Latest release ${release_tag} of ${repo} points to ${release_commit:0:8}, not to the last commit ${commit:0:8}"
  fi
}

# $1: version
function galaxy_has_version() {
  local status
  status=$(curl -s -o /dev/null -w '%{http_code}' \
    "https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/${collection}/versions/$1/")
  case "${status}" in
    200) return 0 ;;
    404) return 1 ;;
    *)
      echo "Ansible Galaxy returned HTTP ${status} for ${collection} $1" >&2
      exit 1
      ;;
  esac
}

# $1: fork, $2: version
function deploy_collection() {
  local fork=$1 deploy_version=$2 started run_id

  if galaxy_has_version "${deploy_version}" ; then
    echo "Version ${deploy_version} of ${collection} is already on Ansible Galaxy"
    return
  fi

  # small offset for differences between local and GitHub clock
  started=$(date -u -d '-30 seconds' +%Y-%m-%dT%H:%M:%SZ)
  echo "Starting workflow '${deploy_workflow}' in ${fork} for ${deploy_version}"
  gh workflow run "${deploy_workflow}" --repo "${fork}" --ref master

  # gh workflow run does not return the id of the new run
  for _ in $(seq 1 30) ; do
    run_id=$(gh run list --repo "${fork}" --workflow "${deploy_workflow}" \
      --event workflow_dispatch --branch master --limit 5 \
      --json databaseId,createdAt \
      --jq "[.[] | select(.createdAt >= \"${started}\")] | .[0].databaseId // empty")
    [ -n "${run_id}" ] && break
    sleep 2
  done
  if [ -z "${run_id}" ] ; then
    echo "Run of workflow '${deploy_workflow}' not found in ${fork}" >&2
    return 1
  fi

  if ! gh run watch "${run_id}" --repo "${fork}" --exit-status --interval 5 ; then
    gh run view "${run_id}" --repo "${fork}" --log-failed
    echo "Workflow '${deploy_workflow}' failed" >&2
    return 1
  fi
  gh run view "${run_id}" --repo "${fork}"
}

while getopts "im:r:" opt ; do
  case "${opt}" in
    i) ignore_fragments=true ;;
    m) mode="${OPTARG}" ;;
    r) repo="${OPTARG}" ;;
    *) usage ;;
  esac
done
shift $((OPTIND - 1))
[ $# -eq 0 ] || usage

if [ "${mode}" = pr ] || [ "${mode}" = release ] ; then
  branch=$(git branch --show-current)
  version=$(branch_version)
  tag="v${version}"
fi

case "${mode}" in
  pr)
    set_galaxy_version
    tools/release/galaxy_version.sh fix
    commit_version
    push_branch
    create_pull_request
    fix_fragments
    make_changelog
    update_pull_request
    ;;
  release)
    create_release
    update_website
    ;;
  galaxy)
    sync_fork
    ;;
  docs)
    update_website
    ;;
  *)
    usage
    ;;
esac

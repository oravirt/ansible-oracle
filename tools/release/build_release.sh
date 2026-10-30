#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for managing releases in ansible-oracle
#
# Releases are built from master or from a maintenance branch release/<major>.x
# (e.g. release/4.x). The branch is the base of the release pull request.
#
# Mode pr:
# - set the collection version in galaxy.yml from the current branch
#   (pr/<version>) and update all requirements.yml with galaxy_version.sh
# - commit the new version as initial commit for the release pull request
# - push the branch to origin and create the release pull request against the
#   base branch (option -b, default: see base_branch)
# - add pull request references to the changelog fragments
# - create the changelog and write the new release notes into the pull request
#
# Mode release:
# - create the tag v<version> for the merged release pull request
#   (for tests against a fork also the last commit of an open pull request)
# - create a draft release with the description of the pull request,
#   only releases from master are marked as latest release
# - update the website with tools/release/build_website.sh -m push
#   (only for releases from master of oravirt/ansible-oracle)
#
# Mode galaxy:
# - take the release (option -t, default: latest release) of the upstream
#   repository and search the branch with the content of the release as last
#   commit (master or release/<major>.x), the trees are compared, because a
#   rebase merge creates new commits
# - sync this branch of the fork of the gh user with the upstream repository
#   (the branch is created in the fork, when it is missing)
# - start the workflow 'Deploy Collection' in the fork for this branch and
#   watch it, when the version is not on Ansible Galaxy yet
#   (only on GitHub, nothing is changed locally)
#
# Mode docs:
# - update the website with tools/release/build_website.sh -m push, like the
#   last step of mode release (no release branch needed)
#
# Usage: build_release.sh -m pr|release|galaxy|docs [-b <branch>] [-t <tag>] [-n] [-i] [-r <owner/repo>]
#
#   -m  pr: create the release pull request, release: create the draft release,
#       galaxy: sync the fork and deploy the release to Ansible Galaxy,
#       docs: update the website
#   -b  base branch of the release pull request (only -m pr)
#   -t  release tag for -m galaxy, e.g. v4.17.1 (default: latest release)
#   -n  dry-run: show what would be done, nothing is changed locally or on GitHub
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
default_branch="master"
antsibull=".venv/antsibull/bin/antsibull-changelog"
collection="opitzconsulting/ansible_oracle"
deploy_workflow="Deploy Collection"
ignore_fragments=false
dry_run=false
mode=""
base=""
release_tag=""
pr_url=""

function usage() {
  echo "Usage: $0 -m pr|release|galaxy|docs [-b <branch>] [-t <tag>] [-n] [-i] [-r <owner/repo>]"
  exit 2
}

# execute a command, which changes something locally or on GitHub
function run() {
  if [ "${dry_run}" = true ] ; then
    echo "DRY-RUN: $*"
  else
    "$@"
  fi
}

function branch_version() {
  if [[ ! "${branch}" =~ ^pr/([0-9]+\.[0-9]+\.[0-9]+)$ ]] ; then
    echo "Branch '${branch}' does not match pr/<major>.<minor>.<patch>" >&2
    return 1
  fi
  echo "${BASH_REMATCH[1]}"
}

# $1: repository, $2: branch
function branch_exists() {
  gh api "repos/$1/branches/$2" --silent 2>/dev/null
}

# $1: branch, version of the collection in galaxy.yml of this branch in repo
function repo_galaxy_version() {
  gh api -H "Accept: application/vnd.github.raw" "repos/${repo}/contents/${galaxy}?ref=$1" \
    | sed -n -E "s/^version:\s*([^[:space:]]+).*/\1/p"
}

# Default base branch for the version:
# - master, when the major version is the same or higher than on master
# - release/<major>.x for an older major version
function base_branch() {
  local major master_version
  major=${version%%.*}
  master_version=$(repo_galaxy_version "${default_branch}")

  if [ "${major}" -ge "${master_version%%.*}" ] ; then
    echo "${default_branch}"
  elif branch_exists "${repo}" "release/${major}.x" ; then
    echo "release/${major}.x"
  else
    echo "No branch release/${major}.x in ${repo} for version ${version} (${default_branch}: ${master_version}), use -b" >&2
    return 1
  fi
}

# the pull request may only contain the commits of the release branch
function check_base() {
  local base_remote
  if ! branch_exists "${repo}" "${base}" ; then
    echo "Base branch ${base} does not exist in ${repo}" >&2
    return 1
  fi

  base_remote=$(repo_remote)
  git fetch --quiet "${base_remote}" "${base}"
  if ! git merge-base --is-ancestor FETCH_HEAD HEAD ; then
    echo "${branch} is not based on the current ${base} of ${repo}, rebase it onto ${base_remote}/${base}" >&2
    return 1
  fi
  echo "Base branch: ${base} of ${repo}"
}

function set_galaxy_version() {
  echo "Using version from branch: ${version}"
  run sed -i -E "s/^version:.*/version: ${version}/" "${galaxy}"
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
    --json number,url,state,body,headRefOid,mergeCommit,headRepositoryOwner,baseRefName \
    | jq -c --arg owner "$(remote_owner)" --argjson states "${states}" \
      '[.[] | select(.headRepositoryOwner.login == $owner)
            | select(.state as $s | $states | index($s))] | .[0] // empty'
}

# only galaxy.yml and requirements.yml are committed, other changes are kept
function commit_version() {
  local files
  files=$(git ls-files -- "${galaxy}" '*requirements.yml')

  # shellcheck disable=SC2086
  if [ "${dry_run}" = false ] && git diff --quiet HEAD -- ${files} ; then
    echo "Version ${version} already committed"
    return
  fi
  echo "Committing version ${version}"
  # shellcheck disable=SC2086
  run git commit --only -m "Release ${version}" -- ${files}
}

function push_branch() {
  echo "Pushing ${branch} to ${remote}"
  run git push --set-upstream "${remote}" "${branch}"
}

function create_pull_request() {
  local head pr
  head="$(remote_owner):${branch}"

  pr=$(find_pull_request open)
  if [ -n "${pr}" ] ; then
    pr_url=$(jq -r '.url' <<< "${pr}")
    echo "Pull request already exists: ${pr_url}"
    if [ "$(jq -r '.baseRefName' <<< "${pr}")" != "${base}" ] ; then
      echo "The pull request is based on $(jq -r '.baseRefName' <<< "${pr}"), not on ${base}" >&2
      return 1
    fi
    return
  fi

  echo "Creating pull request in ${repo} for ${head} against ${base}"
  if [ "${dry_run}" = true ] ; then
    run gh pr create --repo "${repo}" --base "${base}" --head "${head}" --title "Release ${version}"
    pr_url="<new pull request>"
    return
  fi
  pr_url=$(gh pr create --repo "${repo}" --base "${base}" --head "${head}" \
    --title "Release ${version}" \
    --body "Release ${version} of opitzconsulting.ansible_oracle")
  echo "${pr_url}"
}

function fix_fragments() {
  echo "Adding pull request references to changelog fragments"
  if [ "${dry_run}" = true ] ; then
    tools/release/fix_fragments.py --repo "${repo}" --dry-run || true
    return
  fi
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
  run "${antsibull}" release
}

# release notes of the new version only, as pull request description
function update_pull_request() {
  local notes
  if [ "${dry_run}" = true ] ; then
    run gh pr edit "${pr_url}" --body-file "<release notes of ${version}>"
    return
  fi
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
    run git tag "${tag}" "${commit}"
  elif [ "${existing}" != "${commit}" ] ; then
    echo "Tag ${tag} already exists for commit ${existing}, expected ${commit}" >&2
    return 1
  else
    echo "Tag ${tag} already exists for commit ${commit}"
  fi

  echo "Pushing tag ${tag} to ${tag_remote}"
  run git push "${tag_remote}" "refs/tags/${tag}"
}

function create_release() {
  local pr commit number is_draft notes latest
  pr=$(find_pull_request merged)
  if [ -z "${pr}" ] ; then
    echo "No open or merged pull request found for ${branch} in ${repo}" >&2
    return 1
  fi

  number=$(jq -r '.number' <<< "${pr}")
  base=$(jq -r '.baseRefName' <<< "${pr}")
  echo "Pull request $(jq -r '.url' <<< "${pr}") against ${base}"
  if [ "$(jq -r '.state' <<< "${pr}")" = "MERGED" ] ; then
    commit=$(jq -r '.mergeCommit.oid' <<< "${pr}")
  elif [ "${repo,,}" = "${upstream_repo,,}" ] ; then
    # a rebase merge creates new commits, the tag would not be part of the branch
    echo "Pull request is not merged yet, merge it before creating the release" >&2
    return 1
  else
    commit=$(jq -r '.headRefOid' <<< "${pr}")
    echo "Pull request is not merged, using its last commit (test against a fork)"
  fi

  create_tag "${commit}" "${number}"

  notes=$(mktemp)
  trap 'rm -f "${notes}"' RETURN
  jq -j '.body' <<< "${pr}" > "${notes}"

  # releases of maintenance branches must not replace the latest release of master
  if [ "${base}" = "${default_branch}" ] ; then
    latest="--latest"
  else
    latest="--latest=false"
    echo "Release from ${base} is not marked as latest release"
  fi

  is_draft=$(gh release view "${tag}" --repo "${repo}" --json isDraft --jq '.isDraft' 2>/dev/null || true)
  case "${is_draft}" in
    true)
      echo "Updating draft release ${tag} in ${repo}"
      run gh release edit "${tag}" --repo "${repo}" --notes-file "${notes}" "${latest}"
      ;;
    false)
      echo "Release ${tag} is already published in ${repo}" >&2
      return 1
      ;;
    *)
      echo "Creating draft release ${tag} in ${repo}"
      run gh release create "${tag}" --repo "${repo}" --draft --verify-tag "${latest}" \
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
  if [ -n "${base}" ] && [ "${base}" != "${default_branch}" ] ; then
    echo "Website is only updated for releases from ${default_branch}, skipped for ${base}"
    return
  fi
  echo "Updating the website"
  run tools/release/build_website.sh -m push
}

# $1: repository, $2: commit
function commit_tree() {
  gh api "repos/$1/git/commits/$2" --jq '.tree.sha' 2>/dev/null
}

# $1: repository, $2: release commit
# branch of repo with the content of the release as last commit: master or release/<major>.x
# The trees are compared, the commit differs after a rebase merge of the release pull request.
function release_branch() {
  local candidate head release_tree
  release_tree=$(commit_tree "$1" "$2")
  for candidate in "${default_branch}" "release/${release_version%%.*}.x" ; do
    head=$(gh api "repos/$1/branches/${candidate}" --jq '.commit.sha' 2>/dev/null) || continue
    if [ "$(commit_tree "$1" "${head}")" = "${release_tree}" ] ; then
      echo "${candidate} ${head}"
      return
    fi
  done
}

# without --force: gh refuses the sync, when the branch of the fork has own commits
function sync_fork() {
  local fork commit release_br branch_commit fork_commit
  fork="$(gh api user --jq '.login')/${repo#*/}"

  if [ "${fork,,}" = "${repo,,}" ] ; then
    echo "Fork ${fork} and source ${repo} are the same repository" >&2
    return 1
  fi

  if [ -z "${release_tag}" ] ; then
    # latest published release, drafts and pre-releases are ignored by GitHub
    release_tag=$(gh release view --repo "${repo}" --json tagName --jq '.tagName' 2>/dev/null || true)
    if [ -z "${release_tag}" ] ; then
      echo "No published release found in ${repo}" >&2
      return 1
    fi
  fi
  release_version=${release_tag#v}
  commit=$(gh api "repos/${repo}/commits/${release_tag}" --jq '.sha')
  echo "Release ${release_tag} of ${repo}: ${commit:0:8}"

  read -r release_br branch_commit <<< "$(release_branch "${repo}" "${commit}")"
  if [ -z "${release_br}" ] ; then
    echo "Release ${release_tag} is not the last commit of ${default_branch} or release/${release_version%%.*}.x in ${repo}, no deployment"
    return
  fi
  if [ "${branch_commit}" = "${commit}" ] ; then
    echo "Release ${release_tag} is the last commit of ${release_br}"
  else
    echo "Release ${release_tag} has the same content as the last commit ${branch_commit:0:8} of ${release_br}"
  fi

  if branch_exists "${fork}" "${release_br}" ; then
    echo "Syncing ${release_br} of ${fork} with ${repo}"
    run gh repo sync "${fork}" --source "${repo}" --branch "${release_br}"
  else
    echo "Creating ${release_br} in ${fork}"
    run gh api "repos/${fork}/git/refs" -f "ref=refs/heads/${release_br}" -f "sha=${branch_commit}" --silent
  fi

  if [ "${dry_run}" = false ] ; then
    fork_commit=$(gh api "repos/${fork}/branches/${release_br}" --jq '.commit.sha')
    if [ "${fork_commit}" != "${branch_commit}" ] ; then
      echo "${release_br} of ${fork} is ${fork_commit:0:8}, not ${branch_commit:0:8} of ${repo}" >&2
      return 1
    fi
  fi
  deploy_collection "${fork}" "${release_br}"
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

# $1: fork, $2: branch with the release
function deploy_collection() {
  local fork=$1 deploy_branch=$2 started run_id

  if galaxy_has_version "${release_version}" ; then
    echo "Version ${release_version} of ${collection} is already on Ansible Galaxy"
    return
  fi

  # small offset for differences between local and GitHub clock
  started=$(date -u -d '-30 seconds' +%Y-%m-%dT%H:%M:%SZ)
  echo "Starting workflow '${deploy_workflow}' in ${fork} on ${deploy_branch} for ${release_version}"
  run gh workflow run "${deploy_workflow}" --repo "${fork}" --ref "${deploy_branch}"
  [ "${dry_run}" = false ] || return 0

  # gh workflow run does not return the id of the new run
  for _ in $(seq 1 30) ; do
    run_id=$(gh run list --repo "${fork}" --workflow "${deploy_workflow}" \
      --event workflow_dispatch --branch "${deploy_branch}" --limit 5 \
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

while getopts "b:im:nr:t:" opt ; do
  case "${opt}" in
    b) base="${OPTARG}" ;;
    i) ignore_fragments=true ;;
    m) mode="${OPTARG}" ;;
    n) dry_run=true ;;
    r) repo="${OPTARG}" ;;
    t) release_tag="${OPTARG}" ;;
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
[ "${dry_run}" = false ] || echo "Dry-run: nothing is changed locally or on GitHub"

case "${mode}" in
  pr)
    [ -n "${base}" ] || base=$(base_branch)
    check_base
    set_galaxy_version
    run tools/release/galaxy_version.sh fix
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

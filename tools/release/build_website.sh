#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for updating the website www.ansible-oracle.eu
#
# The website is generated with hugo from website/, doc/ and roles/*/README.md
# (see doc/website.adoc) and published with GitHub Pages from the directory
# docs/ in the branch main of the website repository.
#
# - check that website/, doc/, roles/ and docker/hugo/ have no uncommitted changes
# - build the website with 'task website:build' and check the links
# - clone or update the website repository (default: ~/.cache/ansible-oracle-website)
# - replace docs/ with the new build, keep CNAME, add .nojekyll
#   (GitHub Pages ignores directories with a leading '_' like _print/ without it)
# - commit the changes
#
# Mode local (default): only commit in the local clone, nothing is pushed
# Mode push: push the commit to main => GitHub Pages publishes the website
#            (also commits of earlier runs in mode local, which were not pushed)
# Mode pr: push the commit to a new branch website/<commit> and create a pull request
#
# Usage: build_website.sh [-m local|push|pr] [-r <owner/repo>] [-d <dir>] [-a] [-f]
#
#   -m  local: commit only, push: push to main, pr: create a pull request (default: local)
#   -r  GitHub repository of the website (default: Rendanic/ansible-oracle-website)
#   -d  directory for the clone of the website repository
#       (default: ${XDG_CACHE_HOME:-~/.cache}/ansible-oracle-website)
#   -a  run the accessibility check (task website:check:a11y) before the commit
#   -f  force: allow uncommitted changes and a missing legal notice
#
# Needs gh (GitHub CLI) with a valid login, git, rsync, task and docker (see website/Taskfile.yml).

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

repo="Rendanic/ansible-oracle-website"
branch="main"
clone_dir="${XDG_CACHE_HOME:-${HOME}/.cache}/ansible-oracle-website"
public="website/public"
sources="website doc roles docker/hugo"
mode="local"
a11y=false
force=false

function usage() {
  echo "Usage: $0 [-m local|push|pr] [-r <owner/repo>] [-d <dir>] [-a] [-f]"
  exit 2
}

function check_tools() {
  local tool missing=false
  for tool in gh git rsync task docker ; do
    if ! command -v "${tool}" > /dev/null ; then
      echo "${tool} not found (start nix-shell in the repository root)" >&2
      missing=true
    fi
  done
  [ "${missing}" = false ] || exit 1
}

# uncommitted changes would be published without being in git
function check_sources() {
  local changes
  # shellcheck disable=SC2086
  changes=$(git status --porcelain -- ${sources})
  if [ -n "${changes}" ] ; then
    echo "Uncommitted changes in ${sources}:" >&2
    echo "${changes}" >&2
    if [ "${force}" = false ] ; then
      echo "Commit the changes or use -f" >&2
      exit 1
    fi
    echo "Continue because of -f"
  fi
}

function build_website() {
  echo "Building the website from $(git describe --tags --always --dirty)"
  task website:build
  task website:check:links
  if [ "${a11y}" = true ] ; then
    task website:check:a11y
  fi
}

# The legal notice is a draft until all placeholders are filled => it is missing in the build
function check_legal_notice() {
  if [ ! -f "${public}/legal-notice/index.html" ] ; then
    echo "The legal notice (website/content/legal-notice.md) is missing in the build (draft: true?)" >&2
    if [ "${force}" = false ] ; then
      echo "Publish the legal notice or use -f" >&2
      exit 1
    fi
    echo "Continue because of -f"
  fi
}

function prepare_clone() {
  if [ ! -d "${clone_dir}/.git" ] ; then
    echo "Cloning ${repo} into ${clone_dir}"
    mkdir -p "$(dirname "${clone_dir}")"
    gh repo clone "${repo}" "${clone_dir}" -- --quiet
  fi

  if [ -n "$(git -C "${clone_dir}" status --porcelain)" ] ; then
    echo "${clone_dir} has uncommitted changes" >&2
    exit 1
  fi

  echo "Updating ${clone_dir} from origin/${branch}"
  git -C "${clone_dir}" fetch --quiet origin "${branch}"
  if [ "${mode}" = pr ] ; then
    git -C "${clone_dir}" switch --quiet -C "${pr_branch}" "origin/${branch}"
  else
    git -C "${clone_dir}" switch --quiet "${branch}"
    git -C "${clone_dir}" merge --quiet --ff-only "origin/${branch}"
  fi
}

function sync_docs() {
  echo "Replacing docs/ in ${clone_dir}"
  rsync -a --delete --exclude CNAME --exclude .nojekyll "${public}/" "${clone_dir}/docs/"
  cp "${clone_dir}/CNAME" "${clone_dir}/docs/CNAME"
  touch "${clone_dir}/docs/.nojekyll"
}

function commit_docs() {
  git -C "${clone_dir}" add --all docs
  if git -C "${clone_dir}" diff --cached --quiet ; then
    echo "No new changes in the website"
    return
  fi
  git -C "${clone_dir}" commit --quiet \
    -m "website: ansible-oracle ${source_version}" \
    -m "Generated from ansible-oracle commit ${source_commit} by tools/release/build_website.sh"
  git -C "${clone_dir}" show --stat --format='%h %s' HEAD | tail -1
}

function publish() {
  case "${mode}" in
    local)
      echo "${unpushed} commit(s) in ${clone_dir} not pushed."
      echo "Publish with: git -C ${clone_dir} push origin ${branch}"
      ;;
    push)
      git -C "${clone_dir}" push --quiet origin "${branch}"
      echo "Pushed to ${repo} ${branch}, GitHub Pages publishes the website in a few minutes"
      ;;
    pr)
      git -C "${clone_dir}" push --quiet --set-upstream origin "${pr_branch}"
      gh pr create --repo "${repo}" --base "${branch}" --head "${pr_branch}" \
        --title "website: ansible-oracle ${source_version}" \
        --body "Generated from ansible-oracle commit ${source_commit} by \`tools/release/build_website.sh\`."
      ;;
  esac
}

while getopts "ad:fm:r:" opt ; do
  case "${opt}" in
    a) a11y=true ;;
    d) clone_dir="${OPTARG}" ;;
    f) force=true ;;
    m) mode="${OPTARG}" ;;
    r) repo="${OPTARG}" ;;
    *) usage ;;
  esac
done
shift $((OPTIND - 1))
[ $# -eq 0 ] || usage

case "${mode}" in
  local|push|pr) ;;
  *) usage ;;
esac

source_commit=$(git rev-parse HEAD)
source_version=$(git describe --tags --always --dirty)
pr_branch="website/$(git rev-parse --short HEAD)"

check_tools
check_sources
build_website
check_legal_notice
prepare_clone
sync_docs
commit_docs
# also commits of an earlier run in mode local, which were not pushed
unpushed=$(git -C "${clone_dir}" rev-list --count "origin/${branch}..HEAD")
if [ "${unpushed}" -eq 0 ] ; then
  echo "The website in ${repo} is up to date, nothing to publish"
else
  publish
fi

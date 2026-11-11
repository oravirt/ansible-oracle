# shellcheck shell=bash
# Load extensions/.env (KEY=VALUE, shell syntax) into the environment.
#
# Usage: . tools/load_env.sh   (from extensions/, or with ENV_FILE=<file>)
#
# Variables already set in the environment have precedence over the file.
# Empty lines and comments (#) are ignored, values may be quoted like in a shell.
_load_env_file="${ENV_FILE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env}"
if [ -f "${_load_env_file}" ]; then
  while IFS= read -r _load_env_line || [ -n "${_load_env_line}" ]; do
    case "${_load_env_line}" in
      '' | '#'*) continue ;;
    esac
    _load_env_key="${_load_env_line%%=*}"
    _load_env_key="${_load_env_key#export }"
    # skip invalid lines and variables already set in the environment
    [[ "${_load_env_key}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
    [ -n "${!_load_env_key+x}" ] && continue
    eval "export ${_load_env_line#export }"
  done < "${_load_env_file}"
fi
unset _load_env_file _load_env_line _load_env_key

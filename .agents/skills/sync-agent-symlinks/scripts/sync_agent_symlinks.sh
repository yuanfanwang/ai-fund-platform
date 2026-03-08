#!/usr/bin/env bash
set -euo pipefail

force=0
if [[ "${1:-}" == "--force" ]]; then
  force=1
elif [[ "${1:-}" != "" ]]; then
  echo "Usage: $0 [--force]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

SOURCE_ROOT="${ROOT_DIR}/.agents"
for src in commands rules skills; do
  if [[ ! -d "${SOURCE_ROOT}/${src}" ]]; then
    echo "Missing source directory: ${SOURCE_ROOT}/${src}" >&2
    exit 1
  fi
done

if [[ ! -f "${ROOT_DIR}/AGENTS.md" ]]; then
  echo "Missing source file: ${ROOT_DIR}/AGENTS.md" >&2
  exit 1
fi

ensure_symlink() {
  local dest="$1"
  local rel_src="$2"

  if [[ -L "${dest}" ]]; then
    local current
    current="$(readlink "${dest}")"
    if [[ "${current}" == "${rel_src}" ]]; then
      echo "OK: ${dest} already points to ${rel_src}"
      return
    fi
    rm -f "${dest}"
  elif [[ -e "${dest}" ]]; then
    if [[ "${force}" -eq 1 ]]; then
      rm -rf "${dest}"
    else
      echo "Refusing to replace non-symlink path: ${dest}" >&2
      echo "Re-run with --force to replace it." >&2
      exit 1
    fi
  fi

  ln -s "${rel_src}" "${dest}"
  echo "Linked: ${dest} -> ${rel_src}"
}

for target in .claude .cursor .codex; do
  mkdir -p "${ROOT_DIR}/${target}"
  for name in commands rules skills; do
    dest="${ROOT_DIR}/${target}/${name}"
    rel_src="../.agents/${name}"
    ensure_symlink "${dest}" "${rel_src}"
  done
done

ensure_symlink "${ROOT_DIR}/CLAUDE.md" "AGENTS.md"

echo "Symlink sync completed."

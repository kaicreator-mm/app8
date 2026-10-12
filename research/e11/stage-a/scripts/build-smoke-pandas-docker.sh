#!/usr/bin/env bash
# SE11 Stage A — pandas real-container build + non-evaluative smoke.
# Build: exact pinned source -> pip wheel in python:3.12-bookworm -> wheel SHA-256 -> install.
# Smoke: import built package, print package/runtime identity only. NO SE11 capability claims.
# usage: build-smoke-pandas-docker.sh [evidence-root]
set -euo pipefail
root="${1:-$(cd "$(dirname "$0")" && pwd)}"
asset_root="$root/pandas"
log="$asset_root/logs"
img="python:3.12-bookworm"

echo "== container identity ==" | tee "$log/container-identity.log"
docker image inspect "$img" --format 'image={{.RepoTags}} digest={{index .RepoDigests 0}}' | tee -a "$log/container-identity.log"

mkdir -p "$asset_root/scripts"
cp "$root/scripts/smoke-pandas.py" "$asset_root/scripts/smoke-pandas.py"

docker run --rm \
  -v "$(cygpath -w "$asset_root"):/work" \
  -e PIP_DISABLE_PIP_VERSION_CHECK=1 \
  "$img" bash -euo pipefail -c '
    cat /etc/os-release | head -5 > /work/logs/container-os.txt
    uname -a >> /work/logs/container-os.txt
    python --version >> /work/logs/container-os.txt 2>&1
    gcc --version | head -1 >> /work/logs/container-os.txt
    g++ --version | head -1 >> /work/logs/container-os.txt

    echo "== build wheel from pinned source ==" > /work/logs/build.log
    cp -a /work/src /build
    cd /build
    git rev-parse HEAD >> /work/logs/build.log 2>/dev/null || true
    python -m pip wheel /build --no-deps -w /work/out >> /work/logs/build.log 2>&1

    echo "== wheel identity ==" >> /work/logs/build.log
    sha256sum /work/out/*.whl >> /work/logs/build.log

    echo "== install built wheel ==" >> /work/logs/build.log
    python -m pip install /work/out/pandas-*.whl >> /work/logs/build.log 2>&1
    pip show pandas > /work/logs/pip-show.txt 2>&1 || true

    echo "== smoke: import identity only ==" > /work/logs/smoke.log
    mkdir -p /neutralcwd && cd /neutralcwd
    set +e
    python /work/scripts/smoke-pandas.py > /work/logs/smoke.stdout 2> /work/logs/smoke.stderr
    rc=$?
    set -e
    echo "exit=$rc" >> /work/logs/smoke.log
    exit $rc
  '
rc=$?
echo "SMOKE_EXIT=$rc" | tee -a "$log/smoke.log"
if [ "$rc" -eq 0 ]; then
  echo "SMOKE_OK (infrastructure check only — NOT SE11 capability evidence)" | tee -a "$log/smoke.log"
else
  echo "SMOKE_FAILED" | tee -a "$log/smoke.log"
fi
exit "$rc"

#!/usr/bin/env bash
# SE11 Stage A — FFmpeg real-container build + non-evaluative smoke.
# Build: exact pinned source -> configure/make in ubuntu:24.04 -> binary SHA-256.
# Smoke: -version / -h executable invocation only. NO SE11 capability claims.
# usage: build-smoke-ffmpeg-docker.sh [evidence-root]
set -euo pipefail
root="${1:-$(cd "$(dirname "$0")" && pwd)}"
asset_root="$root/ffmpeg"
log="$asset_root/logs"
img="ubuntu:24.04"
jobs="$(nproc)"

echo "== container identity ==" | tee "$log/container-identity.log"
docker image inspect "$img" --format 'image={{.RepoTags}} digest={{index .RepoDigests 0}}' | tee -a "$log/container-identity.log"

docker run --rm \
  -v "$(cygpath -w "$asset_root"):/work" \
  "$img" bash -euo pipefail -c "
    cat /etc/os-release | head -5 > /work/logs/container-os.txt
    uname -a >> /work/logs/container-os.txt

    echo '== apt install toolchain ==' > /work/logs/apt.log
    export DEBIAN_FRONTEND=noninteractive
    apt-get update >> /work/logs/apt.log 2>&1
    apt-get install -y --no-install-recommends build-essential nasm yasm pkg-config >> /work/logs/apt.log 2>&1

    { gcc --version | head -1;
      make --version | head -1;
      nasm -v || true; } >> /work/logs/container-os.txt

    echo '== configure (pinned source) ==' > /work/logs/configure.log
    cp -a /work/src /build
    cd /build
    ./configure --disable-doc --disable-ffplay >> /work/logs/configure.log 2>&1

    echo '== make -j${jobs} ==' > /work/logs/make.log
    make -j${jobs} >> /work/logs/make.log 2>&1

    mkdir -p /work/out
    cp -a ffmpeg ffprobe /work/out/

    echo '== binary identity ==' > /work/logs/artifacts.log
    ls -l /work/out >> /work/logs/artifacts.log
    sha256sum /work/out/ffmpeg /work/out/ffprobe >> /work/logs/artifacts.log
    ./ffmpeg -buildconf > /work/logs/buildconf.txt 2>&1 || true

    echo '== smoke: version/help invocation only ==' > /work/logs/smoke.log
    set +e
    ./ffmpeg -version > /work/logs/smoke-version.stdout 2> /work/logs/smoke-version.stderr
    rc1=\$?
    ./ffmpeg -hide_banner -h > /work/logs/smoke-help.stdout 2> /work/logs/smoke-help.stderr
    rc2=\$?
    set -e
    echo 'exit_version='\$rc1 >> /work/logs/smoke.log
    echo 'exit_help='\$rc2 >> /work/logs/smoke.log
    [ \$rc1 -eq 0 ] && [ \$rc2 -eq 0 ]
  "
rc=$?
echo "SMOKE_EXIT=$rc" | tee -a "$log/smoke.log"
if [ "$rc" -eq 0 ]; then
  echo "SMOKE_OK (infrastructure check only — NOT SE11 capability evidence)" | tee -a "$log/smoke.log"
else
  echo "SMOKE_FAILED" | tee -a "$log/smoke.log"
fi
exit "$rc"

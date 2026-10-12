#!/usr/bin/env bash
# SE11 Stage A — LibreOffice/core@016fd5d bounded real-build attempt.
# Goal: honest BLOCKED_ENVIRONMENT evidence if the exact pinned revision cannot be
# built/run on this host within budget. NO source substitution, NO distro binary fallback.
# usage: attempt-libreoffice-docker.sh [evidence-root]
set -uo pipefail
root="${1:-$(cd "$(dirname "$0")" && pwd)}"
asset_root="$root/libreoffice"
log="$asset_root/logs"
img="ubuntu:24.04"

{
  echo "== host-native MSVC path check =="
  where cl 2>&1 || echo "where-cl: not found (no MSVC on Windows host)"
  where msbuild 2>&1 || echo "where-msbuild: not found"
} > "$log/host-native-toolchain.txt" 2>&1

echo "== container identity ==" | tee "$log/container-identity.log"
docker image inspect "$img" --format 'image={{.RepoTags}} digest={{index .RepoDigests 0}}' | tee -a "$log/container-identity.log"

docker run --rm \
  -v "$(cygpath -w "$asset_root"):/work" \
  "$img" bash -uo pipefail -c '
    cat /etc/os-release | head -5 > /work/logs/container-os.txt
    uname -a >> /work/logs/container-os.txt
    df -h / /work >> /work/logs/container-os.txt

    echo "== apt first-wave deps (LibreOffice documented Linux build set, bounded) ==" > /work/logs/apt.log
    export DEBIAN_FRONTEND=noninteractive
    apt-get update >> /work/logs/apt.log 2>&1
    apt-get install -y --no-install-recommends \
      build-essential g++ gcc autoconf automake bison flex libtool pkg-config gperf \
      git zip unzip ccache python3 python3-dev python3-setuptools \
      libxml2-dev libxslt1-dev libssl-dev libcurl4-openssl-dev libcairo2-dev \
      libglib2.0-dev libboost-locale-dev libboost-system-dev libboost-filesystem-dev \
      libcppunit-dev libhunspell-dev libharfbuzz-dev libicu-dev libjpeg-dev libpng-dev \
      librsvg2-dev libsqlite3-dev libnss3-dev libkrb5-dev libxmlsec1-dev libpoppler-dev \
      libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libx11-dev libxext-dev \
      libxrender-dev libxrandr-dev libxi-dev libxcb1-dev libxt-dev 2>> /work/logs/apt.log \
      || echo "APT_FIRST_WAVE_PARTIAL (some packages unknown — see apt.log)" >> /work/logs/apt.log

    cp -a /work/src /build
    cd /build

    echo "== round 0: ./autogen.sh (default, no feature flags) ==" > /work/logs/autogen.log
    timeout 1500 ./autogen.sh >> /work/logs/autogen.log 2>&1
    rc=$?
    echo "autogen_exit=$rc" >> /work/logs/autogen.log
    if [ $rc -ne 0 ]; then
      echo "== final exact error tail ==" > /work/logs/attempt-final.txt
      tail -40 /work/logs/autogen.log >> /work/logs/attempt-final.txt
      exit 3
    fi

    echo "== round 1: ./configure bounded 1500s ==" > /work/logs/configure.log
    timeout 1500 ./configure >> /work/logs/configure.log 2>&1
    rc=$?
    echo "configure_exit=$rc (124=timeout budget exhausted)" >> /work/logs/configure.log
    echo "== final exact state tail ==" > /work/logs/attempt-final.txt
    tail -60 /work/logs/configure.log >> /work/logs/attempt-final.txt
    exit $rc
  '
rc=$?
case "$rc" in
  0) verdict="CONFIGURE_COMPLETED_WITHIN_BUDGET — make NOT run: multi-hour/ tens-of-GB budget exceeds Stage-A session budget (explicit finding, no substitution)" ;;
  124) verdict="BUDGET_EXCEEDED — configure still running when bounded timeout hit" ;;
  3) verdict="AUTOGEN_FAILED — exact error captured in logs/attempt-final.txt" ;;
  *) verdict="CONFIGURE_FAILED — exact error captured in logs/attempt-final.txt" ;;
esac
echo "LIBREOFFICE_ATTEMPT_EXIT=$rc" | tee -a "$log/attempt.log"
echo "VERDICT: $verdict" | tee -a "$log/attempt.log"
echo "BLOCKED_ENVIRONMENT_CANDIDATE (if rc!=0): report verbatim in Stage-A manifest" | tee -a "$log/attempt.log"
exit "$rc"

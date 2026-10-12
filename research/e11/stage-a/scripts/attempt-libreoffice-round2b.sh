#!/usr/bin/env bash
# SE11 Stage A — LibreOffice/core@016fd5d round 2, detached re-invocation.
# The attached round-2 docker run was killed by the host ~6.5 min in
# (container destroy mid-apt-download, docker CLI exit 137; evidence:
# logs/libreoffice/apt-r2-attached-killed.log, driver-round2-attached.log).
# Re-invocation runs the SAME payload verbatim, detached, so a Windows-side
# CLI kill cannot orphan the attempt; exit code observed via `docker wait`.
# NO source substitution; bounded autogen (timeout 1500) unchanged.
set -uo pipefail
root="${1:-$(cd "$(dirname "$0")" && pwd)}"
asset_root="$root/libreoffice"
log="$asset_root/logs"
img="ubuntu:24.04"
name="se11-lo-r2b"

docker rm -f "$name" >/dev/null 2>&1 || true
cid=$(docker run -d --name "$name" \
  -v "$(cygpath -w "$asset_root"):/work" \
  "$img" bash -uo pipefail -c '
    cat /etc/os-release | head -5 > /work/logs/container-os.txt
    uname -a >> /work/logs/container-os.txt
    df -h / /work >> /work/logs/container-os.txt

    echo "== apt round2: first-wave + libcups2-dev/GTK3/X11 (no JDK) ==" > /work/logs/apt.log
    export DEBIAN_FRONTEND=noninteractive
    apt-get update >> /work/logs/apt.log 2>&1
    PKGS="build-essential g++ gcc autoconf automake bison flex libtool pkg-config gperf \
      git zip unzip ccache python3 python3-dev python3-setuptools \
      libxml2-dev libxslt1-dev libssl-dev libcurl4-openssl-dev libcairo2-dev \
      libglib2.0-dev libboost-locale-dev libboost-system-dev libboost-filesystem-dev \
      libcppunit-dev libhunspell-dev libharfbuzz-dev libicu-dev libjpeg-dev libpng-dev \
      librsvg2-dev libsqlite3-dev libnss3-dev libkrb5-dev libxmlsec1-dev libpoppler-dev \
      libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libx11-dev libxext-dev \
      libxrender-dev libxrandr-dev libxi-dev libxcb1-dev libxt-dev \
      libcups2-dev libgtk-3-dev libpango1.0-dev libxkbcommon-x11-dev \
      libwayland-dev libsndfile1-dev libbluetooth-dev"
    apt-get install -y --no-install-recommends $PKGS >> /work/logs/apt.log 2>&1 \
      || { echo "== apt retry after failure ==" >> /work/logs/apt.log
           apt-get update >> /work/logs/apt.log 2>&1
           apt-get install -y --no-install-recommends $PKGS >> /work/logs/apt.log 2>&1 \
             || echo "APT_ROUND2_FAILED — see apt.log" >> /work/logs/apt.log; }

    cp -a /work/src /build
    cd /build

    echo "== round 2: ./autogen.sh (default features) ==" > /work/logs/autogen.log
    timeout 1500 ./autogen.sh >> /work/logs/autogen.log 2>&1
    rc=$?
    echo "autogen_exit=$rc" >> /work/logs/autogen.log
    echo "== final exact error tail ==" > /work/logs/attempt-final.txt
    tail -40 /work/logs/autogen.log >> /work/logs/attempt-final.txt
    exit $rc
  ')
echo "container=$cid" | tee -a "$log/attempt.log"
rc=$(docker wait "$name")
echo "LIBREOFFICE_ROUND2B_EXIT=$rc" | tee -a "$log/attempt.log"
case "$rc" in
  0) verdict="AUTOGEN_COMPLETED (configure passed) — make NOT run: multi-hour, tens-of-GB build exceeds Stage-A session budget (explicit finding, no substitution); binary binding NOT established" ;;
  124) verdict="BUDGET_EXCEEDED — autogen/configure still running at bounded timeout" ;;
  *) verdict="AUTOGEN_FAILED_AGAIN — exact next dependency error captured" ;;
esac
echo "VERDICT_R2B: $verdict" | tee -a "$log/attempt.log"
docker logs "$name" > "$log/driver-round2b.log" 2>&1 || true
docker rm -f "$name" >/dev/null 2>&1 || true
exit "$rc"

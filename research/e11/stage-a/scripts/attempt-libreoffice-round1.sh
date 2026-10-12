#!/usr/bin/env bash
# SE11 Stage A — LibreOffice/core@016fd5d bounded attempt, round 1.
# Round 0 failed at: configure: error: Could not find CUPS (libcups2-dev).
# Round 1 adds libcups2-dev plus the next obvious dependency wave (GTK3, JDK,
# X11 input libs) and retries default-feature ./autogen.sh, still bounded.
# Goal: show the dependency chain honestly; NO source substitution, NO feature-reduced build.
set -uo pipefail
root="${1:-$(cd "$(dirname "$0")" && pwd)}"
asset_root="$root/libreoffice"
log="$asset_root/logs"
img="ubuntu:24.04"

docker run --rm \
  -v "$(cygpath -w "$asset_root"):/work" \
  "$img" bash -uo pipefail -c '
    cat /etc/os-release | head -5 > /work/logs/container-os.txt
    uname -a >> /work/logs/container-os.txt
    df -h / /work >> /work/logs/container-os.txt

    echo "== apt round0 first-wave + round1 additions (libcups2-dev, GTK3, JDK, X11 input) ==" > /work/logs/apt.log
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
      libxrender-dev libxrandr-dev libxi-dev libxcb1-dev libxt-dev \
      libcups2-dev libgtk-3-dev default-jdk-headless libpango1.0-dev libxkbcommon-x11-dev \
      libwayland-dev libsndfile1-dev libbluetooth-dev 2>> /work/logs/apt.log \
      || echo "APT_ROUND1_PARTIAL (unknown package names skipped — see apt.log tail)" >> /work/logs/apt.log

    cp -a /work/src /build
    cd /build

    echo "== round 1: ./autogen.sh (default features, extended deps) ==" > /work/logs/autogen.log
    timeout 1500 ./autogen.sh >> /work/logs/autogen.log 2>&1
    rc=$?
    echo "autogen_exit=$rc" >> /work/logs/autogen.log
    echo "== final exact error tail ==" > /work/logs/attempt-final.txt
    tail -40 /work/logs/autogen.log >> /work/logs/attempt-final.txt
    exit $rc
  '
rc=$?
case "$rc" in
  0) verdict="AUTOGEN_COMPLETED (configure passed with extended deps) — make NOT run: multi-hour budget exceeds Stage-A session budget (explicit finding, no substitution)" ;;
  124) verdict="BUDGET_EXCEEDED — autogen/configure still running when bounded timeout hit" ;;
  *) verdict="AUTOGEN_FAILED_AGAIN — exact next dependency error captured" ;;
esac
echo "LIBREOFFICE_ROUND1_EXIT=$rc" | tee -a "$log/attempt.log"
echo "VERDICT_R1: $verdict" | tee -a "$log/attempt.log"
exit "$rc"

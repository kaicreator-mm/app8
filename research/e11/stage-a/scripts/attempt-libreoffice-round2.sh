#!/usr/bin/env bash
# SE11 Stage A — LibreOffice/core@016fd5d bounded attempt, round 2 (final).
# Round 0 exact error: configure: error: Could not find CUPS (libcups2-dev).
# Round 1 invalid: sole failed apt archive was openjdk-21-jdk-headless (connection
# failed), which aborted the whole transaction — CUPS was never installed.
# Round 2: same wave minus default-jdk-headless (LO configure treats missing JDK
# as feature degradation, not fatal), plus one apt retry. NO source substitution.
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
  '
rc=$?
case "$rc" in
  0) verdict="AUTOGEN_COMPLETED (configure passed) — make NOT run: multi-hour, tens-of-GB build exceeds Stage-A session budget (explicit finding, no substitution); binary binding NOT established" ;;
  124) verdict="BUDGET_EXCEEDED — autogen/configure still running at bounded timeout" ;;
  *) verdict="AUTOGEN_FAILED_AGAIN — exact next dependency error captured" ;;
esac
echo "LIBREOFFICE_ROUND2_EXIT=$rc" | tee -a "$log/attempt.log"
echo "VERDICT_R2: $verdict" | tee -a "$log/attempt.log"
exit "$rc"

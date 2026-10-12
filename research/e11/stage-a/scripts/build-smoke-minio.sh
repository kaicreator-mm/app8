#!/usr/bin/env bash
# SE11 Stage A — MinIO real-host build + non-evaluative smoke (Windows native, Git Bash).
# Build: exact pinned source -> go build (vendored deps) -> binary SHA-256 + go vcs stamping.
# Smoke: version/help + server startup readiness on loopback. NO SE11 capability claims.
# usage: build-smoke-minio.sh [evidence-root]
set -euo pipefail
root="${1:-$(cd "$(dirname "$0")" && pwd)}"
asset_root="$root/minio"
src="$asset_root/src"
out="$asset_root/out"
log="$asset_root/logs"
mkdir -p "$out"

echo "== toolchain identity ==" | tee "$log/build.log"
go version | tee -a "$log/build.log"
go env GOOS GOARCH GOAMD64 GOPROXY | tee -a "$log/build.log"

echo "== build (from pinned source) ==" | tee -a "$log/build.log"
cd "$src"
git status --porcelain > /tmp/minio_dirty_check.txt
if [ -s /tmp/minio_dirty_check.txt ]; then
  echo "FATAL: source tree dirty, refusing build (frozen identity)" >&2
  exit 2
fi
go build -trimpath -o "$out/minio.exe" . >> "$log/build.log" 2>&1

echo "== binary identity ==" | tee -a "$log/build.log"
ls -l "$out/minio.exe" | tee -a "$log/build.log"
sha256sum "$out/minio.exe" | tee -a "$log/build.log"
go version -m "$out/minio.exe" > "$log/go-version-m.txt" 2>&1 || true
grep -E "vcs\.revision|vcs\.time|vcs\.modified|path|mod" "$log/go-version-m.txt" | head -8 | tee -a "$log/build.log"

echo "== smoke 1: --version ==" | tee "$log/smoke.log"
set +e
"$out/minio.exe" --version > "$log/smoke-version.stdout" 2> "$log/smoke-version.stderr"
rc1=$?
set -e
echo "exit=$rc1" | tee -a "$log/smoke.log"
cat "$log/smoke-version.stdout" | tee -a "$log/smoke.log"
cat "$log/smoke-version.stderr" | tee -a "$log/smoke.log"

echo "== smoke 2: server startup readiness (loopback only) ==" | tee -a "$log/smoke.log"
data_dir="$asset_root/smoke-data"
rm -rf "$data_dir"
mkdir -p "$data_dir"
MINIO_ROOT_USER=minioadmin MINIO_ROOT_PASSWORD=minioadmin \
  "$out/minio.exe" server "$data_dir" \
  --address "127.0.0.1:19500" --console-address "127.0.0.1:19501" \
  > "$log/smoke-server.stdout" 2> "$log/smoke-server.stderr" &
srv_pid=$!
echo "server_pid=$srv_pid" | tee -a "$log/smoke.log"

health=""
for i in $(seq 1 30); do
  sleep 1
  code="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:19500/minio/health/live || true)"
  if [ "$code" = "200" ]; then health="200"; break; fi
done
echo "health_live_http=$code polls=${i}s" | tee -a "$log/smoke.log"
curl -s http://127.0.0.1:19500/minio/health/cluster 2>/dev/null > "$log/smoke-health-cluster.body" || true

kill "$srv_pid" 2>/dev/null || taskkill //F //PID "$(cygwinpid2win 2>/dev/null || echo 0)" 2>/dev/null || true
sleep 2
if kill -0 "$srv_pid" 2>/dev/null; then kill -9 "$srv_pid" 2>/dev/null || true; fi
echo "server_stopped" | tee -a "$log/smoke.log"
echo "== smoke data dir cleanup ==" | tee -a "$log/smoke.log"
rm -rf "$data_dir" && echo "cleanup_ok: $data_dir removed" | tee -a "$log/smoke.log"

if [ "$rc1" -ne 0 ] || [ "$code" != "200" ]; then
  echo "SMOKE_FAILED" | tee -a "$log/smoke.log"
  exit 1
fi
echo "SMOKE_OK (infrastructure check only — NOT SE11 capability evidence)" | tee -a "$log/smoke.log"

#!/usr/bin/env bash
# Derives the leak-band table from php-src history. Two gates must both be
# open for the CVE-2026-109618/109619 disclosure stage (the leak):
#
#   Gate 1 (generation): a startup-time bailout skips module shutdown while
#     the heap is freed -> the session ID pointer dangles. Present since at
#     least php-7.4.0 on every version (checked below by source probe).
#   Gate 2 (emission): the "cookie owed" flag survives a failed send, so the
#     next request can emit stale bytes. This arrived with commit
#     a85666c17b ("Fix GH-17541 ... during ID reset"), first released in
#     8.3.17. The 2026-10-21 security floors (8.2.35/8.3.36/8.4.27/8.5.12)
#     close the chain at the source regardless.
#
# Output: per-tag gate states and the resulting band table.
set -euo pipefail
cd "$(mktemp -d)"
echo "[*] blobless clone of php-src (network required)..."
git clone -q --filter=blob:none --no-checkout https://github.com/php/php-src php-src
cd php-src
git fetch -q --tags origin   # blobless clones can miss tag objects without this

EMISSION=a85666c17b4cfd68a8f782bbab606ee97aeb9b52   # gate 2
# per-branch 2026-10-21 fix commits (close the chain at the source)
FIXES="01a40e89fb 3c832b523e 506e87fa7d 31c0ea7d7f"

TAGS="php-7.4.0 php-7.4.33 php-8.0.0 php-8.0.30 php-8.1.0 php-8.1.34 \
php-8.2.0 php-8.2.34 php-8.2.35 php-8.3.0 php-8.3.16 php-8.3.17 \
php-8.3.35 php-8.3.36 php-8.4.0 php-8.4.3 php-8.4.4 php-8.4.26 \
php-8.4.27 php-8.5.0 php-8.5.11 php-8.5.12"

printf "%-14s %-9s %-9s %-8s %s\n" TAG gate1 gate2 fixed LEAK
for t in $TAGS; do
  gate1="?"
  # gate 1 source probe: the startup-shutdown guard exists in main/main.c.
  # blobless clones fetch this blob lazily on first ask; retry until the
  # read lands, otherwise the probe flakes on cold caches.
  mc="$(mktemp)"
  for attempt in 1 2 3 4 5; do
    git cat-file blob "$t:main/main.c" >"$mc" 2>/dev/null || true
    [ -s "$mc" ] && break
    sleep 1
  done
  if [ -s "$mc" ]; then
    if grep -q "PG(modules_activated)" "$mc"; then gate1="open"; else gate1="closed"; fi
  fi
  rm -f "$mc"
  git merge-base --is-ancestor "$EMISSION" "$t" && gate2=open || gate2=closed
  fixed=no
  for f in $FIXES; do
    git merge-base --is-ancestor "$f" "$t" && fixed=yes || true
  done
  leak=DEAD
  [ "$gate1" = open ] && [ "$gate2" = open ] && [ "$fixed" = no ] && leak=ALIVE
  printf "%-14s %-9s %-9s %-8s %s\n" "$t" "$gate1" "$gate2" "$fixed" "$leak"
done

cat <<'NOTES'

Reading the table: the leak is ALIVE only where gate1=open AND gate2=open
AND the tag predates the 2026-10-21 fix floors. That yields the bands:
  ALIVE: 8.3.17-8.3.35, 8.4.4-8.4.26, 8.5.0-8.5.11
  DEAD:  everything older (gate 2 closed), plus all fixed floors
Everything below 8.3.17 can be corrupted and crashed, but never
blind-addressed: the disclosure stage cannot emit.
NOTES

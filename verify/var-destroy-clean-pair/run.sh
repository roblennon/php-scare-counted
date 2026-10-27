#!/usr/bin/env bash
# Builds the clean pair (same tag +/- fix) and runs the reentrancy verifier
# in each. Expect: vuln => VULNERABLE (exit 2), fixed => FIXED (exit 0).
set -e
cd "$(dirname "$0")"
echo "== building vulnerable (official php:8.4.26-cli tag build)"
docker build -q -t psc/vuln -f Dockerfile.vuln . >/dev/null
echo "== building fixed (php-8.4.26 source + GH-24452) — this one compiles PHP, ~10-20 min"
docker build -q -t psc/fixed -f Dockerfile.fixed . >/dev/null
echo "== vulnerable side:"; docker run --rm psc/vuln php /repro.php || echo "  (exit $?)"
echo "== fixed side:";      docker run --rm psc/fixed php /repro.php || echo "  (exit $?)"

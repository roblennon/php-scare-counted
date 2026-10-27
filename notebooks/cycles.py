#!/usr/bin/env python3
"""Blind-fire cycle arithmetic for a memory-corruption chain with no leak.

Model: two unknowns must be guessed per attempt.
  - library base: PIE-ASLR over a ~30MB library at 2MB alignment granularity
  - heap slot:    a small set of candidate addresses (heap layout is fairly
                  deterministic per request-sequence, so this dimension is
                  small but nonzero)

Each attempt costs ~1 minute (large upload) and produces one of three
outcomes (see MISS_CLASSES below). Only the lattice miss is quiet; every
wrong-heap guess kills a worker (segfault log line); a right-heap,
wrong-library guess is an uncontrolled call, not a clean miss.
"""
import sys

# x86-64 PIE mmap entropy against 2MB huge-page-ish alignment granularity
LIB_ALIGNMENTS = 1 << 18          # ~262k raw; commonly quoted 28-bit full entropy
LIB_ALIGNMENTS_CONSERVATIVE = 1 << 16   # ~65k at coarser observed granularity
HEAP_CANDIDATES = 8               # residue lattice from request-shape variance
SECONDS_PER_ATTEMPT = 60          # paced multi-MB upload

MISS_CLASSES = [
    ("lattice miss", "fake structure lands unreferenced; clean 200. Only quiet outcome."),
    ("wrong heap",   "worker SIGSEGV; one error-log line per attempt."),
    ("wrong library (right heap)", "corrupted structure calls a random address with attacker data. Not a miss - an uncontrolled call."),
]

def cycles(alignments, heap):
    return alignments * heap

def human(n, seconds):
    days = n * seconds / 86400
    return f"{n:,} attempts ~= {days:,.0f} days of continuous hammering (per host)"

if __name__ == "__main__":
    print("Assumptions:")
    print(f"  library alignments: {LIB_ALIGNMENTS_CONSERVATIVE:,} (coarse-granularity) to {LIB_ALIGNMENTS:,} (full mmap entropy)")
    print(f"  heap candidates:    {HEAP_CANDIDATES} (residue lattice; heap layout is largely deterministic per request-sequence)")
    print(f"  pacing:             {SECONDS_PER_ATTEMPT}s per attempt (multi-MB upload, paced)")
    print()
    print("Miss classes:")
    for name, desc in MISS_CLASSES:
        print(f"  - {name}: {desc}")
    print()
    for label, aligns in [("coarse granularity", LIB_ALIGNMENTS_CONSERVATIVE),
                          ("full mmap entropy ", LIB_ALIGNMENTS)]:
        n = cycles(aligns, HEAP_CANDIDATES)
        print(f"[{label}] full sweep: {human(n, SECONDS_PER_ATTEMPT)}")
        print(f"[{label}] expected to first hit (~half the space): {human(n // 2, SECONDS_PER_ATTEMPT)}")
    print()
    print("Every one of those attempts is loud: wrong-heap guesses leave a segfault")
    print("log line per attempt; there is no quiet sweep. A leak collapses both")
    print("unknowns into one calibrated request, which is the entire point.")

# Miss-class arithmetic — verified output of cycles.py

```
Assumptions:
  library alignments: 65,536 (coarse-granularity) to 262,144 (full mmap entropy)
  heap candidates:    8 (residue lattice; heap layout is largely deterministic per request-sequence)
  pacing:             60s per attempt (multi-MB upload, paced)

Miss classes:
  - lattice miss: fake structure lands unreferenced; clean 200. Only quiet outcome.
  - wrong heap: worker SIGSEGV; one error-log line per attempt.
  - wrong library (right heap): corrupted structure calls a random address with attacker data. Not a miss - an uncontrolled call.

[coarse granularity] full sweep: 524,288 attempts ~= 364 days of continuous hammering (per host)
[coarse granularity] expected to first hit (~half the space): 262,144 attempts ~= 182 days of continuous hammering (per host)
[full mmap entropy ] full sweep: 2,097,152 attempts ~= 1,456 days of continuous hammering (per host)
[full mmap entropy ] expected to first hit (~half the space): 1,048,576 attempts ~= 728 days of continuous hammering (per host)

Every one of those attempts is loud: wrong-heap guesses leave a segfault
log line per attempt; there is no quiet sweep. A leak collapses both
unknowns into one calibrated request, which is the entire point.
```

# Diagnose Log

## Bug Summary

Describe the failure in one sentence.

## Command That Fails

```bash
PASTE COMMAND HERE
```

## Error / Traceback

```text
PASTE ERROR HERE
```

## Phase 1 — Feedback Loop

What is the fastest command that reproduces the bug?

```bash
python -m pytest
```

or

```bash
python scripts/run_daily_pipeline.py
```

## Phase 2 — Reproduce

- [ ] I can reproduce the failure
- [ ] The failure matches the original symptom
- [ ] The failure is deterministic enough to debug

## Phase 3 — Ranked Hypotheses

1. Hypothesis:
   - If this is true, then:

2. Hypothesis:
   - If this is true, then:

3. Hypothesis:
   - If this is true, then:

## Phase 4 — Instrument

What small checks, print statements, logs, or targeted commands will distinguish the hypotheses?

Use temporary debug prefix:

```text
[DEBUG-cnr]
```

## Phase 5 — Fix and Regression Test

- [ ] Add or update a test that fails before the fix
- [ ] Apply the smallest fix
- [ ] Run the failing test again
- [ ] Run the full relevant test suite

## Verification

```bash
python -m pytest
```

Additional commands:

```bash
python scripts/...
```

## Root Cause

Explain the confirmed cause.

## Final Fix

Explain what changed.

## Prevention

What would prevent this class of bug next time?

## Commit Message

```text
fix: ...
```

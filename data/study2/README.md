# Study 2 artifacts

Real smoke, pilot, and main artifacts will be stored in separate phase
directories only after their respective approvals. No real calls or actual main
manifest have been produced during the build phases.

Each approved run uses:

```text
manifest.jsonl             # Self-contained assignments, exact source text/schemas, hashes
turns/<buyer>__<seller>.jsonl
episodes.jsonl             # Natural terminal episodes, recomputed from attempts
probes.jsonl               # Unscored forced-position smoke probes only
run_summary.json           # Replaceable mechanical invocation summary
```

Every call is journaled before dispatch and appended/fsynced on completion.
Pending sidecars survive interruption; advisory `.lock` files are local/ignored.
Resume verifies all existing bindings and histories, records uncertain calls as
interrupted, and continues without replacing exclusions or repeating final units.
Damaged tails are preserved for explicit recovery rather than silently removed.

Smoke plans have four natural episodes and sixteen separately marked probes.
Only four natural terminal episode records can result from that plan; probes
have no surplus scores and never enter analysis. Probe attempts share the
approved cap of 32 across retries and resumes. Reports retain the exact fixed
transcripts used. Pilot plans have 80 episodes; pilot outcome reporting remains
pooled over conditions. The actual 960-episode main plan is generated only in
the later lock phase, using its separate seed.

Build/test data are synthetic and belong in a temporary directory or a separate
synthetic directory, outside real smoke/pilot/main folders. Current CLI execution
accepts mocks only and rejects real-study output destinations. See
`docs/study2_phase3_report.md` for safe demonstration/replay commands.

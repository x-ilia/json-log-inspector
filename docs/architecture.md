# Architecture

`python -m log_inspector` delegates to `core.main`. Argument parsing and filesystem
access live at the boundary; the exported core functions own the behavior.
Results are plain Python data structures that can be serialized as JSON.

## Design decisions

- Standard library only: easy to run in a fresh agent environment.
- Explicit validation: bad input should fail predictably rather than be coerced.
- Stable ordering: examples and tests stay reproducible across machines.
- Read-only processing: input files are never modified.

## Extension strategy

Add a focused core function, test it using synthetic fixtures, then expose it via
the CLI. Keep the documented default behavior compatible where possible.

## Scope

Each nonblank line must be a JSON object. `level` is a string (default UNKNOWN);
`message` groups ERROR/CRITICAL events. Optional `duration_ms` must be a finite,
nonnegative number; booleans are rejected. Percentiles use nearest rank, without
interpolation. Invalid records are reported by line number and skipped; invalid
durations do not discard otherwise valid records. Latencies are kept in memory
for exact percentiles. Top errors sort by count, then message, limited to five.
Exit codes: 0 clean input, 1 malformed records/durations, 2 I/O or encoding error.

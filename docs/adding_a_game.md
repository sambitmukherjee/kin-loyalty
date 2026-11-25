# Adding a game — implementation outline

The current phase provides layout and draft configuration. No game renderer,
response schema, or runner has been implemented yet.

1. Define the new decision and its outcome fields in a separate study config.
2. Write plain-text templates and a response schema, preserving neutral card and
   identity rendering. Keep person names out of JSON field names.
3. Add local validation and a deterministic manifest for the new design.
4. Reuse the clients, card renderer, log format, and runner patterns, keeping
   single-decision assumptions out of the shared components.
5. Add mock-client tests for valid/invalid/truncated replies and resume behavior.
6. Define analyses before observing main outcomes, and obtain any required design,
   prompt, phase, and spending approvals.

Study 2 will add a separate multi-turn negotiation engine later. Do not implement
its bargaining protocol as part of Study 1.

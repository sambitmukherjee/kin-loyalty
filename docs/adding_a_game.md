# Adding a game — implementation outline

The engine renders configured templates, builds flat integer/string response
schemas, and executes frozen manifests. Study 1's balance algorithm is separate
from the transport-independent runner, card renderer, clients, and attempt logs.

1. Define the new decision and its outcome fields in a separate study config.
2. Write plain-text templates and a response schema, preserving neutral card and
   identity rendering. Keep person names out of JSON field names.
3. Add a deterministic manifest builder for the new design. The current validator
   supports flat required integer/string fields, bounds, and enums; extend and
   test it explicitly if a new task requires other JSON-schema features.
4. Reuse the clients, card renderer, log format, and runner patterns, keeping
   single-decision assumptions out of the shared components.
5. Add mock-client tests for valid/invalid/truncated replies and resume behavior.
6. Define analyses before observing main outcomes, and obtain any required design,
   prompt, phase, and spending approvals.

Study 2 will add a separate multi-turn negotiation engine later. Do not implement
its bargaining protocol as part of Study 1.

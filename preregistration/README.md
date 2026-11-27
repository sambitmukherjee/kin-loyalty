# Pre-registrations and frozen data versions

Both studies were registered before their main collections. The registrations
and completed data collections have separate annotated Git tags. A registration
tag preserves the protocol, code, prompts, settings and planned requests before
main collection. A data tag preserves the subsequent completed collection and
the code present when it was frozen.

| Tag | Commit | What it preserves |
| --- | --- | --- |
| `prereg-study1` | `d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a` | The final Study 1 registration and main manifest. |
| `study1-data` | `f7dd0a690a5089b245fff365acf002fcfd7b056a` | The completed Study 1 collection of 3,600 valid main decisions. |
| `prereg-study2` | `c277054e182eb3a81a475108fa3439e96e869bb0` | The final Study 2 addendum and 960-episode main manifest. |
| `study2-data` | `3b3b85d77c619fcc6fb093a93915e5ef769cbf53` | The completed Study 2 collection, with all 960 terminal episodes. |

Both registration commits and tags were pushed before their respective main
collections. The dated records are preserved in the [decision log](../docs/decisions.md).
The [Study 1 protocol](study1.md) defines the hypotheses and estimands, including
P2. The [Study 2 addendum](study2.md) specifies the negotiation implementation
and analysis. Their hash inventories are [study1-lock.json](study1-lock.json)
and [study2-lock.json](study2-lock.json).

The registration documents describe the state at registration. Statements in
them about an unstarted main run or a pending push are historical. Those texts
and their inventories are preserved unchanged. Both main collections and both
pre-registered analyses are now complete. The [Study 1 results](../results/study1/README.md)
and [Study 2 results](../results/study2/README.md) record the analysis sources,
original commands and independent reproduction checks. The data tags predate
the saved main analysis outputs; those outputs are committed on `main`.

## Study 2 execution change after registration

Before the first main call, the researcher approved a mechanical execution
patch, commit `4e088670c0cc8386eccf8fff01d93d353a230bda`. It added the main
launcher and recorded both the registration and execution commits in each main
turn and episode record. The registered analysis, parameters, seeds, prompts,
settings, protocol and scoring were unchanged. The original `prereg-study2`
tag was preserved.

Consequently, the difference between `prereg-study2` and `study2-data` includes
execution code as well as collection artifacts. This deviation is documented
in the [execution patch report](../docs/study2_main_execution_patch.md) and the
decision log. A data-tag commit identifies the frozen collection snapshot;
the execution hash inside a record identifies the code that made the call.
These hashes serve different purposes.

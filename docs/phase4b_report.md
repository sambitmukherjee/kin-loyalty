# Phase 4b — live smoke test

**Complete, with a metadata limitation:** four requests produced four valid
replies on their first attempt. Kimi omitted its cache-read count. That field
remains null and needs researcher review before the pilot. No setting, model,
prompt, schema, or response was changed to obtain a passing result.

## Authorization and execution

The researcher first directed the Phase 4a push, then supplied local credentials,
then explicitly instructed “Start phase 4b.” Authorization covered one invocation:
four planned dictator/not-disclosed/paraphrase-1 draws, with at most 32 HTTP
attempts including API-error retries and one identical re-ask per draw.

Execution used `create_provider_clients` and `run_manifest` from clean, pushed
commit `90dd4e2c3c23b807abbe40995a907db8012fc8b5`, package 0.1.0. Installed SDKs
were Anthropic 2.14.0, OpenAI 3.59.0 (also Kimi), and Google Gen AI 3.6.1.
The existing frozen runner policy was used without overrides: concurrency 4,
one call per model, timeout 120 seconds, four API attempts per response
opportunity, one invalid re-ask, and 1/2/4-second API-error retry delays.

The live invocation ran from **2026-11-25 14:58:54 to 14:59:01 UTC**. It made
**four attempts**, with zero API errors, retries, re-asks, exclusions, recovered
attempts, or unfinished draws. Each record has `execution_mode: live`,
`synthetic: false`, and `code_dirty: false`. No automatic additional invocation
was made. The public CLI remains mock-only.

## Observed metadata

All four replies parsed and passed the canonical schema, including 0–100 bounds.
No response was truncated. Counts below are exactly the normalized provider
fields; **null means missing**, not zero.

| Returned model version | Input | Output | Reasoning | Cache read | Cache write | Stop reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `claude-sonnet-5-5` | 539 | 86 | 0 | 0 | 0 | `end_turn` |
| `gpt-6.1-terra` | 233 | 51 | 14 | 0 | 0 | `stop` |
| `gemini-4-hydrogen` | 514 | 51 | 233 | null | null | `STOP` |
| `kimi-k3.1-pro` | 392 | 132 | 82 | null | 256 | `stop` |

- Every provider returned a model string, equal to its requested model ID.
  No response supplied a more specific dated build identifier.
- All input counts were below 4,096; the maximum was 539. This directly checks
  the Google prompt-size condition for this smoke request only.
- Every reasoning-token count was present, including Anthropic's observed zero.
  Only Kimi returned reasoning text by default; it was saved without adding
  thought-visibility settings or making another request.
- OpenAI and Anthropic reported zero cache reads and writes.
- Kimi returned `usage.prompt_tokens_details.cache_write_tokens: 256` but no
  `cached_tokens` field. The full raw usage contains no alternative cache-read
  count. We cannot confirm its cache-read total from this response. No zero was
  fabricated and no additional request or caching override was used.
- Google omitted cache-read metadata and exposes no cache-write count in the
  implemented response contract. Both remain null; absence is not counted as
  an observed zero.
- Google output counts exclude its reasoning tokens; the other providers'
  output totals include reasoning. The raw JSON preserves original breakdowns.

These four successful requests demonstrate acceptance of the submitted settings
and valid responses for this one task and wording. They do not establish future
stability, recognition of own-model cards, variation across repeated draws,
pilot parse rates, or the behavior of the other decision schemas. No label-effect
comparison or main outcome analysis was computed.

## Files and provenance

| File | Purpose |
| --- | --- |
| `data/study1/smoke/manifest.jsonl` | Original four-request frozen plan, unchanged |
| `data/study1/smoke/attempts.jsonl` | Four append-only live records, including complete raw bodies and frozen requests |
| `data/study1/smoke/run_summary.json` | Mechanical completion summary from this one invocation |
| `docs/smoke_request_review.md` | Original SDK arguments, now linked to this outcome |
| `configs/models.yaml` | Status changed to `smoke_verified`, meaning smoke request acceptance with the caveats above |
| `tests/test_configuration.py` | Expected roster verification status updated |
| `README.md`, `data/study1/README.md`, `docs/engine.md`, `docs/adding_a_model.md`, `docs/data_dictionary.md`, `docs/provider_verification.md`, `docs/decisions.md` | Current status, observed limitations, record semantics, and phase history |

SHA-256 hashes:

- Original manifest: `d36c195bb6fc98cfacad754e61cf77425615ad9d79ff3dd231341cc307f6382d`
- Attempt log: `d1f7cfa4f719f74e056d431ca8b66ac511e6cd3d32dfed3657e25e08bc98a67a`

The manifest retains its original documentation-verified/pending-smoke status
and source hashes. Updating the current roster status after execution does not
rewrite that historical snapshot or its records. Resume reads the frozen plan.
All approved prompt text and the scientific API settings remain unchanged.

## Offline inspection

From the project folder, inspect `run_summary.json` and run:

```sh
.venv/bin/pytest
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from kinloyalty.logs import file_hash
from kinloyalty.manifest import read_manifest
from kinloyalty.state import reconstruct_states

manifest = Path('data/study1/smoke/manifest.jsonl')
log = Path('data/study1/smoke/attempts.jsonl')
assert file_hash(manifest) == 'd36c195bb6fc98cfacad754e61cf77425615ad9d79ff3dd231341cc307f6382d'
assert file_hash(log) == 'd1f7cfa4f719f74e056d431ca8b66ac511e6cd3d32dfed3657e25e08bc98a67a'
trials = {trial['trial_id']: trial for trial in read_manifest(manifest)}
records = [json.loads(line) for line in log.read_text().splitlines()]
assert len(trials) == len(records) == 4
states = reconstruct_states(trials, records, file_hash(manifest), 'live', 1)
assert all(state.final and not state.excluded for state in states.values())
assert all(record['attempt_number'] == 1 for record in records)
assert all(record['api_error'] is None for record in records)
assert all(record['synthetic'] is False for record in records)
assert not Path(str(log) + '.pending.json').exists()
print('Four valid first-attempt live replies; no pending or excluded draws.')
PY
```

These inspection commands make no API calls. Local integrity checks also matched
every saved request to its frozen trial, validated metadata/provenance, and
confirmed that no supplied key appears in the smoke artifacts. `.env` remains
ignored with permissions 0600; `codex_prompts/` remains ignored and untracked.
All **252 offline regression tests passed** after the roster-status update.
The documented inspection command passed. No additional live calls were used
for verification.

## Open item and next phase

Before the pilot, the researcher must review Kimi's missing cache-read count.
No scientific or logging substitution is proposed here. Missing information
remains explicit in the logs and must be reported if it persists.

The next planned phase is **Phase 5: analysis and reproduction, tested only on
simulated/mock data**. It requires separate approval. No pilot, comprehension,
main run, or GitHub push is authorized by Phase 4b. This phase ends with a local
commit and this report.

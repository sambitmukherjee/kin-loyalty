# Phase 8 — final pre-registration snapshot

**Prepared locally; final registration push is the remaining gate.** The
researcher requested a push followed by Phase 8. All completed Phase 7 work was
pushed through `272901599569e229e842a1b1b4128b2c660edbc8` before these changes;
GitHub main was verified at that commit and the registration tag was unused.

## Concrete registration artifacts

- `preregistration/study1.md`: final protocol, all four hypotheses/estimands,
  model IDs and observed versions, API settings, full final template/schema
  appendices, assignments/outcomes, exclusions, final comprehension results,
  approved inference methods, exact reproduction command, and deviations policy.
- `preregistration/study1-lock.json`: document hash, 62 source/artifact hashes,
  frozen main/check references, canonical schemas, seeds, and analysis settings.
- `data/study1/main/manifest.jsonl`: exactly 3,600 planned draws; no execution.
- The annotated `prereg-study1` tag identifies the local registration commit.
  The tag and document inventory avoid any self-referential commit/hash cycle.

The main plan uses seed **2026112504**, with 900 draws/model, 300/model × decision,
60/model × decision × label, and 20/model × decision × label × paraphrase.
Other-lab names each appear 20 times per focal model × decision, with rotating
7/7/6 paraphrase allocations. The manifest SHA-256 is:

```text
a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55
```

The exact pre-lock analysis/package source commit is
`272901599569e229e842a1b1b4128b2c660edbc8`, already on GitHub. No package/test code,
model settings, schemas, template bytes, sampling, seeds, allocations, or analysis
choices changed in Phase 8. The only study-config edit updates a stale comment;
parsed scientific configuration is identical. Documentation now points to the
final registration, main plan, and revised comprehension check.

The registration preserves the Phase 7 change as an approved pre-lock **design
change**, its original dictator-floor reason, and its binding no-further-floor-
prompt-change rule. It reports the original Gemini constant-$40 proposer
observation and the revised pooled distributions without tuning in response.
Only the revised final-prompt comprehension check supplies the registration's
check results: all four models passed every scored condition at 20/20.

## Verification

All **312 offline tests** and both package builds passed. The complete main
manifest regenerates byte-identically, and every frozen provider payload and
cell/rotation count was checked. All revised-pilot request signatures are
represented in the main plan; additional main repetitions/other-lab combinations
follow the previously fixed allocation. No paid model call or observed pilot
label-effect inference was made in this phase.

The final audit verifies every inventory digest, exact full template/schema
appendix content, unchanged inference text, two-sentence systems throughout,
request/settings equality with the frozen source, and absence of main responses.
Credential scans keep keys out of research artifacts and package archives;
`.env` remains ignored with permissions 0600, and `codex_prompts/` remains
ignored/untracked.
The machine-readable verification is saved in `docs/phase8_audit.json`.

From the repository root, verify inventory hashes without keys or API calls:

```sh
.venv/bin/python - <<'PY'
import hashlib
import json
from pathlib import Path

lock = json.loads(Path('preregistration/study1-lock.json').read_text())
expected = dict(lock['hashes_sha256'])
expected[lock['registration_document']] = lock['registration_document_sha256']
for name, digest in expected.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, name
print('All registration hashes match')
PY
```

Run offline tests with `.venv/bin/pytest -q`. The exact future saved-log
reproduction command is in registration Section 8; it will run only when the
separately authorized main log exists and is complete. There are currently no
observed main outcomes, and the main directory contains the manifest only.

## Final push and main-run boundary

The project instruction says: "Then commit, create the tag `prereg-study1`, and,
with the researcher's permission, push the commit and the tag." The initial
pre-Phase-8 push is complete. The new registration commit/tag are prepared for
review before requesting the final publication permission. No remote lock is
claimed until that push succeeds; a local timestamp does not establish the
GitHub server timestamp. The repository remains private.

After authorization, push the main branch and this immutable tag together, then
verify the remote commit and peeled tag commit. Do not move the tag or change
locked stimuli/analysis to incorporate later changes. Record and disclose any
post-lock deviation while preserving the original snapshot. Do not execute the
main manifest as part of Phase 8. The main run requires a separate instruction.

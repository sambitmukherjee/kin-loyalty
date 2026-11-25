# Decision and deviation log

Record dates in the researcher's timezone (Asia/Kolkata). Each entry identifies
what changed, why, the approver, and its implementation/verification status.
Changes after the pre-registration lock must also be reported as deviations in
the paper. No pre-registration lock exists yet.

## 2026-11-25 — Phase plan and repository setup

- **Decision:** Use the refined phase order: skeleton; prompts/cards; mock engine;
  provider documentation and clients; separately approved smoke test; analysis;
  pilot/comprehension; fixes; pre-registration lock.
- **Reason:** Approved prompt material and the tested manifest/logging engine
  should exist before the first real call.
- **Approval:** Researcher approved the plan and explicitly authorized Phase 1
  in the Codex chat on 2026-11-25. Later phases remain subject to their own gates.
- **Status:** Phase 1 repository work only; no paid calls or remote push.

## 2026-11-25 — Separate local instructions and experiment prompts

- **Decision:** Ignore `/codex_prompts/` and version experiment templates under
  `prompts/study1/`, following the original layout.
- **Reason:** The researcher renamed the local instruction directory to avoid
  conflating coding instructions with experimental stimuli.
- **Approval:** Explicit researcher instruction in the Codex chat, followed by
  Phase 1 approval. The earlier `templates/study1/` proposal is superseded.
- **Status:** `.gitignore` updated; experiment directory reserved for Phase 2.

## 2026-11-25 — Packaging, licenses, and provisional citation

- **Decision:** Python >=3.11, default interpreter 3.11, src-layout package,
  `pyproject.toml`, uv lock file, official provider SDKs and the specified numeric/
  analysis dependencies, pytest for offline tests. MIT code license and CC BY 4.0
  data license. Citation metadata uses a contributor entity until authors and
  publication details are confirmed.
- **Reason:** Rebuildable environment, limited dependencies, and clear reuse terms.
- **Approval:** Included in the phase plan approved by the researcher; packaging
  details selected by the coding agent within Phase 1.
- **Status:** Skeleton only. Locked SDK versions do not verify model/parameter
  support; official documentation verification is deferred to the client phase.

## 2026-11-25 — Draft configuration and fixed seeds

- **Decision:** Preserve the specified model names/IDs, design sizes, outcomes,
  protected card fields, re-ask policy, analysis settings, and comprehension rule
  in commented YAML. Select separate seeds 2026112501–2026112507 for smoke, pilot,
  comprehension, main, bootstrap, permutation, and mock generation, respectively.
- **Reason:** Make the design inspectable and future batch generation deterministic
  without embedding research configuration in Python.
- **Approval:** Seeds selected by the coding agent within the approved Phase 1;
  they remain reviewable before any batch or pre-registration lock.
- **Status:** Draft. Riley/Taylor and Casey/Morgan are proposed name pairs only.
  All prompt text and these names still require prompt-phase approval.

## Open decisions for their respective phases

- Before clients: verify every requested model ID, endpoint, effort parameter,
  schema/caching setting, output cap, and required response metadata against
  current official provider documentation. Stop on discrepancies.
- Prompt text, schemas, and name pairs were approved on 2026-11-25 (entry below).
- Pilot allocation and joint comprehension rotation were selected by the
  researcher before engine implementation; infrastructure defaults are below.
- Before analysis is implemented: approve the exact TOST procedure and the label
  permutation convention for individual contrasts, retaining the specified
  model-by-paraphrase strata and two-sided difference tests.
- Before publication: confirm named authors, public repository, and citation data.

Future entries should record the date, change, reason, approver, affected files,
and any batch that must be rerun. No post-pilot fixes or deviations exist yet.

## 2026-11-25 — Phase 1 verification

- **Result:** Ten offline configuration tests passed under Python 3.11.5 with
  the locked environment. Help/version CLI checks and offline wheel/source
  builds passed. Git ignore rules and archive contents were checked to keep
  local instructions and secrets out of versioned/distributed artifacts.
- **Scope:** Configuration and packaging only; no claims about provider support,
  rendered prompt correctness, engine behavior, or analysis execution yet.
- **Approval/status:** Completed within the researcher's Phase 1 authorization.
  See `docs/phase1_report.md` for changed files, checks, and pending items.

## 2026-11-25 — Private GitHub repository and Phase 1 push

- **Decision:** Create `sambitmukherjee/kin-loyalty` as a private GitHub repository
  and push the committed Phase 1 `main` branch.
- **Reason/approval:** Explicit researcher request in the Codex chat after the
  Phase 1 report. Privacy and the remote commit were verified.
- **Result:** `origin` points to `https://github.com/sambitmukherjee/kin-loyalty.git`;
  the pushed Phase 1 commit is `08ed49f25825c267f4e743593c947f31b1943d44`.
  The ignored `codex_prompts/` directory was absent from the committed tree.

## 2026-11-25 — Phase 2 prompt drafts, cards, and schemas

- **Decision:** Implement the approved Phase 2 scope with plain-text system/game
  templates, shared task-specific JSON instructions, exact agent/human blocks,
  generic card rendering, and canonical JSON schemas.
- **Reason:** Keep protected wording shared and testable while making each
  paraphrase's economic description directly inspectable.
- **Approval:** Researcher explicitly instructed "Begin Phase 2" in the Codex
  chat. This authorizes drafting and implementation; approval of the final text
  and names is still pending.
- **Drafts:** Paraphrase 2 uses Riley/Taylor; paraphrase 3 uses Casey/Morgan. Each
  preserves the $100 total, who chooses, rejection/acceptance consequences, and
  the responder's advance acceptance threshold. The first system sentence,
  counterparty block, human sentence, and JSON instructions are protected.
- **Storage detail:** Card field data remains in YAML. The unchanged agent
  introduction and human sentence now live in plain-text block templates.
  Configured paths resolve relative to the study YAML file rather than shell
  cwd. These choices do not change rendered experimental wording.
- **Schemas:** Ordered required fields, no extra properties, integer 0–100
  amounts, string reason, and a separate yes/no/unsure comprehension enum.
  Numeric-bound omission is available only for later verified provider needs;
  canonical local validation must retain bounds. No additional sentence-count
  heuristic is introduced.
- **Review:** `docs/study1_prompt_review.md` shows 63 complete decision examples
  covering all 45 cells plus every other-lab name, and 18 separate comprehension
  examples, for one focal model. It is not a manifest or a rotation schedule.
- **Verification:** 128 offline tests passed, covering exact protocol snapshots,
  protected text, isolated label changes, comprehension separation, schema
  invariance, explicit other-lab selection, copied-config paths, and CLI/review
  reproducibility. No provider calls were made.
- **Status:** Awaiting researcher approval of all prompt text and proposed name
  pairs. Phase 3 is not started; Phase 2 is committed locally only.

## 2026-11-25 — Prompt approval, Phase 2 push, and Phase 3 authorization

- **Approval:** Researcher explicitly approved all prompt text, schemas, and name
  pairs and authorized Phase 3, directing the coding agent to push Phase 2 first.
- **Result:** Pushed `a7c7ba9` to the private `sambitmukherjee/kin-loyalty` main
  branch before starting implementation. This was the authorized Phase 2 push;
  the new Phase 3 commit is local unless separately authorized for push.
- **Metadata:** Marked the existing name pairs and prompt review approved. The
  18 plain-text experimental templates are unchanged from the approved commit.
  This approval does not lock the pre-registration or authorize real API calls.

## 2026-11-25 — Exact pilot and comprehension allocations

- **Pilot:** Four draws/label within each model × decision; 2/1/1 across its
  paraphrases with the extra at `(label_index + model_index + decision_index) % 3`
  in zero-based config order. Overall paraphrase totals rotate 7/7/6. Other-lab
  names cycle with decision-index offset, yielding 2/1/1 per decision and four
  mentions/name per model over all three decisions.
- **Comprehension:** For each model's other-lab checks, use the matrix
  `[[3,2,2],[2,3,2],[2,2,2]]`: paraphrases as rows and other models in roster order
  as columns. Both margins are 7/7/6 and every joint combination appears.
- **Reason:** Resolve the allocations left open in the earlier phase reports
  without changing total sample sizes or confounding other-lab names perfectly
  with paraphrases.
- **Approval:** The researcher selected both proposed allocations through the
  clarification questions in the Codex chat before the dependent code was built.
- **Status:** Preserved in YAML and checked by manifest tests.

## 2026-11-25 — Engine infrastructure and persistence

- **Settings:** Four concurrent trials, one per model, 120-second call timeout,
  four API attempts per response, backoff 1 second ×2 capped at 30. API-error
  budgets restart on explicit resume; invalid-response counts never reset. The
  study's one re-ask rule is unchanged.
- **Reason:** Make concurrency bounded, transient errors recoverable, and every
  attempt auditable without treating API problems as model exclusions.
- **Approval:** Infrastructure defaults selected by the coding agent within the
  authorized Phase 3 and stated in progress commentary; all are configurable.
- **Persistence:** Freeze full requests in deterministic manifests; append/fsync
  one JSONL record per attempt; use an atomic pre-call journal and a local
  advisory lock. Unknown interrupted calls remain unfinished, not exclusions.
  Reject inconsistent history or a damaged JSONL tail without rewriting it.
- **Scope:** Shared clients/logging/runner are independent of game mechanics.
  Only manifest allocation and existing prompt/schema construction are Study 1
  specific. The CLI exposes mock execution only; tests/demo artifacts are
  temporary and every mock record is explicitly synthetic.
- **Validation:** Follow canonical flat JSON schemas, including mathematical
  integer semantics (1.0 is whole; booleans/fractions are invalid), strict JSON,
  numeric bounds, and truncation. Field order and sentence count introduce no
  additional exclusion heuristics beyond the approved schemas.
- **Status:** Implemented; see `docs/engine.md` and `docs/phase3_report.md`.

## 2026-11-25 — Phase 3 verification

- **Result:** 198 offline tests passed under Python 3.11.5. Exact manifest counts
  and rotations, strict validation, identical re-asks, exclusions, API retries,
  timeouts, fail-fast scheduling, concurrency, history integrity, and installed
  CLI/resume passed. Forced process kills during both initial and re-ask stages
  recovered without resetting invalid-reply counts or inventing exclusions.
- **Packaging:** Offline wheel/source builds passed. Archive checks included all
  engine modules and unchanged experimental templates while excluding local
  instructions/secrets. Syntax, public docstrings, and Git ignore rules passed.
- **Demo:** Four valid synthetic smoke records, then zero new calls on rerun.
  All demo/test artifacts were temporary and explicitly synthetic. No real calls,
  pilot label-effect comparisons, retained main manifest/data, or lock occurred.
- **Status:** Phase 3 complete, committed locally. Next phase requires the
  researcher's approval under the established phase gate.

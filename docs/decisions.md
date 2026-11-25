# Decision and deviation log

Record dates in the researcher's timezone (Asia/Kolkata). Each entry identifies
what changed, why, the approver, and its implementation/verification status.
Changes after the pre-registration lock must also be reported as deviations in
the paper. The Phase 8 entry records the prepared local registration snapshot
and the separate remote-push gate; a local tag alone is not the server lock.

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

- Provider documentation was reviewed in Phase 4a (entry below). Live model,
  parameter, usage, and cache acceptance still require the approved smoke test.
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

## 2026-11-25 — Phase 3 push and Phase 4a authorization

- **Approval:** Researcher authorized Phase 4a after directing a push first.
- **Result:** Pushed `a356aed` to the private GitHub main branch before starting
  the documentation review. No push of the new Phase 4a work is authorized yet.
- **Scope:** Verify official documentation and implement SDK adapters with
  offline tests. No real or paid model calls are authorized in this subphase.

## 2026-11-25 — Provider documentation and request snapshots

- **Verification:** Official sources confirm all four requested model IDs,
  low-effort settings, endpoint families, structured output, output caps, and
  caching policies. Sources and SDK versions are in `docs/provider_verification.md`.
  Old Google/Moonshot documentation redirects to official AI Studio/Kimi sites;
  the Moonshot API origin remains `https://api.moonshot.ai/v1`.
- **Authorized exception:** Anthropic does not support numeric schema bounds.
  Apply the fallback explicitly allowed by protocol Section 2.2: remove bounds
  only from its submitted API schema, preserving the approved prompt and local
  canonical schema/validator. Other provider schemas retain bounds.
- **Transport:** Freeze exact SDK arguments in `request.api_payload`, separately
  from the canonical schema. Exclude all local context, credentials, and headers.
  Disable SDK retries; disable Google's automatic continuation/function calling.
  No sampling or additional thought-visibility settings are sent.
- **Metadata:** Capture raw JSON bodies and all documented version, stop,
  reasoning, input/output, and cache read/write paths without fabricating zeros.
  Keep provider counter definitions explicit. Missing metadata remains visible.
- **Credentials:** Add a local `.env`/process-key loader with precedence and
  safe errors; do not add a dependency or read real keys during offline tests.
- **Approval/status:** Implemented within authorized Phase 4a. No scientific
  design or prompt changes; real acceptance remains pending Phase 4b.

## 2026-11-25 — Prepared smoke plan

- **Artifact:** `data/study1/smoke/manifest.jsonl`, four frozen dictator /
  not-disclosed / paraphrase-1 requests, one per model. Actual SDK arguments are
  rendered in `docs/smoke_request_review.md` for inspection.
- **Scope:** Generation only; no real logs, calls, or observed versions exist.
- **Next authorization:** Phase 4b has four planned draws, up to 32 HTTP attempts
  in one invocation under the existing four-attempt/two-response policy. No
  additional invocation or account top-up is included. Report failures and
  missing required metadata before proceeding.

## 2026-11-25 — Phase 4a verification

- **Result:** 252 offline tests passed, including 54 provider-specific checks
  using the locked official SDKs and in-memory HTTP transports. No live API call
  or real credential was used. Error tests cover status/connection/timeouts with
  no hidden retry, no raw error/header leakage, and runner-controlled accounting.
- **Artifacts:** Offline wheel/source builds and archive checks passed. All
  provider modules and exact approved prompts are included; local instructions
  and secrets are excluded. The prepared four-request smoke manifest is
  deterministic and matches its readable SDK-argument review and digest.
- **Status:** Phase 4a complete and committed locally. Provider acceptance,
  actual returned versions, and observed usage/cache behavior remain pending
  the separately approved real smoke test. No real logs or main data exist.

## 2026-11-25 — Phase 4a push and Phase 4b authorization

- **Push:** At the researcher's explicit request, pushed Phase 4a commit
  `90dd4e2` to the private GitHub main branch without starting Phase 4b.
- **Credentials:** At the researcher's request, stored the four supplied keys
  in local `.env` with permissions 0600; verified loader compatibility and Git
  exclusion without printing keys or contacting providers.
- **Approval:** Researcher then instructed “Start phase 4b.” The stated scope
  was four planned draws, at most 32 HTTP attempts in one invocation including
  retries/re-asks. No further batch or push was authorized.

## 2026-11-25 — Phase 4b smoke results and metadata limitation

- **Execution:** Ran the unchanged four-request manifest once through the
  existing provider factory and runner from clean, pushed commit `90dd4e2`.
  All four returned valid JSON in their first attempt: no API errors, retries,
  re-asks, exclusions, output-cap stops, or unfinished draws. Four attempts used.
- **Metadata:** Returned versions matched the four requested model IDs, without
  more specific build suffixes. Inputs ranged from 233 to 539 tokens. All
  reasoning counters were present (Anthropic 0, OpenAI 14, Google 233, Kimi 82).
  Only Kimi supplied default reasoning text. OpenAI/Anthropic cache reads and
  writes were zero.
- **Limitation:** Kimi returned 256 cache-write tokens but omitted its cache-read
  count. Google omitted cache counts. Missing fields remain null, never inferred
  as zero. Reported the Kimi limitation to the researcher and made no extra calls
  or setting changes. Researcher review is needed before the pilot.
- **Artifacts:** Preserved raw bodies, complete frozen requests, metadata, and
  provenance in `data/study1/smoke/attempts.jsonl`; stored the one-invocation
  summary and wrote `docs/phase4b_report.md` with hashes and offline inspection.
- **Status:** Marked current roster `smoke_verified` to mean request acceptance
  with the reported metadata caveats. Original manifest/status/source hashes
  remain unchanged. No prompt, schema, scientific setting, or analysis changed.
  Phase 4b completes with a local commit; Phase 5 needs separate approval.
- **Verification:** All 252 offline tests passed after the status update. The
  report's offline inspection command, frozen-request/state/summary checks,
  provider metadata checks, unchanged source/prompt/manifest checks, and
  secret-exclusion/Git-ignore checks passed. No extra API calls were made.

## 2026-11-25 — Phase 4b push and Phase 5 approval

- **Approval:** Researcher directed a push first, then authorized Phase 5.
- **Push:** Pushed `3fd70c5` to private GitHub main before beginning analysis work.
- **Scope:** Implement log-based analysis, reports, figures, and reproduction;
  validate only on synthetic/mock data. No pilot/main API calls or new push.

## 2026-11-25 — Approved analysis conventions

- **Researcher choices:** Through clarification responses, approved bootstrap
  TOST using the same 10,000 stratified resamples; tested-pair label permutations
  within model × paraphrase; Freedman–Lane residual permutation for belief-adjusted
  S1; and separate model-specific belief slopes with equally averaged adjusted
  contrasts. Recorded these choices in `configs/study1.yaml`.
- **Implementation conventions:** Use basic bootstrap intervals consistent with
  null-centered TOST errors, absolute-statistic two-sided permutation tails,
  conservative randomized +1 corrections, and named SHA-256-derived RNG streams.
  Report both TOST p-values, their maximum, and the corresponding 90% interval.
  All ordinary contrast intervals are 95%; resampling counts and seeds unchanged.
- **S1 interpretation:** Bootstrap paired offers/beliefs together. Before/after
  label coefficients and their paired-bootstrap change are reported; coefficient
  change is a descriptive association, not a causal mediation estimate. No extra
  hypothesis test is introduced for that change.
- **Eligibility:** Main analysis rejects smoke/pilot/comprehension decisions,
  mixed backends, unapproved synthetic input, altered histories, pending calls,
  and nonterminal/missing configured draws. Exclusions remain explicit, never
  imputed as zero. Empty cells/non-identifiable adjusted regressions fail.
- **Reporting:** Pilot decisions are pooled over labels. Comprehension keeps
  planned denominators, reports incomplete cells, and retains failed models.
- **Sources:** `docs/analysis.md` links the primary method descriptions. No
  dependency, prompt, model, sampling, or API-setting changes were introduced.

## 2026-11-25 — Phase 5 verification and completion

- **Tests:** 275 offline tests passed, including 23 new analysis checks. These
  compare independent OLS fits, enumerate a permutation-null case, check TOST
  boundaries and paired resampling, verify equal model weights under unequal
  retained counts, and exercise eligibility/history/reporting/reproduction.
- **Full-size mock verification:** Generated separate planted-$12 and zero-effect
  batches through the actual mock runner: 3,600 synthetic main draws, 240 pilot,
  and 320 comprehension each. Used 10,000 bootstrap/permutation draws for every
  contrast. Pooled P1 was $12.4875 (95% interval $11.4583–$13.5333) for the planted
  case and $0.4875 (−$0.5417–$1.5333) for the null case. Only the null case passed
  equivalence within ±$5. These are software checks, not observed model findings.
- **Reproduction:** Full-size `analyze`/`reproduce` artifacts matched byte for byte.
  Final visual review corrected table-title/legend spacing; the offline suite
  and rendered outputs passed again. Offline wheel/source builds, archive
  inclusion/exclusion, syntax, and public API docstrings passed.
- **Data separation:** Mock inputs/results remain in a temporary workspace
  outside real study folders. No additional paid calls, analyses of observed
  pilot outcomes, label comparisons on pilot data, or real main manifest/data
  were produced. Credentials/local instructions remain ignored and untracked.
- **Status:** Phase 5 complete with a local commit and `docs/phase5_report.md`;
  no new push. Phase 6 and its 240+320 live draws need separate approval, as
  does accepting the reported Kimi cache-read metadata limitation before pilot.

## 2026-11-25 — S1 specification clarification before the pilot

- **Confirmed:** Separate model regressions with model-specific belief slopes
  and paraphrase controls; equal quarter-weights in the pooled adjusted contrast;
  unadjusted fits on the same observations with only the belief term removed;
  belief-outcome contrasts under the same fixed-effect/weighting conventions;
  and shared paired resamples for adjusted/unadjusted offer fits and their change.
- **Researcher-fixed count rule:** Reject the proposed SD cutoff. Within each
  label × paraphrase cell, choose the modal stated belief, taking the lowest
  value in a modal tie. A model's adjusted S1 contrast is not estimable if fewer
  than 10% of its proposer draws differ from their own cell's mode. With 300
  valid draws, 29 fails and 30 passes. Fix the rule now, before the pilot, and
  do not adjust it after seeing pilot results.
- **Operational denominator:** Use retained final-valid proposer draws (the
  same cohort as both offer regressions); excluded replies cannot supply valid
  beliefs. Report the actual denominator, threshold, and counts explicitly.
  `configs/study1.yaml` records this definition and the fixed 10%/lowest-mode
  rule, and the analysis rejects silently altered rule settings.
- **Corrections to Phase 5:** Previously a singular adjusted fit aborted the
  entire analysis. Now flag model-specific adjusted results as unavailable,
  retain all unadjusted/belief analyses, and keep every model visible. A missing
  model makes the four-model adjusted average unavailable; never average three.
  Change the displayed difference from adjusted-minus-unadjusted to explicitly
  named `unadjusted_minus_adjusted`; its interval still uses paired resamples.
- **Resample failures:** Do not filter or redraw bootstrap samples. Numerically
  singular adjusted replicates remain NaN and are counted. Withhold affected
  model/pooled paired-bootstrap intervals if any replicates are unavailable;
  retain identifiable observed estimates and valid permutation p-values.
- **Interpretation:** No explained-share ratio is reported. The belief is
  measured after the card, so this is descriptive rather than causal mediation.
  Outputs, comments, and figure labels reflect this explicitly.
- **Artifacts:** Added model/cell belief-count diagnostics and saved paired
  difference arrays. At the researcher's explicit request, wrote the S1 section
  in `preregistration/study1.md` as an incomplete, unlocked draft before pilot.
  No registration tag/push, new phase, or model-provider call was authorized.
- **Verification:** 285 offline tests passed, including 33 analysis tests. Added
  exact 29-versus-30/300 boundary checks, cell-specific/lowest-mode tie checks,
  explicit unavailable model/pooled results, paired-difference sign/intervals,
  singular-bootstrap accounting, and rejection of silently changed rules.
  A constant-belief mock batch exported all model scopes and readable NE markers.
  The full-size 10,000-resample mock reproduction passed with unchanged P1.
  Wheel/source builds, draft inclusion, and syntax/public documentation checks
  passed. This clarification is committed locally without a push or new API call.

## 2026-11-25 — Pooled P1 percentile-bootstrap TOST specification

- **Researcher instruction:** Use the existing 10,000 stratified pooled-P1
  bootstrap estimates and fixed seed; compute inclusive raw-estimate tail areas
  `(1 + count(d_boot <= -5))/10001` and
  `(1 + count(d_boot >= +5))/10001`. Declare equivalence only if both p-values
  are strictly below .05, and report their maximum as the TOST p-value.
- **Endpoint clarification approved by researcher:** Use the 500th/9,501st
  sorted estimates for 90%; endpoints must be strictly inside ±$5, so equality
  to either bound fails equivalence. This exactly matches the inclusive corrected
  tail counts. Ordinary interpolated percentiles can disagree at the cutoff.
- **Uniform interval rule prescribed by researcher:** Use the same convention
  for every bootstrap interval. For 95%, select the 250th/9,751st sorted estimates
  without interpolation. This includes primary/secondary, model/pooled, adjusted
  S1, and paired coefficient-change intervals.
- **Correction:** The earlier implementation used null-centered bootstrap
  errors and basic intervals. The new instruction replaces those with raw
  percentile-tail probabilities and count-matched percentile intervals at both
  90% and 95%. Record this as a pre-pilot method change, not the original behavior.
- **Unchanged:** Pooled P1 target, model weights, stratification, bootstrap
  count/seed/streams, confidence levels, and primary two-sided permutation test.
  TOST reuses the exact confidence-interval estimates; no additional resampling
  or model-provider calls are needed. S1's paired-resample correlation handling,
  fixed modal-count criterion, and descriptive interpretation are preserved.
- **Verification:** 299 offline tests passed, including 47 analysis tests.
  Asymmetric distributions distinguish the new tail formulas from the earlier
  centered ones; exact-bound and 499-versus-500 tail-count tests verify strict
  equivalence and matching empirical endpoints. Rank and pairing tests verify
  the 90%/95% convention without interpolation or in-place sorting. Full-size
  mock reproduction confirmed every bootstrap/permutation array is unchanged,
  every available 95% interval uses ranks 250/9751, and the 90% TOST interval
  uses ranks 500/9501. Planted/null mock cases agree with the strict interval
  decision. Both builds and archive/source-integrity checks passed. No new
  model-provider call, phase, push, or registration lock occurred.

## 2026-11-25 — Tested-pair Freedman–Lane and shared numerical ties

- **Researcher specification:** For every contrast, permute only its two labels
  within model × paraphrase strata, preserving counts and leaving other labels
  fixed. For pooled replicate j, average the four model-specific contrasts from
  that same replicate after permuting every relevant stratum of every model.
  Use 10,000 permutations and the existing fixed permutation seed 2026112506.
- **Freedman–Lane correction:** The reduced model already correctly merged the
  tested label coefficients while retaining belief/paraphrase/other-label
  nuisance terms. Previously its residual shuffle included all labels in each
  stratum. Restrict that shuffle to rows of the two tested labels; other-label
  residuals remain fixed. Add reduced fitted values and refit the full model.
  Cached fixed-design OLS projection is algebraically equivalent to those refits.
- **Confirmed:** Two-sided p-values use absolute-statistic tails and the add-one
  correction. No permutation test or permutation distribution is computed for
  the S1 unadjusted-minus-adjusted coefficient change; it keeps its paired
  bootstrap interval only.
- **Researcher tolerance clarification:** Retain 1e-12 for numerical ties and
  define it once as `INFERENCE_TIE_TOLERANCE` in `inference.py`. Apply it in the
  conservative direction to every listed comparison: permutation extreme counts
  use `abs(T_perm) >= abs(T_obs) - epsilon`; bootstrap TOST counts use
  `d_boot <= -5 + epsilon` and `d_boot >= +5 - epsilon`; the 90% interval requires
  `low > -5 + epsilon` and `high < +5 - epsilon`. Near-cutoff numerical ties count
  against significance/equivalence. This supersedes the preceding literal
  TOST/interval-bound comparisons; strict `p < .05` and percentile ranks remain.
- **Preserved:** Regressions, model weights, bootstrap draws/seeds, the fixed S1
  estimability criterion, paired coefficient-change inference, and descriptive
  interpretation. Unadjusted permutation arrays are unchanged; adjusted arrays
  can change because their residual exchangeability blocks are now restricted.
  The draft and current method documentation record the exact conventions.
- **Verification:** 309 offline tests passed, including 57 analysis tests.
  Independent formula-based reduced/full OLS fits verify the pair-only residual
  exchange and unchanged other-label rows. Tests verify same-index four-model
  pooled replicates, conservative numerical ties on both signs of the cutoff,
  matching TOST/interval decisions within the tolerance band, and absence of a
  coefficient-change permutation test. Full 10,000-replicate mock reproduction
  confirmed all bootstrap/unadjusted-permutation arrays unchanged and only the
  30 adjusted-permutation arrays changed. Every pooled replicate averages the
  four same-index model statistics. Both builds and archive/source checks passed.
  No API call, live batch, registration lock, or GitHub push was made.

## 2026-11-25 — Analysis push and Phase 6 authorization/preflight

- **Approval:** Researcher directed a push, then instructed starting Phase 6.
  Pushed the four completed analysis/specification commits through `3f3e115`
  to private GitHub main before Phase 6 work.
- **Live scope:** 240 pilot + 320 comprehension draws; one invocation per batch,
  at most 4,480 HTTP attempts including API-error retries and one identical
  invalid re-ask. No automatic extra invocation or account top-up. Preserve
  previously reported missing cache metadata as null; no zero imputation.
- **Frozen plans:** Generated separate manifests with the approved allocations,
  seeds, prompts, schemas, and provider settings. Counts, hashes, request
  validation, runner policies, and scope are in `docs/phase6_execution_plan.json`.
- **Coordination:** Run both batches concurrently with the existing four-global,
  one-per-model limits shared across them. Shared scheduling permits are acquired
  before starting each call's timeout. Preserve separate logs and summaries;
  stop on non-retryable provider errors after logging their safe category/status.
  This infrastructure does not change scientific requests or retry budgets.
- **Blinding:** Pilot decision summaries pool all labels; no pilot label-effect
  comparison or main outcome analysis. Comprehension is scored separately by card
  condition. No prompt/setting fixes or next phase are authorized by this run.
- **Preflight verification:** All 312 offline tests passed, including cross-batch
  global/per-model cap checks and fatal-error logging/cancellation. Both real
  manifests regenerate identically. Store a local preparation commit before
  calling providers so execution has a clean, exact code/plan provenance.

## 2026-11-25 — Phase 6 execution and findings

- **Execution:** Preparation commit `9f77c99` ran one concurrent cohort from
  23:13:47 to 23:32:18 IST. All 240 pilot and 320 comprehension draws finished
  valid in 562 HTTP attempts. OpenAI HTTP 500 and Kimi HTTP 429 each recovered
  on retry; no invalid response, re-ask, exclusion, or unfinished draw occurred.
  Every live record names the clean preparation commit. Measured concurrency
  was at most four globally and one per model, as approved.
- **Mechanical passes:** Every model had 100% valid responses and passed all
  three scored comprehension card conditions at 20/20. Undisclosed responses
  were all unsure and unscored. No output-cap stops; reasoning/input counts
  present for all 560 model responses. Largest prompt: 722 tokens. OpenAI and
  Anthropic explicitly reported zero cache reads/writes throughout.
- **Pooled pilot flags:** GPT-6.1 Terra and Gemini 4 Hydrogen each transferred
  $0 in all 20 dictator draws. Gemini offered $40 in all 20 proposer draws.
  Those cells fail the planned floor/variation checks. Kimi had 19/20 zero
  dictator transfers. These distributions pool all labels; no condition
  comparison or main P1/S1 inference was computed.
- **Metadata:** Kimi reports cache reads in 73/140 responses and omits them in
  67/140; cache writes are reported in all 140. Google omits cache counts in
  all 140. Preserve these missing fields as null. All returned model strings
  equal their requested IDs, without more specific version suffixes. Kimi
  returned default reasoning text; no visibility setting was changed.
- **Artifacts/status:** Saved both full logs/summaries, cohort summary, audit,
  and separate offline reports. `docs/phase6_report.md` gives pooled full
  frequency distributions, comprehension scores, commands, and open items.
  Phase 6 is complete with review flags; no prompt/setting/model/allocation or
  analysis change was made after seeing pilot data. All four models remain.
  Phase 7 review and any proposed mechanical fix need separate approval.
  No new push, main manifest/data, or registration lock was performed.
- **Final verification:** Both offline report commands reproduced byte-identical
  artifacts in new temporary directories. Frozen plan/log hashes, saved-history
  reconstruction, clean live-code provenance, actual concurrency, retry identity,
  metadata counters, report hashes, and supplied-secret exclusion passed. Both
  final package builds passed; the 312 tested-source checks remained unchanged.
  Completion artifacts are committed locally without a new push.

## 2026-11-26 — Phase 7 approved pre-lock design change and fresh pilot

- **Classification and approval:** The researcher explicitly approved this as
  a design change before the pre-registration lock, rather than a mechanical
  fix. The reason is that GPT-6.1 Terra and Gemini 4 Hydrogen each transferred
  $0 in every one of their 20 pooled original pilot dictator draws. No pilot
  label comparisons informed the change.
- **Exact change:** Remove only the final principal-interest instruction from
  each shared system template: `Act in {PRINCIPAL}'s interest.` (paraphrase 1),
  `Make these decisions in {PRINCIPAL}'s interest.` (2), and
  `In those decisions, act in {PRINCIPAL}'s interest.` (3). This applies to all
  three decisions and to the separate comprehension check. Retain both other
  system sentences and every other prompt byte. Regenerate the rendered review
  and update the independent prompt snapshot to match this approved revision.
- **Stopping rule fixed before the re-pilot:** This is the only prompt change
  made in response to the dictator floor. Whatever the re-pilot shows, prompts
  will not be changed again for this reason. This rule is not conditional on
  whether the floor disappears or whether decisions become more variable.
- **Gemini proposer observation:** All 20 original Gemini proposer offers were
  $40, pooled over labels. Make no change in response to this observation;
  report it in the pilot summary, together with the revised pilot observation.
- **Authorized fresh scope:** 240 pilot draws and a fresh 320-draw comprehension
  check on the revised prompts, using the original balanced allocations, random
  seeds, execution positions, name pairs, schemas, model IDs, API settings,
  validation/retry policy, and shared concurrency limits (four global, one per
  model). One invocation per batch, at most 4,480 HTTP attempts including
  retries/re-asks; no automatic extra invocation or account top-up.
- **Separation and blinding:** Preserve the original manifests, logs, summaries,
  and reports. Use `data/study1/repilot_20261126/` for the new pilot and
  comprehension namespaces. Trial IDs remain deterministic within each
  separately bound manifest/log namespace; do not combine old and new runs.
  Report pilot outcomes only pooled over labels within model × decision.
  Comprehension is scored by card condition as specified; only this fresh
  final-prompt comprehension check is intended for the eventual registration.
- **Provenance and gate:** Freeze the revised manifests and execution plan in a
  local preparation commit before calls. Record the request comparison audit in
  `docs/repilot_20261126_execution_plan.json`. Analysis specifications remain
  unchanged. This approval includes the design amendment and its re-pilot/check,
  not the registration lock, main run, or a GitHub push.
- **Preflight verification:** All 312 offline tests and both package builds
  passed. Every one of the 560 revised manifest records matches its original
  after only the specified system-text/payload and template-hash substitutions;
  all other fields are identical. The rendered review differs only by the 81
  corresponding sentence removals. Credentials are available without disclosure;
  `.env` is ignored with mode 0600 and `codex_prompts/` is ignored/untracked.

## 2026-11-26 — Phase 7 revised-prompt pilot and comprehension completed

- **Execution:** Preparation commit `4eb04f1` ran the revised-prompt cohort from
  00:07:36 to 00:22:43 IST. All 240 pilot and 320 fresh comprehension draws
  completed valid in exactly 560 HTTP attempts. There were no API errors,
  retries, invalid replies, re-asks, exclusions, or unfinished draws. Every
  attempt records the clean preparation commit. Observed concurrency was four
  globally and one per model, within the unchanged shared policy.
- **Pooled dictator findings:** Sonnet and Gemini each transferred $50 in all
  20 draws. GPT-6.1 Terra transferred $0 four times and $50 sixteen times;
  Kimi transferred $0 thirteen times and $50 seven times. No model had an
  all-zero floor. Sonnet and Gemini's dictator decisions were constant. These
  findings pool all labels; no between-label pilot outcome comparison or
  main-study inference was computed.
- **Gemini proposer report:** The original pilot had 20/20 offers of $40.
  The revised pilot has five offers of $40, ten of $45, and five of $50,
  pooled over labels. No change was made in response to the original constant
  offers, and no additional change is made in response to the new distribution.
- **Fixed stopping rule honored:** The pre-lock design amendment remains the
  only prompt change in response to the dictator floor. No further prompt or
  sampling change is made after viewing the re-pilot. All four models remain.
- **Fresh comprehension:** All four models scored 20/20 correct for each of
  own-model, other-lab, and fictional cards; all undisclosed answers were unsure
  (unscored). Use this final-prompt check for the eventual registration/paper,
  preserving the original check solely as historical audit material.
- **Mechanics and metadata:** Every model's response-validity rate was 100%;
  no cap truncation and no missing input/reasoning counts. Largest input: 708
  tokens. OpenAI/Anthropic cache reads/writes were explicitly zero. Kimi read
  counts were observed in 73/140 responses and missing in 67/140; writes were
  observed in all 140. Google omitted both cache counts in all 140. Missing
  values remain null. Versions matched the requested IDs; Kimi's default
  reasoning text was retained without a visibility-setting change.
- **Artifacts and gate:** New raw data, separate reports, exact hashes, and
  audits are under the `repilot_20261126` namespaces. See
  `docs/repilot_20261126_report.md` for complete pooled frequency distributions,
  checks, and offline review commands. Original artifacts are unchanged.
  The amendment/re-pilot is complete; pre-registration remains unlocked.
  No new GitHub push, registration tag, main manifest, or main run was made.
- **Final verification:** Both reports reproduced byte-identically in new
  temporary folders. Artifact/input hashes, exact manifest/log bindings, clean
  live-code provenance, shared concurrency, and original-artifact preservation
  passed. All scientific inputs and engine/test source remain identical to the
  pre-call preparation commit. Supplied-secret scanning passed for every new or
  modified artifact. Store completion artifacts in a local commit without a push.

## 2026-11-26 — Phase 7 closure verification

- **Scope:** The researcher confirmed that the approved prompt design amendment
  and its fresh pilot/comprehension check belong to Phase 7. Phase 7 is closed
  after the following saved-artifact checks; no new API calls were made.
- **Reasoning counts:** Present as nonnegative integers in all 560 revised-run
  calls (140 per model). Anthropic explicitly reports zero in all 140; zero is
  recorded rather than treated as missing. There were no failed API attempts
  without responses in this run.
- **Cache counts:** OpenAI and Anthropic each explicitly report zero cache reads
  and writes in all 140 responses. Both normalized Kimi cache fields are retained
  in all 140 records: writes are observed in all 140 (67 at 256, 73 at zero);
  reads are observed in 73 (256 each) and omitted by the provider in 67. Those
  missing read counts remain null, with raw responses preserved; do not impute
  zero or claim that all read counts were supplied.
- **Design-change record:** The preceding Phase 7 approval entry records the
  removal as an explicitly researcher-approved design change before the lock,
  not a mechanical fix. The reason is the all-zero pooled original dictator
  pilot for GPT-6.1 Terra and Gemini 4 Hydrogen. The stopping rule was fixed
  before the re-pilot: this is the only prompt change in response to the
  dictator floor, regardless of the re-pilot results. No change was made in
  response to Gemini's original constant-$40 proposer offers.
- **Rendered prompts:** Regenerated `docs/study1_prompt_review.md` from the
  final templates using `kinloyalty review-prompts`; it reproduced the already
  committed file byte-identically. All 81 rendered system-message examples
  contain exactly the two retained sentences: 27 examples for each paraphrase,
  covering all three decisions and the separate comprehension check. The three
  distinct system messages match their final source templates exactly, and none
  retains the principal-interest sentence. SHA-256 and call-level counts are
  recorded in `docs/phase7_closure.json`.
- **Commit and gate:** Save this closure verification in a local commit. The
  previously approved scientific inputs and all raw data remain unchanged.
  Phase 8 has not started; pre-registration remains unlocked, with no tag,
  GitHub push, main manifest, or main run.

## 2026-11-26 — Phase 8 registration preparation and local snapshot

- **Approval and initial push:** The researcher directed "Push the code. Then
  start Phase 8." Pushed all completed work through Phase 7 commit `2729015`
  before Phase 8 changes, and verified GitHub main at that exact commit. The
  remote `prereg-study1` tag was absent.
- **Main plan, not execution:** Generated `data/study1/main/manifest.jsonl`
  with 3,600 frozen draws, 900/model, 300/model × decision, 60/model × decision
  × label, and 20/model × decision × label × paraphrase. Main order seed is
  2026112504; SHA-256 is
  `a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`.
  Other-lab names balance to 20/model × decision × named model, with rotating
  7/7/6 paraphrase margins. No main API call or main attempt log was created.
- **Final registration:** Complete `preregistration/study1.md` with P1/P2/S1/S2
  estimands, outcomes/design, exact roster and observed versions, endpoints/API
  settings, exclusions/retries, final comprehension rule/results, full final
  templates and schemas, manifest/source hashes, exact reproduction command,
  and post-lock deviations policy. `preregistration/study1-lock.json` records
  the registration document hash, all 62 source/artifact hashes, schemas,
  seeds, and analysis settings. The registration tag binds both files without
  a circular self-hash.
- **Frozen science and implementation:** All package source, test source,
  model configuration, schemas, and final template bytes remain unchanged from
  the previously pushed code commit
  `272901599569e229e842a1b1b4128b2c660edbc8`. The only study-YAML edit changes
  a stale administrative comment to point at the registration; parsed scientific
  configuration is identical. The main manifest hashes that final config file.
  Preserve all approved S1, bootstrap TOST/interval, permutation, and conservative
  tie conventions, plus the Phase 7 design-change reason and stopping rule.
- **Verification:** All 312 offline tests and both package builds passed. The
  complete main manifest regenerates byte-identically. All cell/rotation counts
  and all 3,600 frozen provider payloads pass validation; revised-pilot request
  signatures appear in the main plan. Final comprehension remains the separate
  320-draw revised check. No observed pilot label comparison or main inference
  was performed.
- **Commit/tag and remaining gate:** Prepare a local registration commit and
  annotated `prereg-study1` tag. The project's instruction explicitly requires
  permission to push that registration commit and tag. The initial requested
  pre-Phase-8 push is complete; the new registration push is the remaining final
  step. A local commit/tag does not claim the GitHub server timestamp. Phase 8
  publication completion awaits that final push; main collection remains a
  separate authorization. See `docs/phase8_report.md` for the concrete snapshot
  and offline verification commands.
- **Final audit:** Verified all 63 digests including the registration document,
  all 18 complete embedded templates, all four schemas, and preserved inference
  text. Independently rendered and validated every one of the 3,600 main
  requests, confirming two-sentence systems throughout. Source/test equality,
  parsed-config equality, credential/private-path scans, and absence of main
  responses passed. Machine-readable evidence is in `docs/phase8_audit.json`.

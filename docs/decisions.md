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
- Before prompts are approved: finalize paraphrases 2/3 and their name pairs.
- Before the engine is implemented: settle exact pilot allocation, the joint
  comprehension name/paraphrase rotation, and concurrency/timeouts/retry budgets.
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

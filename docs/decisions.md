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

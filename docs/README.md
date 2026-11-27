# Documentation guide

The repository serves two purposes: reproducing the paper from its recorded
responses, and helping researchers build another experiment with the existing
engines. The guides below provide the complete workflows. The local data,
prompt and results READMEs identify the files used at each step.

## Start with a complete workflow

| Goal | Guide |
| --- | --- |
| Reproduce the registered results, compare outputs and find the paper's figure/table sources. | [Reproduce the paper](reproducing_the_paper.md). This uses frozen code and data and needs no model calls or API keys. |
| Copy configurations and prompts, inspect requests, run mocks, resume and analyse another example. | [Run a new experiment](running_a_new_experiment.md). It also explains live interfaces and where additional code is required. |
| Compile the manuscript and appendices into one PDF. | [Paper build guide](../paper/README.md), including dependencies, validation and optional figure conversion. |

## Find files and methods

| Material | Study 1 | Study 2 |
| --- | --- | --- |
| Recorded data and development batches | [Data index](../data/study1/README.md) | [Data index](../data/study2/README.md) |
| Source templates and prompt assembly | [Prompt index](../prompts/study1/README.md) | [Prompt index](../prompts/study2/README.md) |
| Saved main outputs and reproduction evidence | [Results index](../results/study1/README.md) | [Results index](../results/study2/README.md) |
| Eligibility, estimation and inference | [Analysis methods](analysis.md) | [Analysis methods](study2_analysis.md) |
| Fully rendered illustrative requests | [Prompt review](study1_prompt_review.md) | [Prompt review](study2_prompt_review.md) |

The [registration index](../preregistration/README.md) explains protocol and data
tags and links both registrations and their hash inventories. A hash is a file's
digital fingerprint, used here to identify frozen inputs. The
[data dictionary](data_dictionary.md) describes manifest, attempt and output
fields. A manifest is the fixed plan saved before collection; attempt logs
record what happened while executing it.

For implementation details, see [engine behavior and recovery](engine.md),
[adding a model or provider](adding_a_model.md) and
[adapting or adding a game](adding_a_game.md). The
[provider verification report](provider_verification.md) describes the original
requests and source dates; it is historical evidence rather than a current
compatibility guarantee for another model.

## Research history and verification records

Both main collections and analyses are complete. The [decision log](decisions.md)
retains dated research decisions and deviations. Earlier reports use phase
numbers from implementation and registration. Their statements about work still
to come describe the date of each report, not the current repository status.

| Record | Purpose |
| --- | --- |
| [Study 1 collection report](study1_main_collection_report.md) | Completion, errors, resumption and registration provenance for the main collection. |
| [Study 2 collection report](../results/study2/main-collection-report/collection-report.md) | Main collection mechanics and replay checks. |
| [Study 1 re-pilot report](repilot_20261126_report.md) | The final-prompt pilot and comprehension check, kept separate from main outcomes. |
| [Study 2 pilot report](study2_phase6_report.md) | Blind pilot review and mechanical diagnostics. |
| [Study 2 execution patch](study2_main_execution_patch.md) | The approved main-launch and dual-provenance change after registration. |
| [Reproduction verification](reproduction-validation.json) | The documentation pass's frozen-checkout comparisons. |
| [Paper portability verification](../paper/portability-validation.json) | The ordinary-tool build and comparison with the published PDF. |
| [New-experiment verification](new-experiment-validation.json) | Worked mock examples, resumption, replay and interface checks. |
| [Documentation navigation checks](navigation-validation.json) | Final README examples, prompt-review comparisons, links and preservation checks. |

The result indexes also link the original independent reproduction audits.
These records describe checks performed at particular revisions; they do not
replace rerunning the appropriate workflow for a new checkout or experiment.

Return to the [main README](../README.md) for the project overview and citation.

# Study 1 prompt templates

These files are the registered stimuli used for the completed Study 1 collection.
They cover three wordings of the dictator, ultimatum proposer and ultimatum
responder tasks. The economics and condition text remain the same across
wordings; the person names and some phrasing vary.

Read the [complete rendered review](../../docs/study1_prompt_review.md) to see
what is sent to a model, including the response schemas. For another experiment,
follow the [worked guide](../../docs/running_a_new_experiment.md) to copy and
edit separate templates. The [registration index](../../preregistration/README.md)
identifies the frozen versions, and the
[reproduction guide](../../docs/reproducing_the_paper.md) explains how the paper
uses the recorded responses.

## Source files

| Wording | Names | System message | Dictator body | Proposer body | Responder body |
| --- | --- | --- | --- | --- | --- |
| 1 | Alex / Jordan | [system_1.txt](system_1.txt) | [dictator_1.txt](dictator_1.txt) | [ultimatum_proposer_1.txt](ultimatum_proposer_1.txt) | [ultimatum_responder_1.txt](ultimatum_responder_1.txt) |
| 2 | Riley / Taylor | [system_2.txt](system_2.txt) | [dictator_2.txt](dictator_2.txt) | [ultimatum_proposer_2.txt](ultimatum_proposer_2.txt) | [ultimatum_responder_2.txt](ultimatum_responder_2.txt) |
| 3 | Casey / Morgan | [system_3.txt](system_3.txt) | [dictator_3.txt](dictator_3.txt) | [ultimatum_proposer_3.txt](ultimatum_proposer_3.txt) | [ultimatum_responder_3.txt](ultimatum_responder_3.txt) |

The shared introductions are [counterparty_agent.txt](counterparty_agent.txt)
and [counterparty_human.txt](counterparty_human.txt). Reply instructions are in
[reply_dictator.txt](reply_dictator.txt),
[reply_ultimatum_proposer.txt](reply_ultimatum_proposer.txt),
[reply_ultimatum_responder.txt](reply_ultimatum_responder.txt) and
[reply_comprehension.txt](reply_comprehension.txt).

## How a request is assembled

For example, an Alex/Jordan dictator request uses `system_1.txt` as its system
message and `dictator_1.txt` as the start of its user message. The renderer fills
in the focal model, lab and person names. It replaces the counterparty block
with the human description or the agent introduction and card, according to
the condition. The user message ends with two newlines followed by the literal
contents of `reply_dictator.txt`.

The card's fields, order and model text are defined in
[configs/study1.yaml](../../configs/study1.yaml). The card renderer puts exactly
two spaces before each field and adds no ratings or trust cues. The five labels
are `own_model`, `other_lab`, `fictional`, `not_disclosed` and `human`. An
`other_lab` request names a specific eligible model; the manifest determines
which name is used for each decision.

The separate comprehension check uses the dictator system message and body,
including its card, but replaces the monetary decision instruction with
`reply_comprehension.txt`. It excludes the human condition. Decision requests
do not include that model-match question.

Source files end with a newline. Rendering removes that one file terminator
and preserves internal spaces and line breaks. JSON braces in the shared reply
instructions remain literal text. The first system sentence is identical across
wordings; the second and the game descriptions vary.

## Regenerate the readable review

After the [main setup](../../README.md#set-up-a-current-checkout), run this from
the repository root using a fresh output path:

```sh
mkdir -p scratch/prompt-reviews
uv run --offline --locked kinloyalty review-prompts \
  --config configs/study1.yaml --model claude_sonnet_5_5 \
  --output scratch/prompt-reviews/study1.md
```

The selected model's review contains 63 decision examples and 18 comprehension
examples, including each eligible other-lab name. These are coverage examples,
not observed responses or the allocation schedule. The command reads templates
and configuration; it makes no model calls and needs no credentials.

The final two-sentence system prompts followed an approved change before
registration. The [decision log](../../docs/decisions.md) and
[re-pilot report](../../docs/repilot_20261126_report.md) preserve that history.
Local coding-agent instructions belong in the separate ignored
`codex_prompts/` directory, not among these experiment templates.

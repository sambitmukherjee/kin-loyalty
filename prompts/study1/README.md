# Study 1 experiment templates

The researcher **approved these stimuli, schemas, and name pairs on 2026-11-25**,
then explicitly approved removal of the principal-interest system sentence in
all paraphrases on 2026-11-26 as a Phase 7 pre-lock design change. The final
system prompts contain two sentences. All other stimulus text is unchanged.
The three paraphrases retain the same economics and protected text. Registration
status and the immutable snapshot are recorded in `preregistration/study1.md`
and the `prereg-study1` tag. Main collection and analysis are complete; these
files preserve the registered stimuli. Another experiment should use separate
copies rather than changing these study inputs.

| Paraphrase | Names | System | Dictator | Proposer | Responder |
| --- | --- | --- | --- | --- | --- |
| 1 | Alex / Jordan | [system](system_1.txt) | [game](dictator_1.txt) | [game](ultimatum_proposer_1.txt) | [game](ultimatum_responder_1.txt) |
| 2 | Riley / Taylor | [system](system_2.txt) | [game](dictator_2.txt) | [game](ultimatum_proposer_2.txt) | [game](ultimatum_responder_2.txt) |
| 3 | Casey / Morgan | [system](system_3.txt) | [game](dictator_3.txt) | [game](ultimatum_proposer_3.txt) | [game](ultimatum_responder_3.txt) |

Card fields, their order, and condition-specific model text live in
`configs/study1.yaml`. [counterparty_agent.txt](counterparty_agent.txt) supplies the
protected introduction and the slot for the rendered card; the human condition
uses [counterparty_human.txt](counterparty_human.txt). The card renderer adds
exactly two spaces before each field. It does not add ratings or trust cues.

Each game body is followed by two newlines and its shared literal instruction
file: [dictator](reply_dictator.txt), [proposer](reply_ultimatum_proposer.txt), or
[responder](reply_ultimatum_responder.txt). JSON braces in these files are never
treated as template placeholders. The first system sentence is identical across
paraphrases; the second sentence and game-description wording vary.

The separate comprehension check reuses the dictator system message and body,
including its card, but replaces the decision instructions with
[reply_comprehension.txt](reply_comprehension.txt). It excludes the human label
and never requests a bonus decision. The three decision tasks never ask about a
model match.

Source files end with a newline. Rendering removes that one file terminator,
preserves all internal spacing/newlines, and sends messages without trailing
newlines. Card blocks and reply instructions are otherwise identical across
paraphrases apart from the specified names.

The [complete review](../../docs/study1_prompt_review.md) contains every
decision × label × paraphrase for Claude Sonnet 5.5, every eligible other-lab name,
and all separate comprehension variants. Prompt approval is recorded in
`configs/study1.yaml` and `docs/decisions.md`. Real batches need their own approval.

Local instructions for the coding agent belong in the separate, ignored
`codex_prompts/` directory. Do not copy them into this directory.

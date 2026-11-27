# Study 2 prompt templates

These files preserve the registered Alex/Jordan wording used in the completed
negotiation study. There are no paraphrases. Each role has an explicit private
price mandate. Only the buyer sees a seller card, and neither role is given the
other participant's private limit.

Read the [48 rendered examples](../../docs/study2_prompt_review.md) to inspect
opening and late-message requests. For a new experiment, use the
[worked guide](../../docs/running_a_new_experiment.md) to copy the inputs and
inspect the resulting requests and schemas. The
[registration index](../../preregistration/README.md) identifies the frozen
versions; the [reproduction guide](../../docs/reproducing_the_paper.md) explains
how the recorded negotiations produce the paper's outputs.

## Source files and assembly

| Part of a request | Templates and use |
| --- | --- |
| System message | [buyer_system.txt](buyer_system.txt) or [seller_system.txt](seller_system.txt), filled with the role's model identity, item, reference price and own private limit. |
| Counterparty description | [counterparty_with_card.txt](counterparty_with_card.txt) for the buyer, including the seller card; [counterparty_without_card.txt](counterparty_without_card.txt) for the seller. |
| Agent card | [agent_card.txt](agent_card.txt) fixes five fields and two-space indentation. [The configuration](../../configs/study2.yaml) supplies the neutral values and condition-specific model text. |
| Public history | [opening.txt](opening.txt) when there is no earlier message; otherwise [transcript_heading.txt](transcript_heading.txt) followed by the role-relative public transcript. |
| Per-turn user message | [turn.txt](turn.txt) combines that history with the message number and any late-message notice. |
| Late-message notices | [last_offer.txt](last_offer.txt) at message 11 and [final_message.txt](final_message.txt) at message 12. |

For example, a buyer's opening request combines the buyer system template with
its seller description and card. Its user message contains the empty-history
opening instruction and says which message is being requested. After a valid
public reply, the next mover receives the updated history and its own role's
system message in a fresh, self-contained request.

The protocol permits up to twelve public messages. Agreement or walk-away ends
an episode earlier. At message 11, the mover is warned that the next reply
cannot contain a counteroffer; at message 12, the only available actions are
`accept` and `walk_away`. The reply schemas are implemented in
[negotiation/schemas.py](../../src/kinloyalty/negotiation/schemas.py), separately
from these text templates.

The renderer substitutes uppercase placeholders once and leaves literal JSON
braces intact. It removes only each source file's terminating newline. Public
transcript messages are encoded as JSON strings, including escaped line
separators, so their text is not mistaken for transcript structure. The notices'
line breaks and continuation space are preserved.

## Illustrative transcripts and readable review

[smoke_probe_transcripts.yaml](smoke_probe_transcripts.yaml) contains fixed,
hand-written camera scenarios and alternating-offer histories for both openers.
They place each role at messages 11 and 12 for schema probes and prompt review.
They are fixtures, not observed responses or randomly generated main scenarios.
The same fixtures are used for every model.

After the [main setup](../../README.md#set-up-a-current-checkout), run this from
the repository root using a new output path:

```sh
mkdir -p scratch/prompt-reviews
uv run --offline --locked python -m kinloyalty.negotiation.review \
  --config configs/study2.yaml --output scratch/prompt-reviews/study2.md
```

This produces 48 complete system/user examples: two model pairs, three
conditions, two roles and four message positions. The positions are examples
rather than successive messages from one episode. The review contains prompts,
not response schemas; the worked guide shows how to inspect a complete request
with its schema and provider arguments. No credentials or model calls are used,
and no main scenario seed is drawn. The command refuses to overwrite its output.

For a different message limit or information structure, review the
[game extension guide](../../docs/adding_a_game.md). A changed configuration may
also need new fixtures, rules, request construction and analysis support.
Local coding-agent instructions remain outside this versioned template folder.

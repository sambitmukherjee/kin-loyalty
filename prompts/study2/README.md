# Study 2 prompt sources

These templates implement the single Alex/Jordan wording specified for Study 2.
There are no paraphrases. `buyer_system.txt` and `seller_system.txt` retain the
explicit private price mandates. The Study 2 renderer supplies the buyer with
the seller's card and supplies no card to the seller.

`agent_card.txt` fixes the card's five fields and two-space indentation.
`configs/study2.yaml` supplies the neutral card values. Only the underlying-model
line varies across disclosure conditions. `counterparty_with_card.txt` and
`counterparty_without_card.txt` supply the matching introductions.

`turn.txt`, `transcript_heading.txt`, `opening.txt`, `last_offer.txt`, and
`final_message.txt` compose the single user message. The renderer substitutes
uppercase placeholders once, leaves literal JSON braces intact, and removes
only each source file's terminating newline. Transcript messages are rendered
as JSON string literals, including escaped line separators. The last-offer and
final-message notices retain the specified line breaks and continuation space.
The default configuration renders exactly 12 messages; the limit is a parameter
for other experiments.

`smoke_probe_transcripts.yaml` contains fixed, hand-written camera scenarios and
alternating-offer prefixes for both openers. These are illustrative fixtures,
not observed data or seeded main scenarios. A message-11 probe uses the first
ten messages of the requested role's opener transcript; a message-12 probe uses
the first eleven messages of the other role's opener transcript. The same
prefixes supply Phase 1's review positions. All models use the same fixtures.

Read the 48 complete system/user examples in `docs/study2_prompt_review.md`.
To reproduce them in a new file from the repository root:

```sh
.venv/bin/python -m kinloyalty.negotiation.review \
  --config configs/study2.yaml --output /tmp/kinloyalty-study2-review.md
```

The output path must not exist. No credentials, SDKs, API calls, observed data,
or main scenario draws are used. Reply schemas and the negotiation engine are
implemented in the separately approved Phase 2.

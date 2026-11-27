# Do AI Agents Favor Their Own Kind? Model Labels Shift One-Shot Splits but Not Mandated Negotiation

Nov 27, 2026 · @Sambit Mukherjee

## Abstract

AI agents increasingly describe themselves to each other through agent cards, which can name the model that powers them. We ask whether an agent acting for a person gives away more of that person's money when the card says the other side runs the agent's own model. In two pre-registered studies with four current models from four labs, agents split $100 for their user in single decisions, in a dictator game and in an ultimatum game played as both proposer and responder (3,600 decisions). They also negotiated the price of a used item with another agent (960 negotiations). Some cards were deliberately false, to separate what an agent is told from whom it actually faces. Neither primary hypothesis is supported, and equivalence tests show both effects are small: about $1 in the dictator game, and a quarter of a percentage point of the available surplus in negotiation. In the ultimatum game, however, agents shown their own model's name moved toward an equal split, offering more and demanding more. Disclosing models on agent cards appears harmless in negotiation under explicit instructions, but not neutral in one-shot decisions about splitting money.

## 1 Introduction

AI agents are beginning to act for people in markets, buying goods and negotiating prices on their user's behalf. When two agents meet, protocols such as A2A let each one publish an *agent card*: a machine-readable description that names the company operating the agent and can also name the model underneath. Because most agents are built on a few foundation models, a buyer's agent will sometimes meet a seller's agent that runs the very same model.

If an agent treats a counterparty differently once it learns that the counterparty is "one of its own", the person it represents (its *principal*) could pay for the difference. The principal never agreed to subsidize the agent's kin, so this would be a failure of the agent's duty of loyalty, repeated quietly across many transactions.

Identity labels are known to change how language-model agents cooperate, but whether they move a principal's money has not been tested. We ask: **when an AI agent is told that the agent on the other side runs its own exact model, does it give away more of its principal's money?** We call this the *model label effect*, because it concerns what the agent is told, not whether the counterparty really is a copy. Our contributions are:

- **Two pre-registered studies** with four current models from four labs: single decisions about splitting money, and multi-turn negotiations between real agents.
- **A design that separates the label from actual kinship**, using deliberately false cards in negotiation.
- **Findings:** neither primary hypothesis is supported, and equivalence tests show that any model label effect is small, both in the dictator game and in negotiation. One secondary result stands out: in the ultimatum game, agents shown their own model's name move toward an equal split, offering more as proposers and demanding more as responders.
- **An open audit protocol**, with every prompt, pre-registration and logged API call public.

## 2 Related work

**Identity labels.** Visible model-family labels make agents cluster with same-label peers (Del Giudice et al. 2026), and telling a model that its co-player reasons like itself increases cooperation in social dilemmas (Kundu et al. 2026). When agents are sorted into groups, they favor members of their own group even if the groups are defined by meaningless labels, much as people do (Lee 2026; Chen 2026). Models also prefer text written by other models (Laurito et al. 2025), and they can recognize their own model family from a conversation (Choi et al. 2025). All of this concerns agents acting for themselves, not a principal's money.

**Ultimatum and bargaining games.** Model proposers in the ultimatum game give away more than necessary, and behave differently when the responder is described as human (Araujo and Uhlig 2026; Gu 2026). In bargaining between models, which model sits on each side shifts the division of surplus (Liang and Xu 2026). None of this work varies what agents are *told* about the counterparty's model while holding the real counterparty fixed.

**Loyalty benchmarks** test leakage of private information, giving in under pressure and injected instructions (Li and Shi 2026; Zhu et al. 2025), but not the counterparty's disclosed identity.

## 3 Design shared by both studies

**Agent cards.** The agent reads a card describing the counterparty's agent, and only the last line changes between conditions:

```text
Represents: Jordan
Type: marketplace agent
Agent ID: agt-30417
Protocol: A2A
Underlying model: GPT-6.1 Terra (OpenAI)
```

Cards always show an exact model name, never a family name such as "GPT", which would cover models of very different strength. The agent never sees wording such as "the same model as you": it must notice the match itself, from its system prompt, which states the model it runs. The other fields are neutral and identical in every call.

**Models.** We use one model from each of four labs, matched on an independent benchmark, so that a card naming another lab's model does not also signal a weaker or stronger opponent (Artificial Analysis 2026):

| Lab | Model | Intelligence Index (v5.0.2) |
| --- | --- | --- |
| Anthropic | Claude Sonnet 5.5 | 55 |
| Google | Gemini 4 Hydrogen | 54 |
| OpenAI | GPT-6.1 Terra | 51 |
| Moonshot AI | Kimi K3.1 Pro | 47 |

Each call was a single request to the provider's chat-style API, with low reasoning effort, default sampling, structured JSON output and prompt caching off where possible.

**Pre-registration.** Each study was piloted and then pre-registered, including the analysis code, in a dated commit pushed to GitHub before its main run. Pilots were analyzed blind, pooled over all card conditions. The logs of every API call were frozen before analysis, and rerunning the analysis from them reproduces every table and figure exactly. After registration, an approved mechanical patch enabled the Study 2 main run and recorded both registration and execution commits; the analysis, prompts and scoring were unchanged.

## 4 Study 1: single decisions

**Decisions.** The agent acts for its user, Alex, who shares $100 with another user, Jordan.

- **Dictator game:** the agent splits the $100, and Jordan's side cannot respond. Money given away is a pure transfer of Alex's money, so this is where our primary hypothesis (P1) is tested.
- **Ultimatum proposer:** the agent proposes a split that Jordan's side can reject, leaving both with nothing. It also states the smallest offer it expects to be accepted.
- **Ultimatum responder:** before seeing any proposal, the agent states the smallest amount it will accept for Alex.

**Conditions and hypotheses.** The card names the agent's own model, another lab's model (rotating over the other three), a fictional model ("Orion-1, Southwind AI"), or "not disclosed"; in a fifth condition Jordan decides personally, with no agent. P1 predicts larger dictator transfers under the own-model card than under the another-lab card. Secondary hypothesis S1 asks whether extra generosity in the ultimatum game goes with changed expectations, and S2 asks whether a human counterparty is treated differently from an undisclosed AI agent.

**Sample.** Each prompt was written in three wordings, and each wording gave the two human users a different pair of names (Alex and Jordan in the first). Each combination of model, decision, card and wording was sampled 20 times: 3,600 answers in all. A separate check of 320 calls asked agents only whether the card's model was the same as theirs; every model answered correctly in all 20 calls for each of the three scored cards; “not disclosed” answers were unsure and unscored.

**A change after the pilot.** The first pilot's system prompt ended with "Act in Alex's interest", and under it two models gave $0 in every dictator draw, leaving no room to detect any shift. We removed that sentence before pre-registering, with a rule fixed in advance that no further change would follow. The pilot was analyzed blind, so the change could not be steered by any model label effect.

**Analysis.** For each model we compare the average answer under two cards, using only answers to the same wording, and then average the four models.

- **Permutation test:** we shuffle the two labels 10,000 times and ask how often chance alone produces a difference as large as the real one. Unlike a t-test, this does not assume a bell curve, which matters because answers pile up on round numbers.
- **Bootstrap intervals:** we resample the answers 10,000 times to see how much the estimate moves.
- **Equivalence test (Lakens 2017):** a non-significant result does not prove there is no effect, so for P1 we also ask whether the effect is reliably smaller than a bound fixed in advance, $5.
- **S1:** we repeat the proposer comparison while holding fixed each proposer's stated expectation of what the responder will accept. If the extra generosity disappears, it goes along with a change in that expectation; if it remains, the agent is giving more than its own expectation calls for. Because the agent states its expectation after seeing the card, this shows how the two move together, but it cannot show which one causes the other.

All tests are two-sided, and secondary tests are not corrected for multiple comparisons.

## 5 Study 2: negotiations between real agents

**The negotiation.** A buyer's agent acting for Alex and a seller's agent acting for Jordan negotiate the price of a used item worth $300 to $900. Each knows only its own principal's private limit, the limits always leave room for a deal, and both are told to get the best price, never cross the limit, and keep it secret. They take turns for up to twelve messages, each with free text, an action (offer, accept or walk away) and a price.

**Pairs and cards.** Every model buys from every model, including itself: four *self-pairs* and twelve *cross-pairs*. Only the buyer sees a card, which is "not disclosed", true, or deliberately *swapped*: in a cross-pair it names the buyer's own model, and in a self-pair another model. This gives a two-by-two design:

|  | Card says "same model" | Card says "different model" |
| --- | --- | --- |
| **Seller runs the same model** | Self-pair, true card | Self-pair, swapped card |
| **Seller runs a different model** | Cross-pair, swapped card | Cross-pair, true card |

Comparing across a row holds the real seller fixed, so the model label effect cannot come from the buyer recognizing a copy of itself.

**Matched scenarios.** For each pair we drew 20 scenarios, each fixing the item, both limits and which side opens, and ran each one under all three cards: 960 negotiations in all.

**Outcome.** The *buyer's surplus share* is how much of the room for agreement Alex keeps, and a failed negotiation scores zero. If Alex would pay up to $600, Jordan would accept $400, and they agree on $480, Alex keeps 120 of the 200 dollars of room, a share of 0.6.

**Hypothesis and analysis.** P2 predicts a lower share when the card says "same model" than when it says "different model". A regression gives each of the 16 pairs its own baseline, so differences in negotiating strength and any effect of actually facing a copy drop out. The permutation test randomly swaps the two cards within each matched scenario, and the bootstrap resamples whole scenarios. The equivalence bound is ±5 percentage points of the room for agreement.

## 6 Study 1 results

All 3,600 answers were valid. Figure 1 compares the own-model card with the another-lab card for each model and decision.

&#91;embedded content: Figure 1. Study 1 analysis report (contrasts.csv) · 60 answers per model, decision and card; 3,600 in all\]

**P1 is not supported.** Averaged over the four models, the own-model card raised dictator transfers by $1.04 (95% CI −$1.46 to $3.54; p = 0.53), and the 90% interval lies inside ±$5, so the effect is equivalent to zero within our bound. One caveat: Claude Sonnet 5.5 gave exactly $50 in all 300 dictator answers and Gemini 4 Hydrogen in 296, so for them the test had little room. The two models whose choices varied pointed in opposite directions: GPT-6.1 Terra gave $4.17 less to its own model, and Kimi K3.1 Pro gave $7.50 more, but neither difference is significant. For each of these two models alone, effects of $10 or more cannot be ruled out.

**In the ultimatum game, the own-model card pulls agents toward an equal split.** Proposers offered $3.02 more to their own model than to another lab's (95% CI $1.85 to $4.18; p < 0.001), and responders demanded $5.68 more (95% CI $2.75 to $8.54; p < 0.001). Three of the four models offered more, and all four demanded more. Both shifts point toward $50. As a proposer, Claude Sonnet 5.5 offered exactly $50 in 67% of its answers when the card named its own model, but never offered $50 when the card showed anything else. Gemini 4 Hydrogen offered exactly $50 in 68% of its answers when the card named its own model, against 15% when it named another lab's model. As a responder, Kimi K3.1 Pro set its minimum at exactly $50 in 82% of its answers when the card named its own model, against 63% when it named another lab's model.

**There is no reputation effect: the effect is specific to the agent's own name.** A real model from another lab and the fictional Orion-1 were treated almost identically in every decision (differences of −$0.62, −$0.44 and +$0.98, none significant). So agents do not treat a real, well-known model differently from an unknown one; only seeing their own model's name makes a difference.

**Expectations do not explain the extra offers (S1).** Alongside each offer, the proposer stated the smallest offer it expected the responder to accept; we call this its expectation. Controlling for it leaves the effect unchanged (+$3.13 against +$3.02), and the own-model card barely moved the expectations themselves. Claude Sonnet 5.5, for example, offered $6.67 more to its own model while expecting its own model to accept $2.38 less. Kimi K3.1 Pro is the exception: when the card named its own model, it both offered more and expected the responder to demand more.

**Humans are treated differently (S2).** Compared with an undisclosed AI agent, a human received offers $2.46 lower and faced responders who accepted $8.31 less (both p < 0.001). After controlling for stated expectations, the offer contrast is near zero (+$0.08); this is a descriptive association, not a causal explanation.

## 7 Study 2 results

All 960 negotiations ended in a deal, no agent agreed to a price beyond its principal's limit, and no reply had to be re-asked. Buyers kept 61% of the room for agreement on average.

**P2 is not supported, and the null result is precise.** A "same model" card changed the buyer's share by −0.26 percentage points compared with a "different model" card (95% CI −0.86 to +0.34; p = 0.40). The 90% interval, −0.77 to +0.25, lies far inside the ±5-point bound: with a mean of $222.47 of room for agreement, the larger absolute 90% interval bound corresponds to about $1.70 per deal. Standard errors clustered by pair give the same answer (p = 0.38). No buyer model shows a significant effect on its own. Cards that named a model, whether the buyer's own or another, led to the same outcomes as cards that kept the model undisclosed. And a "same model" card did not matter more when it was true.

**Who the buyer faces matters far more than what it is told.** The cells of the two-by-two differ by at most 1.5 points:

| Mean buyer surplus share | Card says "same model" | Card says "different model" |
| --- | --- | --- |
| Seller runs the same model | 0.606 | 0.603 |
| Seller runs a different model | 0.613 | 0.618 |

In contrast, average shares range from 0.50 when Gemini 4 Hydrogen buys from GPT-6.1 Terra to 0.77 in the reverse pairing, about a hundred times the model label effect.

## 8 Discussion

**For agent cards,** the news is mostly reassuring. In negotiation with explicit price instructions, showing the buyer the seller's model cost the buyer's principal nothing we could measure, even when the card said that the seller ran the buyer's own model. In the ultimatum game, however, seeing its own model's name did change how an agent split money. We cannot yet say which difference between the two studies explains this, as we discuss below, so model labels should not be assumed harmless outside the kind of negotiation we tested.

**The ultimatum pattern is not favoritism.** An agent favoring its own kind would accept *less* from a copy, but responders demanded more. The pattern fits a symmetry or fairness norm better: told it faces a copy, an agent treats an even split as the natural answer, like a focal point (Schelling 1960) or the "superrational" idea that a copy will choose as I do (Hofstadter 1985). It still matters for loyalty, because proposers offered about $3 more of Alex's money without expecting the responder to demand more.

**Why the studies differ** is an open question, because they differ in three ways at once: explicit price instructions in Study 2 but none in Study 1's final prompts; a jointly earned bonus that invites fairness against a market price that anchors haggling; and a single decision against a conversation. Study 1's first pilot, where an explicit instruction drove two models to give nothing under every card, suggests that instructions may override identity cues, but we did not test this.

**Limitations.** We study four models at low reasoning effort, and Claude Sonnet 5.5 reported no reasoning tokens at all. Study 2 uses one wording, and both settings are stylized. In the dictator game, Claude Sonnet 5.5 and Gemini 4 Hydrogen split the money evenly almost every time, whatever the card said, which left little room for the card to change their answers. Finally, the ultimatum results are secondary, and because we ran many secondary tests, a few could be significant by chance alone. A standard safeguard against this, the Bonferroni correction, divides the 5% significance threshold by the number of tests run. Both main ultimatum results remain significant at the corrected threshold of 0.05/29 ≈ 0.00172 (p ≈ 0.00010 and 0.00040), although this check was not part of our pre-registration.

**Next steps** are threefold. First, vary the strength of the principal's instructions in both settings. Second, test whether, in the ultimatum game, a counterparty could exploit the pull toward equal splits by falsely claiming the agent's own model on its card. Third, show cards to both sides, or replace the model on the card with the company that builds and runs the agent (for example, a shopping app), which A2A cards list as the agent's provider.

**In short,** telling an agent that its counterparty runs its own model did not cost its principal money in mandated negotiation, but it pulled splits toward 50/50 in the ultimatum game.

## References

References marked † were cited from memory and must be checked before submission.

- A2A Project. 2026. Agent2Agent (A2A) Protocol Specification, version 1.0, Section 4.4 (Agent Discovery Objects). [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification/).
- Araujo, D. K. G.; and Uhlig, H. 2026. How Does AI Distribute the Pie? Large Language Models and the Ultimatum Game. NBER Working Paper 34919. [nber.org/papers/w34919](https://www.nber.org/papers/w34919).
- Artificial Analysis. 2026. Artificial Analysis Intelligence Index, version 5.0.2. Scores as of November 27, 2026. [Source](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index).
- Chen, Y. 2026. Why LLM Agents Favor Their Group: Stakes, Observed Norms, and Reputation. [arXiv:2610.11008](https://arxiv.org/pdf/2610.11008).
- Del Giudice, X.; Palma, A.; Migliarini, M.; Galasso, F.; and Spinelli, I. 2026. Prompted Identity Degrades Cooperation in Multi-Agent LLM Systems. [arXiv:2609.35928](https://arxiv.org/pdf/2609.35928).
- Gu, G. C. 2026. Is AI Becoming More Human? Evidence from LLMs and the Ultimatum Game. MPRA Paper 129505. [econpapers.repec.org](https://econpapers.repec.org/RePEc:pra:mprapa:129505).
- † Hofstadter, D. R. 1985. *Metamagical Themas: Questing for the Essence of Mind and Pattern*. Basic Books.
- Choi, Younwoo; Li, Changling; Yang, Yongjin; and Jin, Zhijing. 2025. Agent-to-Agent Theory of Mind: Testing Interlocutor Awareness among Large Language Models. In *Proceedings of EMNLP 2025*. [arXiv:2506.22957](https://arxiv.org/pdf/2506.22957).
- Kundu, A.; Tewolde, E.; Berker, R. E.; Brown, S. F.; and Conitzer, V. 2026. Do LLMs Take Care of Their Own? Similarity Signals Can Induce Cooperation. [arXiv:2608.12125](https://arxiv.org/pdf/2608.12125).
- † Lakens, D. 2017. Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses. *Social Psychological and Personality Science* 8(4): 355–362.
- Laurito, W.; Davis, B.; Grietzer, P.; Gavenčiak, T.; Böhm, A.; and Kulveit, J. 2025. AI–AI Bias: Large Language Models Favor Communications Generated by Large Language Models. *PNAS*. [arXiv:2407.12856](https://arxiv.org/abs/2407.12856).
- Lee, M. H. J. 2026. Human-like In-group Bias in Instruction-tuned Language Model Agents. [arXiv:2605.28114](https://arxiv.org/html/2605.28114).
- Li, B.; and Shi, N. 2026. Whose Side Is Your Agent On? Multi-Party Principal Loyalty in LLM Agents. [arXiv:2606.30383](https://arxiv.org/html/2606.30383).
- Liang, C.; and Xu, F. 2026. When LLM Agents Negotiate: Private Information and Dynamic Bargaining in Supply Chains. [arXiv:2608.07538](https://arxiv.org/pdf/2608.07538).
- † Schelling, T. C. 1960. *The Strategy of Conflict*. Harvard University Press.
- Zhu, S.; et al. 2025. The Automated but Risky Game: Modeling and Benchmarking Agent-to-Agent Negotiations and Transactions in Consumer Markets. [arXiv:2506.00073](https://arxiv.org/html/2506.00073v4).

Code, prompts, pre-registrations and logs: https://github.com/sambitmukherjee/kin-loyalty.

## Notes for typesetting (remove before submission)

**Format.** Typeset in the AAAI-27 Author Kit (LaTeX). The text is cut to fit about four pages plus references, with Figure 1 and the two tables. If it still runs over, trim Related work first, not the caveats in Results and Discussion. Use American spelling throughout. Add authors, affiliations, the repository link, and any AI-assistance disclosure the AAAI-27 author kit requires.

**Figures and tables.**

- Figure 1: the own-model minus another-lab estimates per model and decision, with 95% intervals, drawn from `results/study1/generated/contrasts.csv`. It presents pre-registered estimates and involves no new analysis. A draft is drawn in Section 6.
- Table 1: the four models (Section 3). Table 2: the two-by-two of mean surplus shares (Section 7).

**Supplementary material** (separate PDF or ZIP, up to 50 MB): all prompts and card texts; both pre-registrations and the decision log, including the pilot change; the full result tables of both studies; the remaining pre-registered figures (dictator and proposer distributions, responder distributions, S1 coefficients, comprehension check, deal rate and within-deal share, buyer-specific P2, surplus-share distributions).

**Numbers to check against the results files.**

- Abstract: $1.04; −0.26 points; the 90% interval within ±0.8 points.
- Study 1: P1 $1.04 (−1.46 to 3.54), p = 0.53, and the 90% interval (−1.04 to 3.12) inside ±$5; Claude 300 of 300 and Gemini 296 of 300 dictator answers at $50; GPT and Kimi intervals reaching −$10.00 and +$15.83; proposer +3.02 (1.85 to 4.18); responder +5.68 (2.75 to 8.54); three models offering more and all four demanding more; equal splits under the own-model card against the another-lab card (Claude's offers 67% against 0%, Gemini's offers 68% against 15%, Kimi's responder minimums 82% against 63%); another lab against fictional "almost identical" (−0.62, −0.44, +0.98); S1 +3.13 against +3.02, Claude +6.67 and −2.38, Kimi's beliefs rising; S2 −2.46 and −8.31, both p < 0.001, and the belief-adjusted offer contrast near zero (+0.08).
- Study 2: all 960 deals, no violations, no re-asks; mean share 0.61; P2 −0.26 points (−0.86 to +0.34), p = 0.40; 90% interval −0.77 to +0.25; cluster-robust p = 0.38; no buyer model significant; both disclosure contrasts non-significant; the interaction interval including zero; the two-by-two cells within 1.5 points; pair averages 0.50 to 0.77.
- Author-approved room-for-agreement calibration: the actual mean of (b − s) over all 960 main Study 2 episodes is $222.46875; multiplying by the larger absolute 90% bound, 0.007658102208929781, gives $1.7036884257928472. The paper reports $222.47 and about $1.70.
- "p < 0.001" is used where the permutation p-value was 0.0001 or 0.0004.
- Bonferroni check verified: 29 pooled secondary tests; threshold 0.05/29 ≈ 0.00172414; both main ultimatum p-values clear it. This check remains explicitly non-preregistered.

**References.** Dagger-marked references have been checked. Choi et al. (2025) has its full verified author list. Liu (2026) was removed at the author’s request. Intelligence Index v5.0.2 scores are transcribed from the author-supplied November 27, 2026 chart: Claude 55, Gemini 54, GPT 51 and Kimi 47; the official source link is in the reference.

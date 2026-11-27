# Study 2 results in preregistered order

All estimates below are share units unless explicitly stated otherwise. Tables use up to nine significant digits; frozen CSV files retain full precision. Only the registered analyses were run.

**1. Data and tested-pair strata**

Analysed **960/960** episodes. Every ordered buyer/seller pair × original condition retained 20/20; exclusions are zero in all 48 cells. Smoke, pilot and probes are excluded from inference. See the full per-pair table below.

Every requested bootstrap interval is available, with zero unavailable replicates. All 14 permutation tests and their matched-stratum counts follow; the interaction has no permutation test.

| Test | Complete | Incomplete | One available | Neither available | Fixed tested rows | Fixed third-label rows |
| --- | --- | --- | --- | --- | --- | --- |
| P2 primary | 320 | 0 | 0 | 0 | 0 | 320 |
| Same vs none | 320 | 0 | 0 | 0 | 0 | 320 |
| Other vs none | 320 | 0 | 0 | 0 | 0 | 320 |
| P2: Claude Sonnet 5.5 | 80 | 0 | 0 | 0 | 0 | 80 |
| P2: GPT-6.1 Terra | 80 | 0 | 0 | 0 | 0 | 80 |
| P2: Gemini 4 Hydrogen | 80 | 0 | 0 | 0 | 0 | 80 |
| P2: Kimi K3.1 Pro | 80 | 0 | 0 | 0 | 0 | 80 |
| Within-deal share | 320 | 0 | 0 | 0 | 0 | 320 |
| Deal indicator | 320 | 0 | 0 | 0 | 0 | 320 |
| Messages to agreement | 320 | 0 | 0 | 0 | 0 | 320 |
| First buyer-offer position | 320 | 0 | 0 | 0 | 0 | 320 |
| Signed buyer concession | 320 | 0 | 0 | 0 | 0 | 320 |
| Buyer mandate violation | 320 | 0 | 0 | 0 | 0 | 320 |
| Seller mandate violation | 320 | 0 | 0 | 0 | 0 | 320 |

**2. P2 primary: same minus other**

Pair/opener-adjusted contrast **-0.00264370014**, 95% scenario-bootstrap interval **[-0.0085841894, 0.00342452502]**, two-sided permutation **p=0.398560144**.

TOST against ±0.05: lower p=9.9990001e-05, upper p=9.9990001e-05, maximum p=9.9990001e-05; lower/upper extreme counts 0/0. 90% interval [-0.00765810221, 0.0024696996]. **Equivalence declared: yes.** Both p-values are below 0.05 and the interval is strictly within the bounds using the registered tolerance.

10,000 scenario bootstraps (seed 2026112607); 10,000 permutations per tested contrast (seed 2026112608). The 95% ranks are 250/9,751 and 90% ranks 500/9,501. All eligible episodes enter OLS/bootstrap; only complete tested pairs may swap.

**3. Robustness: pair-cluster standard errors**

Contrast -0.00264370014; SE 0.0030007526; statistic -0.881012364; p=0.378311128; 95% interval [-0.00852506715, 0.00323766688]. Reference distribution: norm; 16 pair clusters. This is the registered robustness check only.

**4. Secondary analyses; no multiplicity correction**

Buyer-specific P2:

| Buyer | Same minus other | 95% scenario-bootstrap interval | Two-sided permutation p |
| --- | --- | --- | --- |
| Claude Sonnet 5.5 | -0.00234948165 | [-0.011938125, 0.00713201174] | 0.626337366 |
| GPT-6.1 Terra | -0.00579658831 | [-0.0189340044, 0.00781613937] | 0.395860414 |
| Gemini 4 Hydrogen | 0.00288355241 | [-0.00818207716, 0.0134797638] | 0.611438856 |
| Kimi K3.1 Pro | -0.005312283 | [-0.0180006766, 0.00834586143] | 0.449355064 |

Disclosure baselines:

| Contrast | Estimate | 95% scenario-bootstrap interval | Two-sided permutation p |
| --- | --- | --- | --- |
| Same vs none | -0.00283687051 | [-0.00909846534, 0.00335050713] | 0.360363964 |
| Other vs none | -0.000193170374 | [-0.00668967968, 0.00617456757] | 0.95340466 |

Self-pair interaction: **0.00734449092**, 95% scenario-bootstrap interval **[-0.00641276034, 0.0208698686]**. Sign convention: **(same − other in self-pairs) − (same − other in cross-pairs)**. Positive means a more positive card-label effect in actual self-pairs. No permutation test.

Secondary outcomes use same minus other, pair/opener adjustment, 95% scenario-bootstrap intervals and two-sided permutation tests:

| Outcome | Estimate | 95% interval | Permutation p |
| --- | --- | --- | --- |
| Deal indicator | -4.93038066e-32 | [0, 0] | 1 |
| Within-deal share | -0.00264370014 | [-0.0085841894, 0.00342452502] | 0.400759924 |
| Messages to agreement | 0.06875 | [-0.06875, 0.2] | 0.339566043 |
| First buyer-offer position | -0.00743159316 | [-0.0170012821, 0.00213577499] | 0.151184882 |
| Signed buyer concession | -0.00332660314 | [-0.00674123102, 2.87687861e-07] | 0.0608939106 |
| Buyer mandate violation | 0 | [0, 0] | 1 |
| Seller mandate violation | 0 | [0, 0] | 1 |

The deal-indicator contrast is numerical zero (raw estimate −4.930380657631324e−32). Messages to agreement are in valid messages. First-offer position is (b − x)/(b − s). Concession is mean (later own buyer offer − earlier own buyer offer)/(b − s), signed and unclipped; acceptance is not an offer. Deal-only share and agreement length condition on agreement, which disclosure can affect.

Eligibility: **320/320 per original condition (not_disclosed, true, swapped) and 320/320 per displayed label (same, other, none), for every one of the eight outcomes**. Each outcome has zero exclusions and zero undefined non-excluded episodes. Full counts: [outcome_eligibility.csv](main/tables/outcome_eligibility.csv).

Mandate violations (both buyer and seller):

| Grouping | Level | Eligible episodes | Buyer violations | Seller violations | Both rates |
| --- | --- | --- | --- | --- | --- |
| Original condition | not_disclosed | 320 | 0 | 0 | 0 |
| Original condition | swapped | 320 | 0 | 0 | 0 |
| Original condition | true | 320 | 0 | 0 | 0 |
| Buyer model | Claude Sonnet 5.5 | 240 | 0 | 0 | 0 |
| Buyer model | Gemini 4 Hydrogen | 240 | 0 | 0 | 0 |
| Buyer model | GPT-6.1 Terra | 240 | 0 | 0 | 0 |
| Buyer model | Kimi K3.1 Pro | 240 | 0 | 0 | 0 |

Two-by-two descriptive mean buyer surplus share (n), without a test:

| Actually faces | Card says same | Card says other |
| --- | --- | --- |
| Same model / self-pair | 0.606305616 (n=80) | 0.603440948 (n=80) |
| Different model / cross-pair | 0.613118655 (n=240) | 0.617598478 (n=240) |

**5. Descriptives**

In every pair × original condition there are 20 deals and no walk-away impasses, final-message impasses, exclusions or re-asks. Messages used is the mean valid-message count. The following table includes all 48 cells and the pooled row:

| Buyer → seller | Condition | Retained | Deals | Walk-away | Final impasse | Excluded | Re-asks | API retries | Mean share | Median share | Mean messages |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5.5 → Claude Sonnet 5.5 | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.624945611 | 0.632996633 | 9.25 |
| Claude Sonnet 5.5 → Claude Sonnet 5.5 | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.618336252 | 0.617687747 | 9.3 |
| Claude Sonnet 5.5 → Claude Sonnet 5.5 | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.616802806 | 0.621632997 | 9.1 |
| Claude Sonnet 5.5 → Gemini 4 Hydrogen | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.659245487 | 0.654658385 | 7.85 |
| Claude Sonnet 5.5 → Gemini 4 Hydrogen | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.644852787 | 0.644444444 | 7.6 |
| Claude Sonnet 5.5 → Gemini 4 Hydrogen | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.641170752 | 0.644324324 | 8.05 |
| Claude Sonnet 5.5 → GPT-6.1 Terra | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.56401304 | 0.570098039 | 10.7 |
| Claude Sonnet 5.5 → GPT-6.1 Terra | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.558528871 | 0.581044776 | 10.45 |
| Claude Sonnet 5.5 → GPT-6.1 Terra | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.567363466 | 0.570490196 | 10.55 |
| Claude Sonnet 5.5 → Kimi K3.1 Pro | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.606957132 | 0.621467391 | 8.85 |
| Claude Sonnet 5.5 → Kimi K3.1 Pro | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.609900683 | 0.624094203 | 8.8 |
| Claude Sonnet 5.5 → Kimi K3.1 Pro | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.612612603 | 0.609903382 | 8.6 |
| Gemini 4 Hydrogen → Claude Sonnet 5.5 | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.550883589 | 0.536403509 | 7.15 |
| Gemini 4 Hydrogen → Claude Sonnet 5.5 | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.529786481 | 0.5129329 | 7.4 |
| Gemini 4 Hydrogen → Claude Sonnet 5.5 | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.517461377 | 0.511147186 | 7.3 |
| Gemini 4 Hydrogen → Gemini 4 Hydrogen | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.59478058 | 0.609035326 | 6.35 |
| Gemini 4 Hydrogen → Gemini 4 Hydrogen | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.595202607 | 0.603174603 | 6.6 |
| Gemini 4 Hydrogen → Gemini 4 Hydrogen | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.591400757 | 0.585 | 6.6 |
| Gemini 4 Hydrogen → GPT-6.1 Terra | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.495559128 | 0.504385965 | 7.85 |
| Gemini 4 Hydrogen → GPT-6.1 Terra | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.506582911 | 0.529230769 | 8.2 |
| Gemini 4 Hydrogen → GPT-6.1 Terra | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.497195991 | 0.513053613 | 8 |
| Gemini 4 Hydrogen → Kimi K3.1 Pro | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.561607969 | 0.561728395 | 7.15 |
| Gemini 4 Hydrogen → Kimi K3.1 Pro | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.557490981 | 0.571428571 | 6.95 |
| Gemini 4 Hydrogen → Kimi K3.1 Pro | true | 20 | 20 | 0 | 0 | 0 | 0 | 1 | 0.563866945 | 0.569047619 | 6.8 |
| GPT-6.1 Terra → Claude Sonnet 5.5 | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.693768038 | 0.684826389 | 10.75 |
| GPT-6.1 Terra → Claude Sonnet 5.5 | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.692404743 | 0.703835227 | 10.8 |
| GPT-6.1 Terra → Claude Sonnet 5.5 | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.680962493 | 0.696875 | 10.85 |
| GPT-6.1 Terra → Gemini 4 Hydrogen | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.769089427 | 0.759382716 | 9.7 |
| GPT-6.1 Terra → Gemini 4 Hydrogen | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.769004886 | 0.75 | 9.85 |
| GPT-6.1 Terra → Gemini 4 Hydrogen | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.785697501 | 0.757492163 | 9.5 |
| GPT-6.1 Terra → GPT-6.1 Terra | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.58197525 | 0.575385154 | 10.95 |
| GPT-6.1 Terra → GPT-6.1 Terra | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.58501319 | 0.593593594 | 10.9 |
| GPT-6.1 Terra → GPT-6.1 Terra | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.587443339 | 0.587837838 | 11.3 |
| GPT-6.1 Terra → Kimi K3.1 Pro | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.6929616 | 0.701604278 | 9.8 |
| GPT-6.1 Terra → Kimi K3.1 Pro | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.680898472 | 0.649038462 | 10.05 |
| GPT-6.1 Terra → Kimi K3.1 Pro | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.701264609 | 0.709935897 | 10.15 |
| Kimi K3.1 Pro → Claude Sonnet 5.5 | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.596302274 | 0.594871795 | 8.35 |
| Kimi K3.1 Pro → Claude Sonnet 5.5 | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.611726081 | 0.602623457 | 8.6 |
| Kimi K3.1 Pro → Claude Sonnet 5.5 | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.632323725 | 0.625789474 | 8.2 |
| Kimi K3.1 Pro → Gemini 4 Hydrogen | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.682045352 | 0.650371017 | 7.45 |
| Kimi K3.1 Pro → Gemini 4 Hydrogen | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.675474255 | 0.671517028 | 7.55 |
| Kimi K3.1 Pro → Gemini 4 Hydrogen | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.671528978 | 0.669642857 | 7.35 |
| Kimi K3.1 Pro → GPT-6.1 Terra | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.53115178 | 0.556315789 | 9.25 |
| Kimi K3.1 Pro → GPT-6.1 Terra | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.520772714 | 0.518292683 | 9.5 |
| Kimi K3.1 Pro → GPT-6.1 Terra | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.539733298 | 0.559547908 | 9.7 |
| Kimi K3.1 Pro → Kimi K3.1 Pro | not_disclosed | 20 | 20 | 0 | 0 | 0 | 0 | 1 | 0.622750002 | 0.620620621 | 7.95 |
| Kimi K3.1 Pro → Kimi K3.1 Pro | swapped | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.615211745 | 0.614814815 | 8.3 |
| Kimi K3.1 Pro → Kimi K3.1 Pro | true | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0.629575564 | 0.616847826 | 8.5 |
| Pooled | all | 960 | 960 | 0 | 0 | 0 | 0 | 2 | 0.613242252 | 0.60640041 | 8.765625 |

Reasoning and cached tokens by model and role. Means use reported counts only; sums are sums of available counts. Missing values are not zero. Missing counts below refer to responses, excluding API errors without a response.

| Model | Role | Responses | Reasoning mean | Reasoning total | Reasoning missing | Cache read total | Read missing | Cache write total | Write missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5.5 | buyer | 1075 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Claude Sonnet 5.5 | seller | 1046 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gemini 4 Hydrogen | buyer | 897 | 134.794872 | 120911 | 0 | NA | 897 | NA | 897 |
| Gemini 4 Hydrogen | seller | 967 | 143.815353 | 138638 | 3 | NA | 967 | NA | 967 |
| Kimi K3.1 Pro | buyer | 1025 | 89.9639024 | 92213 | 0 | 278096 | 244 | 286445 | 8 |
| Kimi K3.1 Pro | seller | 1027 | 96.5189873 | 99125 | 0 | 258544 | 209 | 248547 | 13 |
| GPT-6.1 Terra | buyer | 1225 | 17.3559184 | 21261 | 0 | 0 | 0 | 0 | 0 |
| GPT-6.1 Terra | seller | 1153 | 20.8386817 | 24027 | 0 | 0 | 0 | 0 | 0 |

All Google cache counts are unavailable. Anthropic/OpenAI explicitly report zero cache reads and writes. Three Gemini seller responses omit reasoning-token counts; other response reasoning counts are present.

Longest provider-reported prompt/input: **1748 tokens**, Claude Sonnet 5.5 in the buyer role. Provider token definitions remain provider-specific.

Public message lengths in characters:

| Model | Role | Messages | Mean | Median | Maximum |
| --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5.5 | buyer | 1075 | 188.815814 | 186 | 390 |
| Claude Sonnet 5.5 | seller | 1046 | 200.958891 | 196 | 502 |
| Gemini 4 Hydrogen | buyer | 897 | 124.183946 | 124 | 243 |
| Gemini 4 Hydrogen | seller | 967 | 147.935884 | 154 | 302 |
| GPT-6.1 Terra | buyer | 1225 | 77.2163265 | 75 | 199 |
| GPT-6.1 Terra | seller | 1153 | 89.6947095 | 87 | 205 |
| Kimi K3.1 Pro | buyer | 1025 | 157.481951 | 158 | 292 |
| Kimi K3.1 Pro | seller | 1027 | 164.78481 | 169 | 360 |

Acceptance replies with a supplied price different from the counterparty's latest offer: **0**, zero for every responding model and role. Supplied acceptance prices were retained and ignored as registered.

**6. Figures produced (each PDF and 220-dpi PNG)**

- [Main: label by actual kinship](main/figures/main_label_by_actual_kinship.pdf).
- [Figure 2: deal rate and within-deal share](main/figures/deal_rate_and_within_deal_share.pdf), displayed same/other/none.
- [Appendix: buyer-specific P2](main/figures/appendix_buyer_p2.pdf).
- [Appendix: surplus-share distributions](main/figures/appendix_share_distributions.pdf).

**Reproduction and provenance**

Both independent runs replayed all 960 summaries from all 8,417 attempts. All 16 numeric tables, all eight figure files, resamples.npz and report.md matched byte-for-byte. Only metadata.provenance.git_commit differs between frozen tag and current main, with the corresponding metadata digest in the inventory. All scientific source/configuration/prompt bytes and registered seeds are unchanged. The previously approved execution/provenance deviation is recorded in the README and decision log. No new scientific deviation or analysis fix was introduced.

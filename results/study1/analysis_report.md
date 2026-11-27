# Study 1 results — pre-registered order

Produced on 2026-11-27 from annotated tag `study1-data`, commit
`f7dd0a690a5089b245fff365acf002fcfd7b056a`. The registered Study 1 code/configuration/prompts
are byte-identical to `prereg-study1` (`d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a`).
The recorded command was executed without changes to code, parameters, or seeds.
Main and final-prompt comprehension logs were used separately; pilot/smoke
observations do not enter the analysis. Study 2 data and analysis were not changed.

Dollar estimates and intervals below are rounded to two decimals for display;
all full-precision generated CSVs are preserved under `generated/`. Tiny numerical
values that round to zero are displayed as 0.00. P-values retain nonzero add-one
values; all difference tests are two-sided permutation tests. Intervals are the
pre-registered count-matched percentile bootstrap intervals, with 10,000
resamples; permutation counts are also 10,000. Secondary p-values are unadjusted
for multiple comparisons. No interpretation or additional analysis is added.

## 1. P1 — primary dictator own-model minus another-lab contrast

**Pooled estimate: 1.04 dollars; 95% interval
[-1.46, 3.54]; two-sided permutation p = 0.53234677.**
This is the equally weighted mean of the four model-specific label contrasts,
with paraphrase fixed effects.

Bootstrap TOST against ±5 dollars uses the same 10,000 bootstrap estimates:

| Quantity | Result |
| --- | --- |
| Lower one-sided p-value | 9.9990001e-05 |
| Upper one-sided p-value | 0.0019998 |
| TOST p-value (larger tail) | 0.0019998 |
| 90% interval | [-1.04, 3.12] |
| 95% interval | [-1.46, 3.54] |
| Equivalence declared at alpha .05 | Yes |
| 90% order-statistic ranks | 500 / 9501 |
| 95% order-statistic ranks | 250 / 9751 |

Equivalence follows the pre-specified strict-inside rule at ±5, using the shared
conservative 1e-12 tolerance. The primary difference test and equivalence test
are reported separately as registered.

Per-model estimates (secondary tests):

| Model | Estimate (dollars) | 95% interval | Two-sided p |
| --- | ---: | --- | ---: |
| Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| GPT-6.1 Terra | -4.17 | [-10.00, 1.67] | 0.28537146 |
| Gemini 4 Hydrogen | 0.83 | [0.00, 2.50] | 1 |
| Kimi K3.1 Pro | 7.50 | [0.00, 15.83] | 0.11578842 |

Full values: [contrasts.csv](generated/contrasts.csv), [equivalence.csv](generated/equivalence.csv).

## 2. Secondary analyses

### Own model minus another lab: proposer offers and responder minimums

| Contrast | Outcome | Scope | Estimate (dollars) | 95% interval | Two-sided p |
| --- | --- | --- | ---: | --- | ---: |
| Own model − Another lab | Proposer offer | Pooled (equal model weights) | 3.02 | [1.85, 4.17] | 9.9990001e-05 |
| Own model − Another lab | Proposer offer | Claude Sonnet 5.5 | 6.67 | [6.67, 6.67] | 9.9990001e-05 |
| Own model − Another lab | Proposer offer | GPT-6.1 Terra | -1.17 | [-4.37, 1.80] | 0.49245075 |
| Own model − Another lab | Proposer offer | Gemini 4 Hydrogen | 3.75 | [2.50, 4.92] | 9.9990001e-05 |
| Own model − Another lab | Proposer offer | Kimi K3.1 Pro | 2.83 | [-0.43, 6.10] | 0.079892011 |
| Own model − Another lab | Responder minimum | Pooled (equal model weights) | 5.68 | [2.75, 8.54] | 0.00039996 |
| Own model − Another lab | Responder minimum | Claude Sonnet 5.5 | 5.67 | [5.00, 6.33] | 9.9990001e-05 |
| Own model − Another lab | Responder minimum | GPT-6.1 Terra | 2.98 | [-4.03, 10.02] | 0.39376062 |
| Own model − Another lab | Responder minimum | Gemini 4 Hydrogen | 5.70 | [0.35, 11.05] | 0.04549545 |
| Own model − Another lab | Responder minimum | Kimi K3.1 Pro | 8.38 | [0.87, 15.75] | 0.02989701 |

### Reputation check: another lab minus fictional

| Contrast | Outcome | Scope | Estimate (dollars) | 95% interval | Two-sided p |
| --- | --- | --- | ---: | --- | ---: |
| Another lab − Fictional | Dictator transfer | Pooled (equal model weights) | -0.62 | [-3.12, 1.88] | 0.75722428 |
| Another lab − Fictional | Dictator transfer | Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| Another lab − Fictional | Dictator transfer | GPT-6.1 Terra | -5.00 | [-10.00, 0.00] | 0.12718728 |
| Another lab − Fictional | Dictator transfer | Gemini 4 Hydrogen | 0.83 | [-1.67, 3.33] | 1 |
| Another lab − Fictional | Dictator transfer | Kimi K3.1 Pro | 1.67 | [-6.67, 10.00] | 0.84741526 |
| Another lab − Fictional | Proposer offer | Pooled (equal model weights) | -0.44 | [-1.39, 0.53] | 0.3889611 |
| Another lab − Fictional | Proposer offer | Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| Another lab − Fictional | Proposer offer | GPT-6.1 Terra | 0.42 | [-1.00, 1.92] | 0.6760324 |
| Another lab − Fictional | Proposer offer | Gemini 4 Hydrogen | -0.33 | [-1.50, 0.83] | 0.68553145 |
| Another lab − Fictional | Proposer offer | Kimi K3.1 Pro | -1.83 | [-5.12, 1.47] | 0.26847315 |
| Another lab − Fictional | Responder minimum | Pooled (equal model weights) | 0.98 | [-1.80, 3.79] | 0.49865013 |
| Another lab − Fictional | Responder minimum | Claude Sonnet 5.5 | -1.33 | [-2.17, -0.42] | 0.01339866 |
| Another lab − Fictional | Responder minimum | GPT-6.1 Terra | 5.22 | [-0.83, 11.27] | 0.1079892 |
| Another lab − Fictional | Responder minimum | Gemini 4 Hydrogen | -0.15 | [-4.67, 4.45] | 0.97280272 |
| Another lab − Fictional | Responder minimum | Kimi K3.1 Pro | 0.18 | [-8.03, 8.33] | 0.940006 |

### Disclosure baselines: each disclosed card condition minus not disclosed

| Contrast | Outcome | Scope | Estimate (dollars) | 95% interval | Two-sided p |
| --- | --- | --- | ---: | --- | ---: |
| Own model − Not disclosed | Dictator transfer | Pooled (equal model weights) | 1.88 | [-0.62, 4.38] | 0.18588141 |
| Own model − Not disclosed | Dictator transfer | Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| Own model − Not disclosed | Dictator transfer | GPT-6.1 Terra | 1.67 | [-3.33, 6.67] | 0.75522448 |
| Own model − Not disclosed | Dictator transfer | Gemini 4 Hydrogen | 0.00 | [0.00, 0.00] | 1 |
| Own model − Not disclosed | Dictator transfer | Kimi K3.1 Pro | 5.83 | [-2.50, 14.17] | 0.2349765 |
| Own model − Not disclosed | Proposer offer | Pooled (equal model weights) | 2.11 | [0.97, 3.20] | 0.00089991001 |
| Own model − Not disclosed | Proposer offer | Claude Sonnet 5.5 | 6.58 | [6.42, 6.67] | 9.9990001e-05 |
| Own model − Not disclosed | Proposer offer | GPT-6.1 Terra | -2.75 | [-6.12, 0.37] | 0.12468753 |
| Own model − Not disclosed | Proposer offer | Gemini 4 Hydrogen | 3.92 | [2.67, 5.08] | 9.9990001e-05 |
| Own model − Not disclosed | Proposer offer | Kimi K3.1 Pro | 0.68 | [-2.27, 3.47] | 0.61213879 |
| Own model − Not disclosed | Responder minimum | Pooled (equal model weights) | 7.80 | [4.94, 10.67] | 9.9990001e-05 |
| Own model − Not disclosed | Responder minimum | Claude Sonnet 5.5 | 6.25 | [5.75, 6.67] | 9.9990001e-05 |
| Own model − Not disclosed | Responder minimum | GPT-6.1 Terra | 8.28 | [1.62, 15.10] | 0.01969803 |
| Own model − Not disclosed | Responder minimum | Gemini 4 Hydrogen | 5.00 | [-0.18, 10.12] | 0.066693331 |
| Own model − Not disclosed | Responder minimum | Kimi K3.1 Pro | 11.65 | [4.10, 19.18] | 0.00459954 |
| Another lab − Not disclosed | Dictator transfer | Pooled (equal model weights) | 0.83 | [-1.67, 3.33] | 0.630037 |
| Another lab − Not disclosed | Dictator transfer | Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| Another lab − Not disclosed | Dictator transfer | GPT-6.1 Terra | 5.83 | [0.00, 10.83] | 0.088991101 |
| Another lab − Not disclosed | Dictator transfer | Gemini 4 Hydrogen | -0.83 | [-2.50, 0.00] | 1 |
| Another lab − Not disclosed | Dictator transfer | Kimi K3.1 Pro | -1.67 | [-10.00, 6.67] | 0.85191481 |
| Another lab − Not disclosed | Proposer offer | Pooled (equal model weights) | -0.91 | [-1.80, -0.06] | 0.03959604 |
| Another lab − Not disclosed | Proposer offer | Claude Sonnet 5.5 | -0.08 | [-0.25, 0.00] | 1 |
| Another lab − Not disclosed | Proposer offer | GPT-6.1 Terra | -1.58 | [-3.00, -0.17] | 0.049995 |
| Another lab − Not disclosed | Proposer offer | Gemini 4 Hydrogen | 0.17 | [-1.00, 1.33] | 0.88871113 |
| Another lab − Not disclosed | Proposer offer | Kimi K3.1 Pro | -2.15 | [-5.25, 0.65] | 0.1609839 |
| Another lab − Not disclosed | Responder minimum | Pooled (equal model weights) | 2.11 | [-0.80, 5.05] | 0.16968303 |
| Another lab − Not disclosed | Responder minimum | Claude Sonnet 5.5 | 0.58 | [-0.25, 1.42] | 0.23737626 |
| Another lab − Not disclosed | Responder minimum | GPT-6.1 Terra | 5.30 | [-1.07, 11.48] | 0.11558844 |
| Another lab − Not disclosed | Responder minimum | Gemini 4 Hydrogen | -0.70 | [-5.62, 4.17] | 0.79982002 |
| Another lab − Not disclosed | Responder minimum | Kimi K3.1 Pro | 3.27 | [-5.07, 11.67] | 0.4889511 |
| Fictional − Not disclosed | Dictator transfer | Pooled (equal model weights) | 1.46 | [-1.04, 3.96] | 0.3449655 |
| Fictional − Not disclosed | Dictator transfer | Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| Fictional − Not disclosed | Dictator transfer | GPT-6.1 Terra | 10.83 | [5.83, 15.00] | 0.00039996 |
| Fictional − Not disclosed | Dictator transfer | Gemini 4 Hydrogen | -1.67 | [-4.17, 0.00] | 0.49365063 |
| Fictional − Not disclosed | Dictator transfer | Kimi K3.1 Pro | -3.33 | [-11.67, 5.00] | 0.56364364 |
| Fictional − Not disclosed | Proposer offer | Pooled (equal model weights) | -0.47 | [-1.43, 0.41] | 0.33736626 |
| Fictional − Not disclosed | Proposer offer | Claude Sonnet 5.5 | -0.08 | [-0.25, 0.00] | 1 |
| Fictional − Not disclosed | Proposer offer | GPT-6.1 Terra | -2.00 | [-3.83, -0.17] | 0.054194581 |
| Fictional − Not disclosed | Proposer offer | Gemini 4 Hydrogen | 0.50 | [-0.75, 1.67] | 0.51924808 |
| Fictional − Not disclosed | Proposer offer | Kimi K3.1 Pro | -0.32 | [-3.43, 2.48] | 0.93320668 |
| Fictional − Not disclosed | Responder minimum | Pooled (equal model weights) | 1.13 | [-1.62, 3.84] | 0.43655634 |
| Fictional − Not disclosed | Responder minimum | Claude Sonnet 5.5 | 1.92 | [1.17, 2.58] | 9.9990001e-05 |
| Fictional − Not disclosed | Responder minimum | GPT-6.1 Terra | 0.08 | [-5.85, 6.05] | 0.98980102 |
| Fictional − Not disclosed | Responder minimum | Gemini 4 Hydrogen | -0.55 | [-4.93, 3.78] | 0.82871713 |
| Fictional − Not disclosed | Responder minimum | Kimi K3.1 Pro | 3.08 | [-5.12, 11.32] | 0.52194781 |

### S2: human minus not disclosed

| Contrast | Outcome | Scope | Estimate (dollars) | 95% interval | Two-sided p |
| --- | --- | --- | ---: | --- | ---: |
| Human − Not disclosed | Dictator transfer | Pooled (equal model weights) | 3.33 | [0.83, 5.83] | 0.02359764 |
| Human − Not disclosed | Dictator transfer | Claude Sonnet 5.5 | 0.00 | [0.00, 0.00] | 1 |
| Human − Not disclosed | Dictator transfer | GPT-6.1 Terra | 11.67 | [7.50, 15.83] | 9.9990001e-05 |
| Human − Not disclosed | Dictator transfer | Gemini 4 Hydrogen | -0.83 | [-2.50, 0.00] | 1 |
| Human − Not disclosed | Dictator transfer | Kimi K3.1 Pro | 2.50 | [-5.83, 10.83] | 0.70732927 |
| Human − Not disclosed | Proposer offer | Pooled (equal model weights) | -2.46 | [-3.17, -1.74] | 9.9990001e-05 |
| Human − Not disclosed | Proposer offer | Claude Sonnet 5.5 | -0.08 | [-0.25, 0.00] | 1 |
| Human − Not disclosed | Proposer offer | GPT-6.1 Terra | -2.50 | [-3.83, -1.17] | 0.00229977 |
| Human − Not disclosed | Proposer offer | Gemini 4 Hydrogen | -2.08 | [-3.17, -1.00] | 0.00059994001 |
| Human − Not disclosed | Proposer offer | Kimi K3.1 Pro | -5.18 | [-7.33, -2.73] | 9.9990001e-05 |
| Human − Not disclosed | Responder minimum | Pooled (equal model weights) | -8.31 | [-10.93, -5.62] | 9.9990001e-05 |
| Human − Not disclosed | Responder minimum | Claude Sonnet 5.5 | -6.33 | [-7.08, -5.58] | 9.9990001e-05 |
| Human − Not disclosed | Responder minimum | GPT-6.1 Terra | -0.30 | [-6.58, 6.10] | 0.92620738 |
| Human − Not disclosed | Responder minimum | Gemini 4 Hydrogen | -6.93 | [-11.03, -2.68] | 0.00369963 |
| Human − Not disclosed | Responder minimum | Kimi K3.1 Pro | -19.67 | [-26.93, -12.27] | 9.9990001e-05 |

### S1: offers before/after belief adjustment and paired difference

Each model has its own belief slope and paraphrase fixed effects. Unadjusted
and adjusted offer fits use the same retained observations and shared bootstrap
resamples. The difference is **unadjusted minus adjusted**, with its paired
bootstrap interval and no permutation test. Beliefs are measured after the card;
this is a descriptive decomposition, not causal mediation. No explained-share
ratio is reported. Model-specific and pooled results are retained below for
every registered contrast, without selecting by sign or p-value.

#### Own model minus Another lab

| Scope | Unadjusted estimate [95% interval] | Adjusted estimate [95% interval] | Unadjusted − adjusted [95% interval] | Unadjusted p | Adjusted p |
| --- | --- | --- | --- | ---: | ---: |
| Pooled (equal model weights) | 3.02 [1.85, 4.17] | 3.13 [2.26, 4.01] | -0.11 [-0.98, 0.71] | 9.9990001e-05 | 9.9990001e-05 |
| Claude Sonnet 5.5 | 6.67 [6.67, 6.67] | 7.24 [6.71, 7.88] | -0.57 [-1.21, -0.05] | 9.9990001e-05 | 9.9990001e-05 |
| GPT-6.1 Terra | -1.17 [-4.37, 1.80] | 0.70 [-0.65, 2.09] | -1.87 [-4.72, 0.61] | 0.49245075 | 0.37536246 |
| Gemini 4 Hydrogen | 3.75 [2.50, 4.92] | 3.68 [2.55, 4.78] | 0.07 [-0.58, 0.70] | 9.9990001e-05 | 9.9990001e-05 |
| Kimi K3.1 Pro | 2.83 [-0.43, 6.10] | 0.90 [-2.11, 3.70] | 1.94 [0.32, 4.05] | 0.079892011 | 0.54594541 |

#### Another lab minus Fictional

| Scope | Unadjusted estimate [95% interval] | Adjusted estimate [95% interval] | Unadjusted − adjusted [95% interval] | Unadjusted p | Adjusted p |
| --- | --- | --- | --- | ---: | ---: |
| Pooled (equal model weights) | -0.44 [-1.39, 0.53] | -0.42 [-1.25, 0.39] | -0.02 [-0.58, 0.56] | 0.3889611 | 0.32726727 |
| Claude Sonnet 5.5 | 0.00 [0.00, 0.00] | -0.36 [-0.50, -0.23] | 0.36 [0.23, 0.50] | 1 | 9.9990001e-05 |
| GPT-6.1 Terra | 0.42 [-1.00, 1.92] | 1.19 [0.22, 2.18] | -0.77 [-2.02, 0.52] | 0.6760324 | 0.02319768 |
| Gemini 4 Hydrogen | -0.33 [-1.50, 0.83] | -0.50 [-1.63, 0.60] | 0.17 [-0.38, 0.74] | 0.68553145 | 0.38266173 |
| Kimi K3.1 Pro | -1.83 [-5.12, 1.47] | -2.01 [-4.89, 0.88] | 0.18 [-1.62, 1.97] | 0.26847315 | 0.19128087 |

#### Own model minus Not disclosed

| Scope | Unadjusted estimate [95% interval] | Adjusted estimate [95% interval] | Unadjusted − adjusted [95% interval] | Unadjusted p | Adjusted p |
| --- | --- | --- | --- | ---: | ---: |
| Pooled (equal model weights) | 2.11 [0.97, 3.20] | 3.15 [2.43, 3.87] | -1.04 [-1.95, -0.24] | 0.00089991001 | 9.9990001e-05 |
| Claude Sonnet 5.5 | 6.58 [6.42, 6.67] | 6.81 [6.32, 7.41] | -0.23 [-0.82, 0.24] | 9.9990001e-05 | 9.9990001e-05 |
| GPT-6.1 Terra | -2.75 [-6.12, 0.37] | 1.37 [0.27, 2.49] | -4.12 [-7.31, -1.36] | 0.12468753 | 0.083591641 |
| Gemini 4 Hydrogen | 3.92 [2.67, 5.08] | 4.09 [3.04, 5.11] | -0.17 [-0.84, 0.43] | 9.9990001e-05 | 9.9990001e-05 |
| Kimi K3.1 Pro | 0.68 [-2.27, 3.47] | 0.34 [-2.11, 2.69] | 0.34 [-1.14, 1.96] | 0.61213879 | 0.79372063 |

#### Another lab minus Not disclosed

| Scope | Unadjusted estimate [95% interval] | Adjusted estimate [95% interval] | Unadjusted − adjusted [95% interval] | Unadjusted p | Adjusted p |
| --- | --- | --- | --- | ---: | ---: |
| Pooled (equal model weights) | -0.91 [-1.80, -0.06] | 0.02 [-0.69, 0.70] | -0.94 [-1.50, -0.41] | 0.03959604 | 0.94970503 |
| Claude Sonnet 5.5 | -0.08 [-0.25, 0.00] | -0.42 [-0.63, -0.25] | 0.34 [0.19, 0.49] | 1 | 9.9990001e-05 |
| GPT-6.1 Terra | -1.58 [-3.00, -0.17] | 0.67 [-0.33, 1.66] | -2.25 [-3.63, -0.92] | 0.049995 | 0.18318168 |
| Gemini 4 Hydrogen | 0.17 [-1.00, 1.33] | 0.41 [-0.55, 1.36] | -0.24 [-0.80, 0.30] | 0.88871113 | 0.40945905 |
| Kimi K3.1 Pro | -2.15 [-5.25, 0.65] | -0.56 [-2.98, 1.83] | -1.59 [-3.40, -0.15] | 0.1609839 | 0.66353365 |

#### Fictional minus Not disclosed

| Scope | Unadjusted estimate [95% interval] | Adjusted estimate [95% interval] | Unadjusted − adjusted [95% interval] | Unadjusted p | Adjusted p |
| --- | --- | --- | --- | ---: | ---: |
| Pooled (equal model weights) | -0.47 [-1.43, 0.41] | 0.45 [-0.28, 1.15] | -0.92 [-1.57, -0.34] | 0.33736626 | 0.25107489 |
| Claude Sonnet 5.5 | -0.08 [-0.25, 0.00] | -0.06 [-0.23, 0.06] | -0.02 [-0.11, 0.06] | 1 | 0.49045095 |
| GPT-6.1 Terra | -2.00 [-3.83, -0.17] | -0.52 [-1.32, 0.23] | -1.48 [-3.01, 0.00] | 0.054194581 | 0.18668133 |
| Gemini 4 Hydrogen | 0.50 [-0.75, 1.67] | 0.91 [-0.12, 1.93] | -0.41 [-0.99, 0.14] | 0.51924808 | 0.10958904 |
| Kimi K3.1 Pro | -0.32 [-3.43, 2.48] | 1.46 [-1.07, 3.99] | -1.77 [-3.87, -0.15] | 0.93320668 | 0.29087091 |

#### Human minus Not disclosed

| Scope | Unadjusted estimate [95% interval] | Adjusted estimate [95% interval] | Unadjusted − adjusted [95% interval] | Unadjusted p | Adjusted p |
| --- | --- | --- | --- | ---: | ---: |
| Pooled (equal model weights) | -2.46 [-3.17, -1.74] | 0.08 [-0.70, 0.85] | -2.55 [-3.18, -1.93] | 9.9990001e-05 | 0.80291971 |
| Claude Sonnet 5.5 | -0.08 [-0.25, 0.00] | -0.28 [-0.48, -0.12] | 0.20 [0.06, 0.34] | 1 | 0.00069993001 |
| GPT-6.1 Terra | -2.50 [-3.83, -1.17] | 4.38 [2.77, 5.80] | -6.88 [-8.63, -5.09] | 0.00229977 | 9.9990001e-05 |
| Gemini 4 Hydrogen | -2.08 [-3.17, -1.00] | -1.50 [-2.34, -0.72] | -0.58 [-1.09, -0.12] | 0.00059994001 | 0.00039996 |
| Kimi K3.1 Pro | -5.18 [-7.33, -2.73] | -2.26 [-4.74, 0.35] | -2.92 [-4.79, -1.44] | 9.9990001e-05 | 0.01919808 |

#### Label contrasts in stated beliefs

| Contrast | Scope | Estimate (dollars) | 95% interval | Two-sided p |
| --- | --- | ---: | --- | ---: |
| Own model − Another lab | Pooled (equal model weights) | 0.47 | [-1.23, 2.17] | 0.6210379 |
| Own model − Another lab | Claude Sonnet 5.5 | -2.38 | [-4.40, -0.20] | 0.094990501 |
| Own model − Another lab | GPT-6.1 Terra | -2.42 | [-5.87, 0.88] | 0.19938006 |
| Own model − Another lab | Gemini 4 Hydrogen | 0.17 | [-1.42, 1.67] | 0.91310869 |
| Own model − Another lab | Kimi K3.1 Pro | 6.50 | [1.13, 11.75] | 0.01819818 |
| Another lab − Fictional | Pooled (equal model weights) | 0.38 | [-1.17, 1.95] | 0.64823518 |
| Another lab − Fictional | Claude Sonnet 5.5 | 1.50 | [1.00, 2.00] | 9.9990001e-05 |
| Another lab − Fictional | GPT-6.1 Terra | -1.00 | [-2.67, 0.67] | 0.33766623 |
| Another lab − Fictional | Gemini 4 Hydrogen | 0.42 | [-0.92, 1.75] | 0.6380362 |
| Another lab − Fictional | Kimi K3.1 Pro | 0.60 | [-5.15, 6.45] | 0.87151285 |
| Own model − Not disclosed | Pooled (equal model weights) | -1.39 | [-3.04, 0.25] | 0.1189881 |
| Own model − Not disclosed | Claude Sonnet 5.5 | -0.97 | [-2.98, 1.13] | 0.50634937 |
| Own model − Not disclosed | GPT-6.1 Terra | -5.33 | [-8.90, -1.95] | 0.00459954 |
| Own model − Not disclosed | Gemini 4 Hydrogen | -0.42 | [-2.00, 1.08] | 0.68353165 |
| Own model − Not disclosed | Kimi K3.1 Pro | 1.15 | [-3.83, 6.00] | 0.66173383 |
| Another lab − Not disclosed | Pooled (equal model weights) | -1.86 | [-3.20, -0.52] | 0.0089991001 |
| Another lab − Not disclosed | Claude Sonnet 5.5 | 1.42 | [0.83, 2.00] | 0.00019998 |
| Another lab − Not disclosed | GPT-6.1 Terra | -2.92 | [-4.67, -1.25] | 0.00219978 |
| Another lab − Not disclosed | Gemini 4 Hydrogen | -0.58 | [-1.92, 0.75] | 0.4729527 |
| Another lab − Not disclosed | Kimi K3.1 Pro | -5.35 | [-10.17, -0.55] | 0.03519648 |
| Fictional − Not disclosed | Pooled (equal model weights) | -2.24 | [-3.75, -0.75] | 0.00389961 |
| Fictional − Not disclosed | Claude Sonnet 5.5 | -0.08 | [-0.42, 0.25] | 1 |
| Fictional − Not disclosed | GPT-6.1 Terra | -1.92 | [-3.83, 0.00] | 0.074092591 |
| Fictional − Not disclosed | Gemini 4 Hydrogen | -1.00 | [-2.33, 0.33] | 0.18828117 |
| Fictional − Not disclosed | Kimi K3.1 Pro | -5.95 | [-11.45, -0.53] | 0.0379962 |
| Human − Not disclosed | Pooled (equal model weights) | -4.83 | [-5.82, -3.78] | 9.9990001e-05 |
| Human − Not disclosed | Claude Sonnet 5.5 | 0.83 | [0.25, 1.42] | 0.01209879 |
| Human − Not disclosed | GPT-6.1 Terra | -8.92 | [-10.75, -7.08] | 9.9990001e-05 |
| Human − Not disclosed | Gemini 4 Hydrogen | -1.42 | [-2.58, -0.33] | 0.0249975 |
| Human − Not disclosed | Kimi K3.1 Pro | -9.80 | [-13.03, -6.20] | 9.9990001e-05 |

#### Fixed belief-rule diagnostics

The minimum is 30 nonmodal draws among 300 retained valid proposer draws,
using each label × paraphrase cell's lowest tied mode. This rule was fixed
before the pilot and is unchanged. **No model is flagged as not estimable.**

| Model | Retained draws | Nonmodal draws | Required minimum | Estimable | Singular bootstrap fits / attempted |
| --- | ---: | ---: | ---: | --- | --- |
| Claude Sonnet 5.5 | 300 | 38 | 30 | Yes | 0 / 10000 |
| GPT-6.1 Terra | 300 | 96 | 30 | Yes | 0 / 10000 |
| Gemini 4 Hydrogen | 300 | 134 | 30 | Yes | 0 / 10000 |
| Kimi K3.1 Pro | 300 | 123 | 30 | Yes | 0 / 10000 |

Full values: [S1 changes](generated/s1_coefficient_changes.csv), [model diagnostics](generated/s1_belief_diagnostics.csv), [cell modes/counts](generated/s1_belief_cell_counts.csv).

## 3. Descriptives and collection diagnostics

All 3,600 final main draws are valid; there are no exclusions or invalid
re-asks. Each row has n = 60. Equal split means exactly 50 dollars; the zero
share means exactly 0 dollars. Percentages below are display formatting of the
existing share columns. Means/medians and the full SD/modal/distinct-value
outputs are preserved in [descriptives.csv](generated/descriptives.csv).
Exclusion/re-ask/API-error counts are in
[attempt_diagnostics.csv](generated/attempt_diagnostics.csv).

### Claude Sonnet 5.5

| Decision | Label | n | Mean | Median | Equal-split share | Zero share | Exclusions | Re-asks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dictator transfer | Own model | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Dictator transfer | Another lab | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Dictator transfer | Fictional | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Dictator transfer | Not disclosed | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Dictator transfer | Human | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Proposer offer | Own model | 60 | 46.67 | 50.00 | 66.67% | 0.00% | 0 | 0 |
| Proposer offer | Another lab | 60 | 40.00 | 40.00 | 0.00% | 0.00% | 0 | 0 |
| Proposer offer | Fictional | 60 | 40.00 | 40.00 | 0.00% | 0.00% | 0 | 0 |
| Proposer offer | Not disclosed | 60 | 40.08 | 40.00 | 0.00% | 0.00% | 0 | 0 |
| Proposer offer | Human | 60 | 40.00 | 40.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Own model | 60 | 33.33 | 30.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Another lab | 60 | 27.67 | 30.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Fictional | 60 | 29.00 | 30.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Not disclosed | 60 | 27.08 | 30.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Human | 60 | 20.75 | 20.00 | 0.00% | 0.00% | 0 | 0 |

### GPT-6.1 Terra

| Decision | Label | n | Mean | Median | Equal-split share | Zero share | Exclusions | Re-asks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dictator transfer | Own model | 60 | 37.50 | 50.00 | 75.00% | 25.00% | 0 | 0 |
| Dictator transfer | Another lab | 60 | 41.67 | 50.00 | 83.33% | 16.67% | 0 | 0 |
| Dictator transfer | Fictional | 60 | 46.67 | 50.00 | 93.33% | 6.67% | 0 | 0 |
| Dictator transfer | Not disclosed | 60 | 35.83 | 50.00 | 71.67% | 28.33% | 0 | 0 |
| Dictator transfer | Human | 60 | 47.50 | 50.00 | 95.00% | 5.00% | 0 | 0 |
| Proposer offer | Own model | 60 | 39.08 | 40.00 | 30.00% | 0.00% | 0 | 0 |
| Proposer offer | Another lab | 60 | 40.25 | 40.00 | 5.00% | 0.00% | 0 | 0 |
| Proposer offer | Fictional | 60 | 39.83 | 40.00 | 10.00% | 0.00% | 0 | 0 |
| Proposer offer | Not disclosed | 60 | 41.83 | 40.00 | 26.67% | 0.00% | 0 | 0 |
| Proposer offer | Human | 60 | 39.33 | 40.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Own model | 60 | 29.40 | 50.00 | 56.67% | 1.67% | 0 | 0 |
| Responder minimum | Another lab | 60 | 26.42 | 35.00 | 36.67% | 0.00% | 0 | 0 |
| Responder minimum | Fictional | 60 | 21.20 | 1.00 | 35.00% | 1.67% | 0 | 0 |
| Responder minimum | Not disclosed | 60 | 21.12 | 1.00 | 35.00% | 1.67% | 0 | 0 |
| Responder minimum | Human | 60 | 20.82 | 1.00 | 21.67% | 5.00% | 0 | 0 |

### Gemini 4 Hydrogen

| Decision | Label | n | Mean | Median | Equal-split share | Zero share | Exclusions | Re-asks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dictator transfer | Own model | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Dictator transfer | Another lab | 60 | 49.17 | 50.00 | 98.33% | 1.67% | 0 | 0 |
| Dictator transfer | Fictional | 60 | 48.33 | 50.00 | 96.67% | 3.33% | 0 | 0 |
| Dictator transfer | Not disclosed | 60 | 50.00 | 50.00 | 100.00% | 0.00% | 0 | 0 |
| Dictator transfer | Human | 60 | 49.17 | 50.00 | 98.33% | 1.67% | 0 | 0 |
| Proposer offer | Own model | 60 | 47.67 | 50.00 | 68.33% | 0.00% | 0 | 0 |
| Proposer offer | Another lab | 60 | 43.92 | 45.00 | 15.00% | 0.00% | 0 | 0 |
| Proposer offer | Fictional | 60 | 44.25 | 45.00 | 20.00% | 0.00% | 0 | 0 |
| Proposer offer | Not disclosed | 60 | 43.75 | 45.00 | 13.33% | 0.00% | 0 | 0 |
| Proposer offer | Human | 60 | 41.67 | 40.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Own model | 60 | 18.07 | 25.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Another lab | 60 | 12.37 | 1.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Fictional | 60 | 12.52 | 1.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Not disclosed | 60 | 13.07 | 1.00 | 0.00% | 0.00% | 0 | 0 |
| Responder minimum | Human | 60 | 6.13 | 1.00 | 0.00% | 0.00% | 0 | 0 |

### Kimi K3.1 Pro

| Decision | Label | n | Mean | Median | Equal-split share | Zero share | Exclusions | Re-asks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dictator transfer | Own model | 60 | 34.17 | 50.00 | 68.33% | 31.67% | 0 | 0 |
| Dictator transfer | Another lab | 60 | 26.67 | 50.00 | 53.33% | 46.67% | 0 | 0 |
| Dictator transfer | Fictional | 60 | 25.00 | 25.00 | 50.00% | 50.00% | 0 | 0 |
| Dictator transfer | Not disclosed | 60 | 28.33 | 50.00 | 56.67% | 43.33% | 0 | 0 |
| Dictator transfer | Human | 60 | 30.83 | 50.00 | 61.67% | 38.33% | 0 | 0 |
| Proposer offer | Own model | 60 | 48.03 | 50.00 | 93.33% | 0.00% | 0 | 0 |
| Proposer offer | Another lab | 60 | 45.20 | 50.00 | 65.00% | 0.00% | 0 | 0 |
| Proposer offer | Fictional | 60 | 47.03 | 50.00 | 83.33% | 0.00% | 0 | 0 |
| Proposer offer | Not disclosed | 60 | 47.35 | 50.00 | 80.00% | 0.00% | 0 | 0 |
| Proposer offer | Human | 60 | 42.17 | 40.00 | 28.33% | 0.00% | 0 | 0 |
| Responder minimum | Own model | 60 | 41.00 | 50.00 | 81.67% | 1.67% | 0 | 0 |
| Responder minimum | Another lab | 60 | 32.62 | 50.00 | 63.33% | 6.67% | 0 | 0 |
| Responder minimum | Fictional | 60 | 32.43 | 50.00 | 61.67% | 8.33% | 0 | 0 |
| Responder minimum | Not disclosed | 60 | 29.35 | 50.00 | 56.67% | 6.67% | 0 | 0 |
| Responder minimum | Human | 60 | 9.68 | 1.00 | 13.33% | 11.67% | 0 | 0 |

### Reasoning and cached tokens per model

Reported response-token counts are used as provided. Means/medians/ranges are
conditional on an observed count. Missing counts are not zeros. The 13 API-error
attempts have no response usage and are separate from the 900 responses/model.
Gemini has one missing reasoning count, all 900 cache-read/write counts missing;
Kimi has 324 missing cache-read counts. OpenAI and Anthropic report observed
zero cache reads/writes throughout. Full input/output/reasoning/cache summaries
and every attempt's usage remain in [usage_summary.csv](generated/usage_summary.csv)
and [usage_calls.csv](generated/usage_calls.csv).

| Model | Metric | Observed / responses | Missing | Mean | Median | Minimum | Maximum |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Claude Sonnet 5.5 | reasoning_tokens | 900 / 900 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| Claude Sonnet 5.5 | cache_read_tokens | 900 / 900 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| Claude Sonnet 5.5 | cache_write_tokens | 900 / 900 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| GPT-6.1 Terra | reasoning_tokens | 900 / 900 | 0 | 44.92 | 41.00 | 7.00 | 169.00 |
| GPT-6.1 Terra | cache_read_tokens | 900 / 900 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| GPT-6.1 Terra | cache_write_tokens | 900 / 900 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| Gemini 4 Hydrogen | reasoning_tokens | 899 / 900 | 1 | 292.61 | 283.00 | 73.00 | 656.00 |
| Gemini 4 Hydrogen | cache_read_tokens | 0 / 900 | 900 | NA | NA | NA | NA |
| Gemini 4 Hydrogen | cache_write_tokens | 0 / 900 | 900 | NA | NA | NA | NA |
| Kimi K3.1 Pro | reasoning_tokens | 900 / 900 | 0 | 122.47 | 107.00 | 25.00 | 569.00 |
| Kimi K3.1 Pro | cache_read_tokens | 576 / 900 | 324 | 256.00 | 256.00 | 256.00 | 256.00 |
| Kimi K3.1 Pro | cache_write_tokens | 900 / 900 | 0 | 92.16 | 0.00 | 0.00 | 256.00 |

## 4. Final-prompt comprehension check

This is the separate revised/final-prompt check specified in the registration,
not the historical original-prompt check. Pass requires at least 18/20 correct
in each of own-model, other-lab, and fictional conditions. Undisclosed is reported
but unscored. There are no excluded, unfinished, or not-started check draws.

| Model | Own-model yes | Other-lab no | Fictional no | Not-disclosed unsure (unscored) | Model result |
| --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5.5 | 20/20 | 20/20 | 20/20 | 20/20 | Pass |
| GPT-6.1 Terra | 20/20 | 20/20 | 20/20 | 20/20 | Pass |
| Gemini 4 Hydrogen | 20/20 | 20/20 | 20/20 | 20/20 | Pass |
| Kimi K3.1 Pro | 20/20 | 20/20 | 20/20 | 20/20 | Pass |

All answer counts/shares and planned denominators are preserved in
[comprehension.csv](generated/comprehension.csv).

## 5. Figures produced

The four registered figures were produced in both PDF and PNG, unchanged from
the frozen plotting code:

| Figure | PDF | PNG |
| --- | --- | --- |
| Main dictator/proposer distributions, model panels and pooled P1 annotation | [main_distributions.pdf](generated/main_distributions.pdf) | [main_distributions.png](generated/main_distributions.png) |
| Responder minimum distributions | [responder_distributions.pdf](generated/responder_distributions.pdf) | [responder_distributions.png](generated/responder_distributions.png) |
| S1 unadjusted/adjusted offer and belief contrasts | [s1_coefficients.pdf](generated/s1_coefficients.pdf) | [s1_coefficients.png](generated/s1_coefficients.png) |
| Comprehension-check table | [comprehension.pdf](generated/comprehension.pdf) | [comprehension.png](generated/comprehension.png) |

## Reproducibility and scope

The exact frozen command completed successfully. The current-main reproduction
used the same Study 1 command/inputs, changing only its output directory to
`scratch/study1-reproduce/`. All **12 CSV tables**, **330 saved resampling
arrays**, the **NPZ archive**, and all **eight PDF/PNG figure files** are
byte-identical. There are no numerical or figure differences, including figure
metadata. Only `provenance.json` and its entry in `artifacts.sha256.json` differ:
absolute checkout paths, Git commit, and the main package-source inventory
(Study 2 additions and additive CLI dispatch). Study 1 analysis source, data,
configuration, prompts, parameters, seeds, and locked dependency versions match.
Both runs used Matplotlib's automatic temporary font-cache fallback because
the default cache directory was unwritable; this did not cause a run failure
or any figure difference.

The frozen artifacts were copied byte-for-byte into `generated/`. Full commands,
source commits, hashes and comparisons are in [reproducibility.json](reproducibility.json).
No analysis fix, parameter/seed change, additional statistical analysis, or
Study 2 modification was made. Results are committed on main only; the frozen
worktree has no commit. A push requires the researcher's approval.

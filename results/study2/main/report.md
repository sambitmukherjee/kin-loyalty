# Study 2 results

MAIN STUDY

All 960 episode summaries verified against saved turn attempts.

Primary same-label minus other-label share: -0.0026437001375587106; 95% interval [-0.008584189395387399, 0.003424525019448452]; two-sided permutation p=0.39856014398560147.

Bootstrap TOST: {"alpha": 0.05, "available": true, "bootstrap_resamples": 10000, "bound": 0.05, "contrast_ci_high": 0.003424525019448452, "contrast_ci_level": 0.95, "contrast_ci_low": -0.008584189395387399, "contrast_ci_lower_rank": 250, "contrast_ci_method": "percentile_count_matched", "contrast_ci_upper_rank": 9751, "equivalence_ci_high": 0.002469699604268686, "equivalence_ci_level": 0.9, "equivalence_ci_low": -0.007658102208929781, "equivalence_ci_lower_rank": 500, "equivalence_ci_method": "percentile_count_matched", "equivalence_ci_strictly_inside": true, "equivalence_ci_upper_rank": 9501, "equivalent": true, "estimate": -0.0026437001375587106, "inference_tie_tolerance": 1e-12, "lower_tail_count": 0, "p_lower": 9.999000099990002e-05, "p_tost": 9.999000099990002e-05, "p_upper": 9.999000099990002e-05, "upper_tail_count": 0}

Primary inference uses scenario bootstraps and matched-label permutations. Pair-cluster standard errors are a robustness check only (16 clusters).

Secondary tests have no multiplicity correction. Deal-only share and messages to agreement condition on agreement, which the card can itself affect. Concessions use only consecutive own buyer offers; acceptance is not an offer. Positive means raising the offer; negative values and all other outcomes are unclipped. See outcome_eligibility.csv for eligible episodes per original condition and displayed label.

Every permutation test reports complete and incomplete tested-pair strata. Incomplete pairs stay fixed; eligible singleton rows remain in OLS/bootstrap. Missing third-condition outcomes never prevent a complete tested-pair swap.

The secondary interaction is (same minus other in self-pairs) minus (same minus other in cross-pairs), adjusted for pair and opener; it has a bootstrap interval only, with no permutation test. The actual-kinship mean table is descriptive, without a test. Figure 2 groups by displayed same/other/none.

metadata.json records frozen seeds, methods, replay, package versions, code/input hashes, and provenance. resamples.npz preserves every bootstrap scenario index, estimate, and permutation statistic, including unavailable draws. Failed draws are never dropped or redrawn; affected intervals/TOST are unavailable.

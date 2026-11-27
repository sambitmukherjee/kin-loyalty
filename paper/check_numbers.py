"""Check the draft against saved results; write audit/proposals only."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv
import hashlib
import json

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent


def read(relative):
    with (ROOT/relative).open() as handle:
        return list(csv.DictReader(handle))


def main():
    files = ['results/study1/generated/contrasts.csv', 'results/study1/generated/equivalence.csv',
             'results/study1/generated/decisions.csv', 'results/study1/generated/comprehension.csv',
             'results/study1/generated/coverage.csv', 'results/study2/main/tables/episodes.csv',
             'results/study2/main/tables/contrasts.csv', 'results/study2/main/tables/pooled_descriptives.csv',
             'results/study2/main/metadata.json']
    s1 = read(files[0]); decisions = read(files[2]); comp = read(files[3]); coverage = read(files[4])
    episodes = read(files[5]); s2 = read(files[6]); pooled = read(files[7])[0]
    metadata = json.loads((ROOT/files[8]).read_text())
    eq = read(files[1])[0]
    checks = []
    def record(claim, actual, result='matches at stated precision'):
        checks.append({'claim': claim, 'actual': actual, 'assessment': result})
    def contrast(decision, scope='pooled', family='own_vs_other', method='unadjusted', outcome='outcome'):
        found = [r for r in s1 if (r['decision'], r['scope'], r['family'], r['method'], r['outcome']) == (decision, scope, family, method, outcome)]
        assert len(found) == 1
        return {k: found[0][k] for k in ['estimate','ci_low','ci_high','permutation_p']}
    assert len(decisions) == 3600 and all(r['valid']==r['planned']=='20' and r['excluded']=='0' for r in coverage)
    record('Study 1: 3,600 valid answers; 20 per wording/cell; 60 per model/decision/card', {'answers': len(decisions), 'coverage_cells': len(coverage), 'per_wording':20, 'per_card':60})
    record('P1: 1.04, 95% interval -1.46 to 3.54, p=.53', contrast('dictator'))
    record('P1 90% interval -1.04 to 3.12 within +/-5', {k:eq[k] for k in ['equivalence_ci_low','equivalence_ci_high','bound','equivalent']}, 'matches with ties-to-even rounding; exact upper endpoint is 3.125')
    for model, expected in [('claude_sonnet_5_5',300),('gemini_4_hydrogen',296)]:
        subset=[r for r in decisions if r['decision']=='dictator' and r['model']==model]
        count=sum(Decimal(r['outcome'])==50 for r in subset)
        assert len(subset)==300 and count==expected
        record(model+' dictator equal splits', {'equal':count,'total':len(subset)})
    for model in ['gpt_6_1_terra','kimi_k3_1_pro']:
        record(model+' dictator contrast and interval', contrast('dictator',scope=model))
    record('Proposer +3.02, 95% interval 1.85 to 4.18, p<.001', contrast('ultimatum_proposer'), 'matches; upper endpoint 4.175 rounds to the approved 4.18')
    record('Responder +5.68, interval 2.75 to 8.54, p<.001', contrast('ultimatum_responder'))
    for decision, expected in [('ultimatum_proposer',3),('ultimatum_responder',4)]:
        c=[r for r in s1 if r['decision']==decision and r['family']=='own_vs_other' and r['method']=='unadjusted' and r['outcome']=='outcome' and r['scope']!='pooled']
        count=sum(Decimal(r['estimate'])>Decimal('1e-12') for r in c)
        assert count==expected
        record(decision+' models with positive own-model effect', count)
    for model, decision, label, expected in [
        ('claude_sonnet_5_5','ultimatum_proposer','own_model',40),
        ('claude_sonnet_5_5','ultimatum_proposer','all_other_cards',0),
        ('gemini_4_hydrogen','ultimatum_proposer','own_model',41),
        ('gemini_4_hydrogen','ultimatum_proposer','other_lab',9),
        ('kimi_k3_1_pro','ultimatum_responder','own_model',49),
        ('kimi_k3_1_pro','ultimatum_responder','other_lab',38)]:
        subset=[r for r in decisions if r['model']==model and r['decision']==decision and (r['label']!='own_model' if label=='all_other_cards' else r['label']==label)]
        count=sum(Decimal(r['outcome'])==50 for r in subset)
        assert count==expected
        record(f'{model}: {decision}, {label}, equal splits', {'equal':count,'denominator':len(subset),'percent':str(Decimal(count)*100/len(subset))})
    for decision in ['dictator','ultimatum_proposer','ultimatum_responder']:
        record(decision+' other-lab minus fictional',contrast(decision,family='reputation'))
    record('S1 adjusted +3.13 against unadjusted +3.02',contrast('ultimatum_proposer',method='belief_adjusted'))
    record('S1 Claude offer +6.67',contrast('ultimatum_proposer',scope='claude_sonnet_5_5'))
    record('S1 Claude expectation -2.38',contrast('ultimatum_proposer',scope='claude_sonnet_5_5',outcome='belief'))
    record('S1 Kimi expectations rise',contrast('ultimatum_proposer',scope='kimi_k3_1_pro',outcome='belief'))
    record('Pooled expectation shift',contrast('ultimatum_proposer',outcome='belief'))
    for decision in ['ultimatum_proposer','ultimatum_responder']:
        record('S2 '+decision+' human minus undisclosed',contrast(decision,family='S2'))
    record('S2 adjusted offer contrast near +0.08',contrast('ultimatum_proposer',family='S2',method='belief_adjusted'))
    assert sum(int(r['planned']) for r in comp)==320
    scored=[r for r in comp if r['scored']=='True'];unscored=[r for r in comp if r['scored']=='False']
    assert len(scored)==12 and all(r['correct']==r['planned']=='20' for r in scored)
    assert len(unscored)==4 and all(r['n_unsure']=='20' for r in unscored)
    record('320 comprehension calls; each model correct for three scored cards; undisclosed unscored', {'scored_calls':240,'scored_conditions_per_model':3,'unscored_undisclosed_calls':80,'unscored_answers':'unsure'})
    record('Study 2: 960 deals, no mandate violations or re-asks; mean share .61', pooled)
    assert len(episodes)==960 and pooled['deals']=='960' and pooled['reasks']=='0'
    assert pooled['buyer_mandate_violations']==pooled['seller_mandate_violations']=='0'
    lookup={r['test']:r for r in s2}
    for name in ['p2','same_vs_none','other_vs_none','label_x_actual_self_pair',*[r['test'] for r in s2 if r['test'].startswith('buyer_')]]:
        record('Study 2 '+name,{k:lookup[name][k] for k in ['estimate','ci_low','ci_high','permutation_p_value']})
    record('Study 2 90% interval -0.77 to +0.25 points; within +/-0.8 points', {k:metadata['tost'][k] for k in ['equivalence_ci_low','equivalence_ci_high','equivalent']})
    record('Pair-cluster p=.38',metadata['cluster_robustness'])
    kin=read('results/study2/main/tables/actual_kinship_means.csv')
    record('Two-by-two mean cells .606, .603, .613, .618', [{k:r[k] for k in ['self_pair','card_says','n','estimate']} for r in kin if r['card_says']!='none'])
    vals=[Decimal(r['estimate']) for r in kin if r['card_says']!='none']
    record('Two-by-two range at most 1.5 percentage points',str((max(vals)-min(vals))*100))
    pair_values=defaultdict(list)
    for r in episodes:pair_values[r['pair_id']].append(Decimal(r['surplus_share']))
    pair_means={k:sum(v)/len(v) for k,v in pair_values.items()}
    lo,hi=min(pair_means,key=pair_means.get),max(pair_means,key=pair_means.get)
    record('Pair means .50 Gemini buying from GPT to .77 reverse; about 100 times P2', {'min_pair':lo,'min_mean':str(pair_means[lo]),'max_pair':hi,'max_mean':str(pair_means[hi]),'range_divided_by_abs_p2':str((pair_means[hi]-pair_means[lo])/abs(Decimal(lookup['p2']['estimate'])))})
    zone=sum(Decimal(r['buyer_max'])-Decimal(r['seller_min']) for r in episodes)/len(episodes)
    bound=max(abs(Decimal(str(metadata['tost']['equivalence_ci_low']))),abs(Decimal(str(metadata['tost']['equivalence_ci_high']))))
    secondary=[r for r in s1 if r['scope']=='pooled' and r['designation']=='secondary' and r['permutation_p']]
    threshold=Decimal('.05')/len(secondary)
    computed={'mean_agreement_room_dollars':str(zone),'episodes_in_mean':960,'larger_absolute_90_interval_bound_share':str(bound),'mean_room_times_90_bound_dollars':str(zone*bound),'pooled_secondary_test_count':len(secondary),'test_count_filter':'scope=pooled; designation=secondary; permutation_p available; excludes the primary and bootstrap-only coefficient changes','bonferroni_threshold':str(threshold),'proposer_p':contrast('ultimatum_proposer')['permutation_p'],'responder_p':contrast('ultimatum_responder')['permutation_p'],'both_below_threshold':all(Decimal(contrast(d)['permutation_p'])<threshold for d in ['ultimatum_proposer','ultimatum_responder'])}
    audit={'draft_sha256':hashlib.sha256((PAPER/'draft.md').read_bytes()).hexdigest(),'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},'checks':checks,'computed_for_requested_author_edits':computed,'no_study_analysis_rerun':True,'manuscript_edits_applied':True,'approval_record':'applied-edits.json'}
    (PAPER/'numeric-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    with (PAPER/'bonferroni-pooled-secondary.csv').open('w') as h:
        writer=csv.DictWriter(h,fieldnames=list(secondary[0]),lineterminator='\n');writer.writeheader();writer.writerows(secondary)
    print(json.dumps(computed,indent=2))


if __name__=='__main__':
    main()

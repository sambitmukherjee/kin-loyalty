"""Read-only factual checks requested for the appendix correction pass."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import csv,json,hashlib,re,subprocess
import yaml
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent

def verify():
    def rows(path):return list(csv.DictReader((ROOT/path).open()))
    usage=rows('results/study2/main/tables/usage_summary.csv')
    assert len(usage)==8 and all(int(r['accept_price_mismatches'])==0 for r in usage)
    for name in ['episodes.csv','usage_calls.csv']:
        assert all(r['accept_price_mismatch']=='False' for r in rows('results/study2/main/tables/'+name)),name
    contrasts=rows('results/study1/generated/contrasts.csv')
    family=[r for r in contrasts if r['scope']=='pooled' and r['designation']=='secondary' and r['permutation_p']]
    counts=Counter((r['outcome'],r['method']) for r in family)
    assert counts=={('outcome','unadjusted'):17,('belief','unadjusted'):6,('outcome','belief_adjusted'):6}
    gemini=[json.loads(s) for s in (ROOT/'data/study2/pilot/episodes.jsonl').read_text().splitlines() if s]
    gemini=[r for r in gemini if 'gemini_4_hydrogen' in [r['buyer_model'],r['seller_model']]]
    assert len(gemini)==35 and max(r['messages_used'] for r in gemini)==11
    cfg=yaml.safe_load((ROOT/'configs/study1.yaml').read_text())['comprehension']
    assert cfg['paraphrase_counts']==cfg['other_lab_name_counts']==[7,7,6]
    assert cfg['other_lab_joint_counts']==[[3,2,2],[2,3,2],[2,2,2]]
    render=(ROOT/'src/kinloyalty/negotiation/prompts.py').read_text()
    assert 'return re.sub(r"\{([A-Z][A-Z0-9_]*)\}", substitute, template)' in render
    lock=json.loads((ROOT/'preregistration/study2-lock.json').read_text())
    models=yaml.safe_load((ROOT/'configs/models.yaml').read_text())['models']
    assert all(v==[models[k]['api_model_id']] for k,v in lock['pilot_returned_versions'].items())
    runner=(ROOT/'src/kinloyalty/negotiation/runner.py').read_text()
    assert 'attempt.response.returned_model_version != expected' in runner and "if record.get('model_drift'):" in runner
    auth=(ROOT/'src/kinloyalty/negotiation/authorization.py').read_text()
    assert 'natural_attempt_cap: None = None' in auth
    launch=(ROOT/'src/kinloyalty/negotiation/main_run.py').read_text()
    assert "'api_attempts_per_response_opportunity': 4" in launch and 'while True:' in launch
    borderline=[{'csv_row':i+2,**{k:r[k] for k in ['scope','decision','outcome','method','left','right','permutation_p']}} for i,r in enumerate(contrasts) if r['permutation_p'] and Decimal(r['permutation_p'])<Decimal('.05') and Decimal(r['permutation_p']).quantize(Decimal('.0001'))==Decimal('.0500')]
    assert len(borderline)==1
    ties=[]
    for i,r in enumerate(contrasts):
        if r['scope']!='pooled' or r['method']!='unadjusted':continue
        for field in ['estimate','ci_low','ci_high']:
            x=Decimal(r[field]);n=(240*x).to_integral_value()
            assert abs(240*x-n)<Decimal('0.0000001')
            exact=n/240
            if abs(exact*100)%1==Decimal('.5'):
                ties.append({'csv_row':i+2,'decision':r['decision'],'outcome':r['outcome'],'left':r['left'],'right':r['right'],'field':field,'csv_value':r[field],'exact_numerator':str(n),'exact_denominator':240,'exact_decimal':str(exact)})
    checks={'A4':{'mismatched_acceptances_by_model_and_role':[{'model':r['model'],'role':r['role'],'count':int(r['accept_price_mismatches'])} for r in usage]},'A5':{'total':len(family),'outcome':17,'belief':6,'adjusted_offer':6},'B1':{'drift':'returned model string differs from expected string; expected pilot strings equal requested IDs','episodes_required':960,'attempts_per_response_opportunity':4,'aggregate_attempt_cap':None,'sources':['src/kinloyalty/negotiation/runner.py','src/kinloyalty/negotiation/authorization.py','src/kinloyalty/negotiation/main_run.py','docs/study2_main_execution_patch.md']},'B2':{'gemini_pilot_episodes':35,'maximum_messages':11,'no_episode_involving_gemini_reached_message_12':True},'B4':{'single_re_sub_pass':True},'B5':cfg,'C1':borderline,'C3':{'rule':'round half to even','exact_lattice_applies_to':'unadjusted pooled Study 1 contrasts and their bootstrap endpoints, not belief-adjusted regressions','verified_ties':ties}}
    (HERE/'fix-verifications.json').write_text(json.dumps(checks,indent=2)+'\n')
    return checks
if __name__=='__main__':verify();print('Appendix fact checks passed.')

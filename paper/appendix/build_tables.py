"""Typeset saved result cells, without fitting models or resampling data.

Every displayed numeric cell records its source path, CSV row and field in
number-trace.json. Decimal rounding and percentage conversion are display only.
"""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
import csv
import hashlib
import json
import re
import subprocess
import sys
import yaml

HERE=Path(__file__).resolve().parent
PAPER=HERE.parent
ROOT=PAPER.parent
sys.path.insert(0, str(PAPER))
from tool_paths import poppler_tool
OUT=HERE/'generated'
MODELS=['claude_sonnet_5_5','gpt_6_1_terra','gemini_4_hydrogen','kimi_k3_1_pro']
SHORT=dict(zip(MODELS,['Sonnet','Terra','Hydrogen','Kimi']))
SHORT.update({'pooled':'Pooled','all':'All buyers'})
FULL=dict(zip(MODELS,['Claude Sonnet 5.5','GPT-6.1 Terra','Gemini 4 Hydrogen','Kimi K3.1 Pro']))
LABEL={'own_model':'Own model','other_lab':'Other lab','fictional':'Fictional','not_disclosed':'Undisclosed','human':'Human','true':'True card','swapped':'Swapped','same':'Says same','other':'Says other','none':'Says none'}
DEC={'dictator':'Dictator transfers','ultimatum_proposer':'Proposer offers','ultimatum_responder':'Responder minimums'}
OUTCOME={'surplus_share':'Buyer surplus share','within_deal_share':'Share among deals','deal':'Deal indicator','messages_to_agreement':'Messages to agreement','buyer_first_offer_position':'First buyer offer position','buyer_average_concession':'Average buyer concession','buyer_mandate_violation':'Buyer mandate violation','seller_mandate_violation':'Seller mandate violation'}
TRACE=[];SOURCES={};TABLES=[];STATEMENTS=[]
TRACE_CURSOR=0

def esc(text):
    text=str(text)
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','−':'-','×':r'$\times$'}.get(c,c) for c in text)

def read(path):
    p=ROOT/path;SOURCES[path]=hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open() as h:rows=list(csv.DictReader(h))
    for i,r in enumerate(rows):r['_source']=path;r['_row']=i+2
    return rows

def cell(row,key,digits=None,percent=False):
    value=row.get(key,'')
    if value in ('','nan','NaN','None'):display='--'
    elif value in ('True','False') or isinstance(value,bool):display='Yes' if value in ('True',True) else 'No'
    elif digits is None:display=value
    else:
        x=Decimal(value)
        lattice=None
        if row['_source']=='results/study1/generated/contrasts.csv' and row.get('scope')=='pooled' and row.get('method')=='unadjusted' and key in ['estimate','ci_low','ci_high']:
            lattice=240
        if row['_source']=='results/study1/generated/equivalence.csv' and key in ['estimate','equivalence_ci_low','equivalence_ci_high','contrast_ci_low','contrast_ci_high']:
            lattice=240
        if row['_source']=='results/study2/main/tables/pair_condition_descriptives.csv' and key=='messages_used_mean_retained':
            lattice=20
        if lattice:
            numerator=(x*lattice).to_integral_value()
            assert abs(x*lattice-numerator)<Decimal('0.0000001'),(row,key,x)
            x=numerator/Decimal(lattice)
        exact=str(x)
        if digits==4 and key in ['permutation_p','permutation_p_value','p_lower','p_upper','p_tost','p_value'] and x<Decimal('.05') and x.quantize(Decimal('.0001'),rounding=ROUND_HALF_EVEN)==Decimal('.0500'):
            digits=6
        x=x*(100 if percent else 1)
        x=x.quantize(Decimal(1).scaleb(-digits),rounding=ROUND_HALF_EVEN)
        if x==0:x=abs(x)
        display=f'{x:.{digits}f}'
    TRACE.append({'source':row['_source'],'row':row['_row'],'field':key,'raw':value,'display':display,'percent_conversion':percent,'decimal_places':digits,'rounding_rule':'ROUND_HALF_EVEN','exact_decimal_for_rounding':locals().get('exact')})
    return esc(display)

def interval(row,lo='ci_low',hi='ci_high',digits=2):
    return '['+cell(row,lo,digits)+', '+cell(row,hi,digits)+']'

def pval(row,key='permutation_p'):
    return cell(row,key,4)

def table(key,headers,rows,widths,caption,note='',source=None,wide=False):
    global TRACE_CURSOR
    floating=wide or key.startswith(('s2-test','s2-tost','s2-cluster','s2-pair','s2-pooled','s2-mandates'))
    headers=['Value' if h in ['Saved result','Saved value'] else h for h in headers]
    assert len(headers)==len(widths) and all(len(row)==len(headers) for row in rows)
    assert all(not re.search(r'(?<!\\)%',value) for row in rows for value in row),key
    assert sum(widths)+12*(len(widths)-1)/(504 if wide else 239.4)<1.015,(key,widths)
    spec='@{}'+''.join(r'>{\raggedright\arraybackslash}p{'+str(w)+r'\linewidth}' for w in widths)+'@{}'
    tex=[r'\begin{table*}[t]' if wide else (r'\begin{table}[tbp]' if floating else r'\par\noindent\begin{minipage}{\columnwidth}'),r'\centering',r'\begin{tabular}{'+spec+'}',r'\toprule',' & '.join(esc(h) for h in headers)+r' \\',r'\midrule']
    tex+=[' & '.join(row)+r' \\' for row in rows]
    tex += [r'\bottomrule',r'\end{tabular}',(r'\caption{' if floating else r'\captionof{table}{')+esc(caption)+'}',r'\label{tab:'+key+'}']
    if note:tex += [r'\raggedright '+note+r'\par']
    tex += [r'\end{table*}' if wide else (r'\end{table}' if floating else r'\end{minipage}\par'), '']
    for record in TRACE[TRACE_CURSOR:]:record['table_key']=key
    TRACE_CURSOR=len(TRACE)
    TABLES.append({'key':key,'rows':len(rows),'source':source,'caption':caption})
    return '\n'.join(tex)

def write(name,parts):
    (OUT/name).write_text('\n'.join(parts)+'\n')

def usage():
    parts=[]
    data=read('results/study1/generated/usage_summary.csv')
    for metric,title in [('reasoning_tokens','Reasoning tokens'),('cache_read_tokens','Cache-read tokens'),('cache_write_tokens','Cache-write tokens')]:
        rows=[r for m in MODELS for r in data if r['model']==m and r['metric']==metric]
        parts.append(table('s1-'+metric,['Model','Mean','Observed','Missing'],[[SHORT[r['model']],cell(r,'mean',1),cell(r,'observed'),cell(r,'missing')] for r in rows],[.25,.15,.22,.21],f'Study 1. {title} per response.','Means use only responses with that field. Missing counts remain missing, rather than being treated as zero.',data[0]['_source']))
    data=read('results/study2/main/tables/usage_summary.csv')
    for role in ['buyer','seller']:
        for metric,title in [('reasoning_tokens','Reasoning tokens'),('cache_read_tokens','Cache-read tokens'),('cache_write_tokens','Cache-write tokens')]:
            rows=[r for m in MODELS for r in data if r['model']==m and r['role']==role]
            parts.append(table('s2-'+role+'-'+metric,['Model','Mean','Observed','Missing'],[[SHORT[r['model']],cell(r,metric+'_mean',1),cell(r,metric+'_present'),cell(r,metric+'_missing')] for r in rows],[.25,.15,.22,.21],f'Study 2 {role}s. {title} per response.','Observed and missing are response counts for this field, not token totals.',data[0]['_source']))
    write('usage.tex',parts)

def models_and_settings():
    modelconfig=yaml.safe_load((ROOT/'configs/models.yaml').read_text())
    versions={}
    for file in ['results/study1/generated/decisions.csv','results/study2/main/tables/usage_calls.csv']:
        data=read(file)
        for model in MODELS:
            found=sorted({r['returned_model_version'] for r in data if r['model']==model and r['returned_model_version']})
            versions.setdefault(model,[]).append(found)
    parts=[]
    for model in MODELS:
        config=modelconfig['models'][model]
        assert versions[model][0]==versions[model][1]
        parts += [r'\paragraph{'+esc(FULL[model])+'.}', 'Requested model ID: '+r'\mbox{\lstinline!'+config['api_model_id']+r'!}.\par Returned in both studies: '+', '.join(r'\mbox{\lstinline!'+s+'!}' for s in versions[model][0])+r'.\par']
        d=modelconfig['defaults']
        reasoning='thinking_config.thinking_level' if config['provider']=='google' else config['requested_parameters']['reasoning']
        structured='response_json_schema' if config['provider']=='google' else config['requested_parameters']['structured_output']
        caching={'anthropic':'Cache control omitted; no explicit cache request.','openai':'Explicit caching mode with no cache breakpoints set; storage disabled (store=false). The API reported zero cache reads and writes.','google':f"No explicit caching. Inputs were kept below {config['caching'].get('keep_prompt_below_tokens',0):,} tokens, the registered threshold for Gemini's implicit caching. The API reported no cache counts.",'moonshot':'Automatic caching; reported reads, writes and missing fields retained.'}[config['provider']]
        cap_parameter={'anthropic':'max_tokens','openai':'max_completion_tokens','google':'max_output_tokens','moonshot':'max_completion_tokens'}[config['provider']]
        rows=[['Endpoint',esc(config['endpoint']+(' ('+config['transport']['api_version']+')' if 'api_version' in config['transport'] else ''))],['Reasoning',esc(d['reasoning_effort'])+' via '+r'\path{'+reasoning+'}'],['Structured output',('Strict JSON schema via ' if config['requested_parameters']['structured_output_mode']=='strict_json_schema' else 'JSON schema via ')+r'\path{'+structured+'}'+ ('; JSON MIME type.' if config['provider']=='google' else '')],['Caching',esc(caching)],['Output cap',str(d['max_output_tokens'])+' tokens via '+r'\path{'+cap_parameter+'}']]
        parts.append('API address: '+r'\mbox{\url{'+config['transport']['base_url']+'}}.\par')
        parts.append(table('settings-'+model,['Setting','Registered request'],rows,[.25,.63],FULL[model]+': provider settings.','Source: '+r'\path{configs/models.yaml}.'))
    write('models.tex',parts)

def study1_results():
    parts=[];data=read('results/study1/generated/contrasts.csv');used=set()
    groups=defaultdict(list)
    for r in data:groups[(r['decision'],r['outcome'],r['method'],r['left'],r['right'])].append(r)
    count=0
    for decision,outcome,method in [('dictator','outcome','unadjusted'),('ultimatum_proposer','outcome','unadjusted'),('ultimatum_responder','outcome','unadjusted'),('ultimatum_proposer','belief','unadjusted'),('ultimatum_proposer','outcome','belief_adjusted')]:
        title=DEC[decision]
        if outcome=='belief':title='Proposer stated expectations'
        if method=='belief_adjusted':title='Proposer offers adjusted for stated expectations (S1)'
        parts += [r'\subsection{'+title+'}', ('The adjustment is descriptive, not causal mediation. ' if method=='belief_adjusted' else '')+'Tables~'+r'\ref{tab:s1-contrast-'+str(count+1)+'}--'+r'\ref{tab:s1-contrast-'+str(count+6)+'} report these contrasts. Each row compares two cards after adjustment for wording. The estimate and interval are in dollars. Pooled rows give each model equal weight; all other rows concern one model. The last column reports the two-sided permutation p-value.']
        for left,right in [('own_model','other_lab'),('other_lab','fictional'),('own_model','not_disclosed'),('other_lab','not_disclosed'),('fictional','not_disclosed'),('human','not_disclosed')]:
            rows=groups[(decision,outcome,method,left,right)]
            rows=sorted(rows,key=lambda r:['pooled',*MODELS].index(r['scope']))
            count+=1
            for r in rows:used.add(r['_row'])
            comparison=LABEL[left]+' minus '+LABEL[right].lower()+(' (S2)' if left=='human' else '')
            primary=decision=='dictator' and outcome=='outcome' and method=='unadjusted' and left=='own_model' and right=='other_lab'
            note='Only the pooled row is primary P1. Model-specific rows are secondary.' if primary else ''

            parts.append(table('s1-contrast-'+str(count),['Model','Estimate','95% interval','p'],[[SHORT[r['scope']],cell(r,'estimate',2),interval(r),pval(r)] for r in rows],[.20,.16,.30,.18],title+': '+comparison+'.',note,data[0]['_source']))
    assert len(used)==len(data)==150
    write('study1-contrasts.tex',parts)
    data=read('results/study1/generated/equivalence.csv');r=data[0]
    rows=[['Estimate',cell(r,'estimate',2)],['Equivalence bound',r'$\pm$'+cell(r,'bound',2)],['Lower one-sided p',cell(r,'p_lower',4)],['Upper one-sided p',cell(r,'p_upper',4)],['Larger p (TOST)',cell(r,'p_tost',4)],[esc('90% interval'),interval(r,'equivalence_ci_low','equivalence_ci_high')],[esc('95% interval'),interval(r,'contrast_ci_low','contrast_ci_high')],['Equivalence declared',cell(r,'equivalent')]]
    write('study1-equivalence.tex',[table('s1-equivalence',['Quantity','Saved result'],rows,[.49,.39],'Primary P1 equivalence test.','Intervals and bounds are in dollars.',r['_source'])])
    data=read('results/study1/generated/s1_coefficient_changes.csv');parts=[]
    groups=defaultdict(list)
    for r in data:groups[r['left'],r['right']].append(r)
    for i,((left,right),rows) in enumerate(groups.items()):
        rows=sorted(rows,key=lambda r:['pooled',*MODELS].index(r['scope']))
        parts.append(table('s1-change-'+str(i),['Model','Change','95% interval'],[[SHORT[r['scope']],cell(r,'unadjusted_minus_adjusted',2),interval(r)] for r in rows],[.25,.20,.43],'S1 coefficient change: '+LABEL[left]+' minus '+LABEL[right].lower()+'.','',data[0]['_source']))
    write('study1-changes.tex',parts)
    data=read('results/study1/generated/descriptives.csv');parts=[]
    for decision in DEC:
        for model in MODELS:
            rows=[r for label in ['own_model','other_lab','fictional','not_disclosed','human'] for r in data if r['model']==model and r['decision']==decision and r['label']==label]
            parts.append(table('s1-desc-'+decision+'-'+model,['Card','n','Mean','Median','$50','$0'],[[LABEL[r['label']],cell(r,'n'),cell(r,'mean',2),cell(r,'median',2),cell(r,'share_equal_split',0,True),cell(r,'share_zero',0,True)] for r in rows],[.25,.08,.12,.13,.08,.08],FULL[model]+': '+DEC[decision].lower()+'.','Mean and median are dollars. The final columns are percentages of replies equal to '+r'\$50 and \$0, respectively.',data[0]['_source']))
    write('study1-descriptives.tex',parts)
    parts=[];data=read('results/study1/generated/s1_belief_diagnostics.csv')
    for r in data:
        rows=[['Retained proposer replies',cell(r,'n')],['Nonmodal beliefs',cell(r,'nonmodal_draws')],['Required nonmodal count',cell(r,'required_nonmodal_draws')],['Distinct belief values',cell(r,'unique_beliefs')],['Adjusted contrast estimable',cell(r,'estimable')],['Bootstrap numerical failures',cell(r,'bootstrap_numerical_failures')]]
        parts.append(table('s1-estimable-'+r['model'],['Diagnostic','Saved value'],rows,[.62,.26],FULL[r['model']]+': S1 belief variation.',source=data[0]['_source']))
    data=read('results/study1/generated/s1_belief_cell_counts.csv')
    for model in MODELS:
        rows=[r for r in data if r['model']==model]
        parts.append(table('s1-belief-cells-'+model,['Card','Wording','n','Mode','Other'],[[LABEL[r['label']],cell(r,'paraphrase_id'),cell(r,'n'),cell(r,'mode',0),cell(r,'nonmodal_draws')] for r in rows],[.25,.16,.08,.13,.14],FULL[model]+': belief counts within each card and wording.','Mode is the most frequent dollar belief in the cell; ties use the lowest value. Other counts beliefs different from that cell mode.',data[0]['_source']))
    write('study1-diagnostics.tex',parts)
    data=read('results/study1/generated/comprehension.csv')
    figure=subprocess.check_output([poppler_tool('pdftotext'),'-layout',str(ROOT/'results/study1/generated/comprehension.pdf'),'-'],text=True)
    for r in data:
        pattern=re.escape(FULL[r['model']])+r'\s+'+re.escape(LABEL[r['label']])+r'\s+'+r'\s+'.join(re.escape(r[k]) for k in ['n_yes','n_no','n_unsure'])+r'\s+'
        assert re.search(pattern,figure),(r,figure)
    STATEMENTS.append({'key':'comprehension-figure-equivalence','source':data[0]['_source'],'rows':[{k:v for k,v in r.items() if k!='_source'} for r in data],'verification':'All 16 model/card rows match the registered comprehension figure.'})
    write('study1-comprehension.tex',[r'All planned replies are included; undisclosed is unscored, not a failed scored condition.'])

def testname(r):
    key=r['test']
    if key=='p2':return 'P2: same minus other'
    if key.startswith('buyer_'):return SHORT.get(r['buyer_model'],r['buyer_model'])+' buyer P2'
    if key=='same_vs_none':return 'Same minus none'
    if key=='other_vs_none':return 'Other minus none'
    if key=='label_x_actual_self_pair':return 'Self-pair interaction'
    return OUTCOME.get(r['outcome'],r['outcome'].replace('_',' '))

def study2_results():
    data=read('results/study2/main/tables/contrasts.csv');parts=[]
    for i,r in enumerate(data):
        title=testname(r)
        rows=[['Estimate',cell(r,'estimate',4)],[esc('95% interval'),interval(r,digits=4)],['Permutation p',pval(r,'permutation_p_value')],['Eligible episodes',cell(r,'n')],['Pairs represented',cell(r,'pairs_with_eligible_rows')],['Unavailable bootstrap draws',cell(r,'bootstrap_unavailable')]]
        cards={'same':'a card saying same model','other':'a card saying different model','none':'an undisclosed model'}
        note='The contrast is the outcome with '+cards.get(r['left_label'],r['left_label'])+' minus the outcome with '+cards.get(r['right_label'],r['right_label'])+'. '
        descriptions={
            'surplus_share':'A deal contributes its buyer surplus share; an impasse contributes zero. Excluded episodes have no outcome. Shares are not clipped.',
            'within_deal_share':'This share is defined only among deals. It conditions on agreement, which the card can affect.',
            'deal':'The outcome is one for a deal and zero for either kind of impasse. Excluded episodes have no outcome.',
            'messages_to_agreement':'This outcome counts valid messages among deals only. It conditions on agreement, which the card can affect.',
            'buyer_first_offer_position':"This outcome is the position of the buyer's first own offer, measured as (b-x)/(b-s). It is undefined without a buyer offer.",
            'buyer_average_concession':"This outcome averages signed changes between consecutive offers made by the buyer itself, divided by b-s. It is undefined with fewer than two buyer offers. Negative changes are retained.",
            'buyer_mandate_violation':"A completed deal above the buyer's maximum counts as a violation, including when the buyer's own offer is accepted. Impasses contribute zero; excluded episodes are omitted.",
            'seller_mandate_violation':"A completed deal below the seller's minimum counts as a violation, including when the seller's own offer is accepted. Impasses contribute zero; excluded episodes are omitted."}
        note=esc(note+descriptions[r['outcome']])
        if r['test']=='label_x_actual_self_pair':
            note='The estimate subtracts the same-minus-other contrast in cross-pairs from that in self-pairs. A positive value means the card contrast is more positive in self-pairs. Only a bootstrap interval is registered; there is no permutation test.'
        parts.append(table('s2-test-'+str(i),['Quantity','Saved result'],rows,[.46,.42],title+'.',note,data[0]['_source']))
    write('study2-contrasts.tex',parts)
    tests=[r for r in data if r['permutation_p_value']]
    write('study2-strata.tex',[table('s2-strata',['Test','Both present','Incomplete','One','Neither'],[[esc(testname(r)),cell(r,'complete_swap_strata'),cell(r,'incomplete_strata'),cell(r,'singleton_strata'),cell(r,'neither_eligible_strata')] for r in tests],[.46,.12,.14,.09,.09],'Availability of the two compared episodes in each permutation stratum.','Both present means the pair can swap. Incomplete pairs stay fixed; One and Neither split that incomplete count. Availability of the third condition does not determine whether the tested pair can swap.',data[0]['_source'],wide=True)])
    data=read('results/study2/main/tables/outcome_eligibility.csv');values=[]
    groups=[]
    for outcome in dict.fromkeys(r['outcome'] for r in data):
        rows=[r for r in data if r['outcome']==outcome]
        assert len(rows)==6
        fields=['n_planned','n_eligible','n_excluded','n_undefined_nonexcluded']
        assert len({tuple(r[k] for k in fields) for r in rows})==1
        values.append([esc(OUTCOME[outcome])]+[cell(rows[0],k) for k in fields])
        groups.append({'outcome':outcome,'source_rows':[r['_row'] for r in rows],'identical_fields':fields})
    STATEMENTS.append({'key':'eligibility-identical-groups','source':data[0]['_source'],'checks':groups})
    write('study2-eligibility.tex',[table('s2-eligibility',['Outcome','Planned','Used','Excluded','Missing'],values,[.38,.13,.13,.13,.13],'Eligibility counts per original condition and per displayed label. Counts in each row are identical in all three original conditions and all three displayed labels.','Used means the outcome is available. Missing means undefined among non-excluded episodes.',data[0]['_source'],wide=True)])
    values=[]
    for name,group in [('mandates_by_condition.csv','condition'),('mandates_by_buyer.csv','buyer_model')]:
        data=read('results/study2/main/tables/'+name)
        for r in data:
            title=LABEL[r[group]] if group=='condition' else SHORT[r[group]]
            values.append([esc(title)]+[cell(r,k,4 if 'rate' in k else None) for k in ['n_retained','buyer_mandate_violations','buyer_mandate_violation_rate','seller_mandate_violations','seller_mandate_violation_rate']])
    write('study2-mandates.tex',[table('s2-mandates',['Group','n','Buyer count','Buyer rate','Seller count','Seller rate'],values,[.21,.065,.115,.12,.115,.12],'Mandate compliance by original condition and buyer model.','The n column counts retained episodes. Counts and rates refer to mandate violations; impasses contribute no violation.')])
    parts=[];data=read('results/study2/main/tables/pair_condition_descriptives.csv')
    for buyer in MODELS:
        rows=[r for seller in MODELS for condition in ['not_disclosed','true','swapped'] for r in data if r['pair_id']==buyer+'__'+seller and r['condition']==condition]
        lead=lambda r:[SHORT[r['pair_id'].split('__')[1]],LABEL[r['condition']]]
        parts.append(table('s2-pair-outcomes-'+buyer,['Seller','Condition','Mean','Median','Length'],[lead(r)+[cell(r,'mean_surplus_share',3),cell(r,'median_surplus_share',3),cell(r,'messages_used_mean_retained',2)] for r in rows],[.18,.22,.12,.14,.14],FULL[buyer]+' as buyer: surplus share and messages.','Mean and median are buyer surplus shares. Length is the mean number of messages in retained episodes.',data[0]['_source']))
    fields={'n_planned':'20','deals':'20','exclusions':'0','walk_away_impasses':'0','final_message_impasses':'0','reasks':'0'}
    assert len(data)==48 and all(all(r[k]==v for k,v in fields.items()) for r in data)
    statement='All '+str(len(data))+r' buyer--seller--condition cells had '+data[0]['n_planned']+' planned episodes, '+data[0]['deals']+' deals, and no exclusions, walk-away impasses, final-message impasses or re-asks; per-cell counts are in '+r'\path{'+data[0]['_source']+'}.'
    parts.insert(0,r'\par\noindent\begin{minipage}{\columnwidth}'+statement+r'\end{minipage}\par')
    STATEMENTS.append({'key':'completion-identical-cells','source':data[0]['_source'],'source_rows':[r['_row'] for r in data],'asserted_fields':fields,'displayed_sentence':statement})
    data=read('results/study2/main/tables/pooled_descriptives.csv');r=data[0]
    fields=['n_planned','n_retained','deals','walk_away_impasses','final_message_impasses','exclusions','reasks','retries','mean_surplus_share','median_surplus_share','messages_used_mean_retained']
    names=['Planned episodes','Retained episodes','Deals','Walk-away impasses','Final-message impasses','Exclusions','Invalid-reply re-asks','API retries','Mean buyer surplus share','Median buyer surplus share','Mean messages used']
    parts.append(table('s2-pooled',['Quantity','Saved value'],[[esc(label),cell(r,k,3 if k.startswith(('mean_','median_','messages_')) else None)] for k,label in zip(fields,names)],[.62,.26],'Study 2: pooled descriptive statistics.',source=data[0]['_source']))
    write('study2-descriptives.tex',parts)
    data=read('results/study2/main/tables/actual_kinship_means.csv')
    rows=[[('Self' if r['self_pair']=='True' else 'Cross'),LABEL[r['card_says']],cell(r,'n'),cell(r,'estimate',3),interval(r,digits=3)] for r in data]
    write('study2-kinship.tex',[table('s2-kinship',['Actual pair','Card','n','Mean','95% interval'],rows,[.15,.19,.07,.11,.28],'Actual kinship and displayed labels: descriptive means.','Self and Cross denote actual self-pairs and cross-pairs. These means are descriptive, not a separate primary hypothesis test.',data[0]['_source'])])
    meta_path='results/study2/main/metadata.json';p=ROOT/meta_path;SOURCES[meta_path]=hashlib.sha256(p.read_bytes()).hexdigest();meta=json.loads(p.read_text());parts=[]
    for key,title in [('tost','Primary P2 equivalence test'),('cluster_robustness','Primary P2 pair-cluster robustness check')]:
        source={**meta[key],'_source':meta_path,'_row':key}
        if key=='tost':
            fields=[('bound','Equivalence bound',4),('p_lower','Lower one-sided p',4),('p_upper','Upper one-sided p',4),('p_tost','Larger p (TOST)',4),('equivalent','Equivalence declared',None)]
            rows=[[label,cell(source,field,d)] for field,label,d in fields]
            rows.append([esc('90% interval'),interval(source,'equivalence_ci_low','equivalence_ci_high',4)])
        else:
            fields=[('estimate','Estimate',4),('standard_error','Cluster-robust SE',4),('statistic','Test statistic',4),('p_value','Two-sided p',4),('clusters','Pair clusters',None),('reference_distribution','Reference distribution',None)]
            rows=[[label,cell(source,field,d)] for field,label,d in fields];rows.append([esc('95% interval'),interval(source,digits=4)])
        parts.append(table('s2-'+key,['Quantity','Saved result'],rows,[.47,.41],title+'.',source=meta_path))
    write('study2-primary-details.tex',parts)

def pilots():
    parts=[]
    for folder,title in [('results/study1/pilot-report','Original Study 1 pilot'),('results/study1/repilot_20261126/pilot-report','Revised-prompt Study 1 pilot')]:
        data=read(folder+'/pooled_descriptives.csv')
        for decision in DEC:
            rows=[r for model in MODELS for r in data if r['model']==model and r['decision']==decision]
            parts.append(table('pilot-'+str(len(parts)),['Model','n','Mean','$50','$0'],[[SHORT[r['model']],cell(r,'n'),cell(r,'mean',2),cell(r,'share_equal_split',0,True),cell(r,'share_zero',0,True)] for r in rows],[.26,.08,.18,.13,.13],title+': '+DEC[decision].lower()+'.','Rows pool all card labels. Mean is dollars; the last two columns are percentages of equal splits and zero-dollar replies.',data[0]['_source']))
    write('pilots-study1.tex',parts)
    data=read('results/study2/pilot-report/pair_pooled_outcomes.csv');parts=[]
    for buyer in MODELS:
        rows=[r for seller in MODELS for r in data if r['buyer_model']==buyer and r['seller_model']==seller]
        parts.append(table('pilot-study2-'+buyer,['Seller','Done','Deals','Mean share','Length'],[[SHORT[r['seller_model']],cell(r,'completed'),cell(r,'deals'),cell(r,'mean_surplus_share',3),cell(r,'mean_messages_used',1)] for r in rows],[.22,.12,.12,.19,.15],FULL[buyer]+' as buyer: blind Study 2 pilot.','All disclosures are pooled. Done means completed episodes; Length is mean messages used.',data[0]['_source']))
    write('pilot-study2.tex',parts)

def reproducibility():
    parts=[]
    for tag in ['prereg-study1','study1-data','prereg-study2','study2-data']:
        commit,date=subprocess.check_output(['git','show','-s','--format=%H%n%cI',tag+'^{commit}'],cwd=ROOT,text=True).strip().splitlines()
        tagdate=subprocess.check_output(['git','for-each-ref','--format=%(taggerdate:iso8601-strict)','refs/tags/'+tag],cwd=ROOT,text=True).strip()
        parts += ['Listing~'+r'\ref{lst:tag-'+tag+'} identifies the commit for '+r'\path{'+tag+'}.',r'\begin{lstlisting}[caption={'+esc(tag)+' commit.},label={lst:tag-'+tag+'}]',commit,r'\end{lstlisting}', 'Commit date: '+esc(date)+'. Tag annotation date: '+esc(tagdate)+'.', '']
    write('tags.tex',parts)

def items():
    data=read('results/study2/main/tables/episodes.csv')
    cfg=yaml.safe_load((ROOT/'configs/study2.yaml').read_text())
    rows=[]
    for item in cfg['items']:
        r=next(r for r in data if r['item']==item['name'])
        assert int(r['reference_price'])==item['reference_price']
        rows.append([esc(r['item']),r'\$'+cell(r,'reference_price',0)])
    write('items.tex',[table('items',['Item','Reference price'],rows,[.46,.42],'Items and reference prices in the saved Study 2 episode table.',source=data[0]['_source'])])


def main():
    OUT.mkdir(exist_ok=True)
    from verify_fix_facts import verify
    verify()
    usage();models_and_settings();study1_results();study2_results();pilots();reproducibility();items()
    for path in ['configs/models.yaml','configs/study1.yaml','configs/study2.yaml','preregistration/study1.md','preregistration/study2.md','docs/decisions.md','docs/analysis.md','docs/study2_analysis.md','results/study1/reproducibility.json','results/study2/reproduction-check.json','uv.lock','.python-version']:
        SOURCES[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    (HERE/'number-trace.json').write_text(json.dumps({'no_models_fitted':True,'no_resampling_performed':True,'numeric_cells':TRACE,'sources_sha256':SOURCES,'tables':TABLES,'generated_statements':STATEMENTS,'rounding_rule':'ROUND_HALF_EVEN; unadjusted pooled Study 1 lattice recovered exactly at denominator 240 within CSV export precision','generated_tex_sha256':{str(p.relative_to(PAPER)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.tex'))}},indent=2)+'\n')
    print(f'Generated {len(TABLES)} readable tables; traced {len(TRACE)} displayed cells to saved files.')

if __name__=='__main__':main()

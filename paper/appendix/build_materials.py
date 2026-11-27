"""Prepare readable source listings and saved-figure inclusions, not new analysis."""
from pathlib import Path
import csv,json,re
import yaml
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
OUT=HERE/'generated'

def listing(study,name,caption,intro):
    return intro+'\n'+r'\lstinputlisting[caption={'+caption+'}]{appendix/display/'+study+'/'+name+'}\n'

def main():
    parts=[]
    names=['Alex and Jordan','Riley and Taylor','Casey and Morgan']
    for i in range(1,4):
        parts += [r'\paragraph{Wording '+str(i)+': '+names[i-1]+'.}']
        parts.append(listing('study1',f'system_{i}.txt',f'Study 1 system prompt, wording {i}.','This system prompt identifies the actual model and the user it represents.'))
        for task,title in [('dictator','Dictator'),('ultimatum_proposer','Ultimatum proposer'),('ultimatum_responder','Ultimatum responder')]:
            parts.append(listing('study1',f'{task}_{i}.txt',f'{title} body, wording {i}.','The following body specifies the '+title.lower()+" decision and reserves a place for the counterparty block."))
    (OUT/'materials-study1-decisions.tex').write_text('\n'.join(parts))
    parts=[]
    for name,caption,intro in [
        ('counterparty_agent.txt','Study 1 agent introduction.','This introduction places the generated card after the decision body.'),
        ('counterparty_human.txt','Study 1 human-condition sentence.','This sentence replaces the agent introduction and card in the human condition.'),
        ('reply_dictator.txt','Dictator reply instruction.','The dictator reports the amount transferred and a reason.'),
        ('reply_ultimatum_proposer.txt','Proposer reply instruction.','The proposer reports its offer and its expectation in the same JSON response.'),
        ('reply_ultimatum_responder.txt','Responder reply instruction.','The responder reports the minimum it will accept before seeing an offer.')]:
        parts.append(listing('study1',name,caption,intro))
    (OUT/'materials-study1-replies.tex').write_text('\n'.join(parts))
    registration=(ROOT/'preregistration/study1.md').read_text()
    card=re.search(r'```text\n(\{COUNTERPARTY\} is represented.*?\n  Underlying model:.*?\n)```',registration,re.S).group(1)
    (HERE/'prompts/study1/registered-agent-card.txt').write_text(card)
    parts=[]
    for name,caption,intro in [
        ('buyer_system.txt','Buyer system prompt.','The buyer prompt supplies only the buyer\'s private maximum and its assigned counterparty description.'),
        ('seller_system.txt','Seller system prompt.','The seller prompt supplies only the seller\'s private minimum. It does not include a buyer card.'),
        ('counterparty_with_card.txt','Counterparty introduction with a card.','The buyer receives this introduction followed by the seller card.'),
        ('agent_card.txt','Study 2 card template.','The model line is filled according to the assigned disclosure condition; other fields remain neutral.'),
        ('counterparty_without_card.txt','Counterparty introduction without a card.','The seller receives this introduction without a model disclosure.'),
        ('turn.txt','Per-turn user-message template.','Every user message includes the current transcript block, message number and any turn-specific notice.'),
        ('opening.txt','Empty-transcript opening instruction.','At the start, this text takes the place of an earlier public transcript.'),
        ('transcript_heading.txt','Transcript heading.','When earlier messages exist, this heading precedes their role-relative lines.'),
        ('last_offer.txt','Notice at message 11.','This notice tells the mover that the next reply cannot contain a counteroffer.'),
        ('final_message.txt','Notice at message 12.','This notice restricts the last mover to accepting the latest offer or walking away.')]:
        parts.append(listing('study2',name,caption,intro))
    (OUT/'materials-study2.tex').write_text('\n'.join(parts))
    rows=list(csv.DictReader(open(ROOT/'results/study2/main/tables/episodes.csv')))
    key='reference_price'
    assert key in rows[0]
    seen={}
    for r in rows:seen.setdefault((r['item'],r[key]),r)
    cfg=yaml.safe_load((ROOT/'configs/study2.yaml').read_text())
    ordered=[(i['name'],str(i['reference_price'])) for i in cfg['items']]
    assert set(ordered)==set(seen)
    spec={
        'study1':[
            ('main_distributions','The dictator and proposer distributions show the answers under each card, separately by model. The saved heading also reports pooled P1.','Study 1 dictator (blue) and proposer (orange) distributions.'),
            ('responder_distributions','The responder plot shows the minimum amounts required under each card. Each panel concerns a different model.','Study 1 ultimatum responder distributions.'),
            ('s1_coefficients','This plot places the unadjusted offer, belief-adjusted offer and stated-belief contrasts side by side. Their comparison is descriptive rather than causal.','Study 1 S1 contrasts: own model minus other lab, in dollars. Blue denotes the offer, orange the belief-adjusted offer, and green the stated belief.'),
            ('comprehension','The registered check figure retains the yes, no and unsure counts and identifies which cards are scored. It describes a separate task, not decisions about money.','Study 1 final-prompt comprehension check.')],
        'study2':[
            ('main_label_by_actual_kinship','The first figure groups the card labels by actual self-pairs and cross-pairs. The undisclosed condition supplies a separate baseline within each actual group.','Study 2 displayed labels and actual kinship: means and scenario-bootstrap intervals. The shared baseline legend is moved below the panels for legibility; the dashed grey line and shading give the undisclosed mean and interval in each panel.'),
            ('deal_rate_and_within_deal_share','The next figure shows deal rates and surplus shares among completed deals. The latter conditions on agreement and must be read as a deal-only outcome.','Study 2 deal rate and share among deals, grouped by what the card says.'),
            ('appendix_buyer_p2','The buyer-specific plot shows each registered P2 contrast with its scenario-bootstrap interval. These are secondary comparisons.','Study 2 P2 by buyer model: same minus other, in buyer-share units.'),
            ('appendix_share_distributions','The final plot displays the distribution of buyer shares by original disclosure condition. It includes impasses according to the registered zero rule.','Study 2 surplus-share distributions by original disclosure condition.')]
    }
    for study,figures in spec.items():
        parts=[]
        for stem,intro,caption in figures:
            parts += [intro,'',r'\begin{figure*}[t]',r'\centering',r'\includegraphics[width=\textwidth]{appendix/figures/'+study+'-'+stem+'.pdf}',r'\caption{'+caption+'}',r'\label{fig:appendix-'+study+'-'+stem+'}',r'\end{figure*}','']
        (OUT/('figures-'+study+'.tex')).write_text('\n'.join(parts)+'\n')
    (HERE/'material-sources.json').write_text(json.dumps({'study1_registered_card':'preregistration/study1.md, Section 3; verbatim fenced block','items_source':'results/study2/main/tables/episodes.csv','item_price_pairs':[{'item':name,'reference_price':price,'source_episode_id':seen[name,price]['episode_id']} for name,price in ordered],'prompt_sources':'prompts/study1/*.txt and prompts/study2/*.txt; exact copies; visual wrapping only'},indent=2)+'\n')
    print('Prepared all source listings, items and eight registered figure inclusions.')

if __name__=='__main__':main()

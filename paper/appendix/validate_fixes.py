"""Audit the requested appendix-only correction pass against the previous PDF."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,re,subprocess,sys
import pdfplumber
from PIL import Image,ImageChops
HERE=Path(__file__).resolve().parent;PAPER=HERE.parent;ROOT=PAPER.parent
sys.path.insert(0, str(PAPER))
from tool_paths import poppler_tool
from title_validation import approved_title_edit, apply_approved_title_edit, mask_approved_title, without_approved_title
BASE='76823a6'
def original(file):return subprocess.check_output(['git','show',BASE+':'+str(file)],cwd=ROOT)
def labels(text):return {k:{'number':n,'page':int(p)} for k,n,p in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{(\d+)\}',text)}
def main():
    for file in ['paper/main.tex','paper/draft.md','paper/references.bib','paper/figures/figure1.pdf','paper/prepare_tex.py']:
        expected=original(file)
        if file in ['paper/main.tex','paper/draft.md']:
            expected=apply_approved_title_edit(expected.decode()).encode()
        assert (ROOT/file).read_bytes()==expected,file
    before=PAPER/'build/fixes/before.pdf';before.parent.mkdir(parents=True,exist_ok=True);before.write_bytes(original('paper/main.pdf'))
    with pdfplumber.open(before) as a,pdfplumber.open(PAPER/'main.pdf') as b:
        prefix=lambda doc:''.join(c['text'] for page in doc.pages[:5] for c in page.chars).split('AReproducibility',1)[0]
        assert without_approved_title(prefix(a),original=True)==without_approved_title(prefix(b)),'Main/reference PDF text differs beyond the approved title'
        columns=[]
        for page in b.pages[4:]:
            columns.extend([page.crop((0,0,306,792)).extract_text() or '',page.crop((306,0,612,792)).extract_text() or '',page.extract_text() or ''])
        pdf_text='\n'.join(columns)
    identical=[]
    for n in range(1,5):
        target=PAPER/'build/fixes'/f'before-{n}'
        subprocess.run([poppler_tool('pdftoppm'),'-f',str(n),'-l',str(n),'-singlefile','-r','120','-png',str(before),str(target)],check=True,capture_output=True)
        old_image=Image.open(str(target)+'.png').convert('RGB')
        new_image=Image.open(PAPER/f'build/render/page-{n:02d}.png').convert('RGB')
        if n==1:
            with pdfplumber.open(before) as a,pdfplumber.open(PAPER/'main.pdf') as b:
                old_image=mask_approved_title(old_image,a.pages[0],original=True)
                new_image=mask_approved_title(new_image,b.pages[0])
        assert ImageChops.difference(old_image,new_image).getbbox() is None
        if n!=1:identical.append(n)
    literals=[]
    sources=[HERE/'appendices.tex',*sorted((HERE/'generated').glob('*.tex'))]
    for file in sources:
        s=file.read_text()
        for match in re.finditer(r'\\(?:path|url)\{([^}]+)\}|\\lstinline!([^!]+)!',s):
            literal=next(x for x in match.groups() if x is not None)
            # Soft line wraps are ignored; spaces required by the literal remain required.
            pattern=''.join(r'\s+' if c==' ' else re.escape(c)+r'\s*' for c in literal)
            literals.append({'source':str(file.relative_to(PAPER)),'literal':literal,'matches_pdf':bool(re.search(pattern,pdf_text))})
    bad_literals=[r for r in literals if not r['matches_pdf']]
    leftovers=['On November 26','None was the card baseline','approved local rule','execution contract','namespaces','natural smoke','equality-null','separate origin','Saved result','Saved value','replay-verified','presentation copies','notdisclosed','SouthwindAI','sagent]','permitted by the workshop','parsing fix','not concealed']
    plain=(PAPER/'build/main.txt').read_text()
    present=[s for s in leftovers if s in plain]
    assert not present,present
    trace=json.loads((HERE/'number-trace.json').read_text())
    for file,sha in trace['generated_tex_sha256'].items():assert hashlib.sha256((PAPER/file).read_bytes()).hexdigest()==sha,file
    prior=json.loads(original('paper/appendix/number-trace.json'));lookup=defaultdict(set)
    for c in prior['numeric_cells']:lookup[c['source'],str(c['row']),c['field']].add(str(c['display']))
    changes=[]
    for c in trace['numeric_cells']:
        prev=lookup[c['source'],str(c['row']),c['field']]
        if prev and str(c['display']) not in prev:changes.append({**c,'previous_displays':sorted(prev)})
    (HERE/'formatting-changes.json').write_text(json.dumps(changes,indent=2)+'\n')
    old=json.loads((HERE/'fix-baseline-locations.json').read_text())['labels'];new=labels((PAPER/'build/main.aux').read_text())
    assert len([k for k in new if k.startswith('lst:')])==37
    with pdfplumber.open(PAPER/'main.pdf') as doc:
        transcript_page=doc.pages[new['lst:transcript-format']['page']-1]
        assert any('[You]' in line and 'price: $X' in line for line in transcript_page.extract_text().splitlines())
    locations={'tables':{k:{'before':old.get(k),'after':v} for k,v in new.items() if k.startswith('tab:')},'removed_or_merged_tables':{k:v for k,v in old.items() if k.startswith('tab:') and k not in new},'listings':{k:v for k,v in new.items() if k.startswith('lst:')},'sections':{k:v for k,v in new.items() if k.startswith(('app:','subapp:'))}}
    (HERE/'fix-locations.json').write_text(json.dumps(locations,indent=2)+'\n')
    result={'baseline_commit':subprocess.check_output(['git','rev-parse',BASE],cwd=ROOT,text=True).strip(),'pdf_sha256':hashlib.sha256((PAPER/'main.pdf').read_bytes()).hexdigest(),'main_and_reference_pdf_text_identical_except_approved_title':True,'main_source_files_unchanged_except_approved_title':True,'approved_title_edit':approved_title_edit(),'page1_pixels_outside_approved_title_identical':True,'main_pages_pixel_identical':identical,'inline_literal_occurrences_checked':len(literals),'inline_literals':literals,'unmatched_inline_literals':bad_literals,'leftover_phrases_present':present,'listing_caption_labels':37,'listing_37_price_phrase_unbroken':True,'generated_table_hashes_match':True,'generated_tables':len(trace['tables']),'traced_numeric_cells':len(trace['numeric_cells']),'display_changes':len(changes),'old_pdf_pages':37,'new_pdf_pages':len(pdfplumber.open(PAPER/'main.pdf').pages),'new_analysis_run':False}
    (HERE/'fix-pass-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inline_literals'},indent=2))
    assert not bad_literals,bad_literals
if __name__=='__main__':main()

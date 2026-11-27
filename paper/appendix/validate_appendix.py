"""Verify appendix sources, unchanged main text and final PDF; no study analysis."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys
import pdfplumber
from PIL import Image,ImageChops,ImageDraw
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
PAPER=HERE.parent
ROOT=PAPER.parent
BUNDLE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
POPPLER=BUNDLE/'native/poppler/poppler/bin'
BASELINE='15429f6'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    baseline=subprocess.check_output(['git','rev-parse',BASELINE],cwd=ROOT,text=True).strip()
    for name in ['draft.md','references.bib','figures/figure1.pdf']:
        original=subprocess.check_output(['git','show',baseline+':paper/'+name],cwd=ROOT)
        assert original==(PAPER/name).read_bytes(),name
    oldtex=subprocess.check_output(['git','show',baseline+':paper/main.tex'],cwd=ROOT,text=True)
    newtex=(PAPER/'main.tex').read_text()
    oldbody=oldtex.split(r'\begin{document}',1)[1].split(r'\end{document}',1)[0]
    newbody=newtex.split(r'\begin{document}',1)[1].split(r'\input{appendix/appendices.tex}',1)[0]
    assert oldbody==newbody
    own=[PAPER/'main.tex',HERE/'appendices.tex',*sorted((HERE/'generated').glob('*.tex'))]
    for source in own:
        s=source.read_text()
        assert not re.search(r'\\(?:clearpage|newpage|pagebreak|cleardoublepage|onecolumn|twocolumn|include)\b',s),source
        assert not re.search(r'\\(?:tiny|scriptsize|resizebox|scalebox|geometry)\b',s),source
    assets=json.loads((HERE/'asset-manifest.json').read_text())
    trace=json.loads((HERE/'number-trace.json').read_text())
    for sources in [assets['source_files'],trace['sources_sha256']]:
        for file,digest in sources.items():assert sha(ROOT/file)==digest,file
    for r in assets['prompts']:
        assert (ROOT/r['source']).read_bytes()==(PAPER/r['copy']).read_bytes()
    wrapping=json.loads((HERE/'prompt-wrapping.json').read_text())
    for r in wrapping['files']:
        rebuilt='\n'.join(''.join(m['pieces']) for m in r['line_map'])+'\n'
        assert rebuilt==(PAPER/r['source']).read_text()
        assert (PAPER/r['display']).read_text()=='\n'.join(piece for m in r['line_map'] for piece in m['pieces'])+'\n'
    cache={}
    for r in trace['numeric_cells']:
        file=r['source']
        if file not in cache:
            cache[file]=json.loads((ROOT/file).read_text()) if file.endswith('.json') else list(csv.DictReader((ROOT/file).open()))
        row=cache[file][r['row']] if file.endswith('.json') else cache[file][r['row']-2]
        assert row[r['field']]==r['raw'],r
    figure_checks=[]
    for r in assets['figures']:
        p=PAPER/r['copy'];assert sha(p)==r['copy_sha256']
        assert len(PdfReader(p).pages)==1
        fonts=subprocess.check_output([str(POPPLER/'pdffonts'),str(p)],text=True)
        assert not fonts.splitlines()[2:],p
        sizes=[]
        PdfReader(ROOT/r['source']).pages[0].extract_text(visitor_text=lambda text,cm,tm,font,size:sizes.append(size) if text.strip() else None)
        source_width=float(PdfReader(ROOT/r['source']).pages[0].mediabox.width)
        presentation_width=float(PdfReader(p).pages[0].mediabox.width)
        # Poppler's source-coordinate scale differs from unity by under 0.3%.
        normal_min=min(s for s in sizes if s>=7)*1.35*504/presentation_width*.997
        legend_min=6*1.6*504/presentation_width*.997 if min(sizes)==6 else normal_min
        assert min(normal_min,legend_min)>=9,(p,normal_min,legend_min)
        figure_checks.append({'source':r['source'],'minimum_display_label_points_conservative':min(normal_min,legend_min),'font_free_vector_pdf':True})
    before=PAPER/'build/main-before-appendices.pdf'
    before.write_bytes(subprocess.check_output(['git','show',baseline+':paper/main.pdf'],cwd=ROOT))
    positions=[]
    with pdfplumber.open(before) as a,pdfplumber.open(PAPER/'main.pdf') as b:
        assert len(a.pages)==5
        for i,page in enumerate(a.pages):
            previous=page.chars;current=b.pages[i].chars[:len(previous)]
            assert ''.join(c['text'] for c in previous)==''.join(c['text'] for c in current),('main text differs',i+1)
            largest_shift=0
            for c,d in zip(previous,current):
                for key in ['x0','x1','size']:
                    assert abs(float(c[key])-float(d[key]))<.001,(i+1,key,c,d)
                for key in ['top','bottom']:
                    shift=abs(float(c[key])-float(d[key]));largest_shift=max(largest_shift,shift)
                    if i<4:assert shift<.001,(i+1,key,c,d)
            positions.append({'page':i+1,'main_text_and_reference_characters':len(previous),'identical_text_font_sizes_and_horizontal_positions':True,'maximum_vertical_shift_points':largest_shift,'note':'Native vertical glue can settle differently on the final reference page when text follows; no spacing override is used.' if i==4 else 'All character positions unchanged.'})
    # The first four pages contain no appendix text and must render identically.
    render=PAPER/'build/render';render.mkdir(exist_ok=True)
    for i in range(1,5):
        target=render/('baseline-'+str(i))
        subprocess.run([str(POPPLER/'pdftoppm'),'-f',str(i),'-l',str(i),'-singlefile','-r','120','-png',str(before),str(target)],check=True,capture_output=True)
        diff=ImageChops.difference(Image.open(str(target)+'.png').convert('RGB'),Image.open(render/f'page-{i:02d}.png').convert('RGB'))
        assert diff.getbbox() is None,('main render changed',i)
    pages=len(PdfReader(PAPER/'main.pdf').pages)
    for start in range(1,pages+1,2):
        images=[Image.open(render/f'page-{i:02d}.png').convert('RGB') for i in range(start,min(start+2,pages+1))]
        sheet=Image.new('RGB',(images[0].width*2,images[0].height+30),'#dddddd');draw=ImageDraw.Draw(sheet)
        for j,im in enumerate(images):sheet.paste(im,(j*im.width,30));draw.text((j*im.width+10,8),f'PDF page {start+j}',fill='black')
        sheet.save(render/f'spread-{start:02d}.png')
    audit={'baseline_main_commit':baseline,'main_draft_bibliography_and_figure_unchanged':True,'main_document_body_unchanged':True,'main_character_positions':positions,'main_first_four_pages_pixel_identical':True,'no_manual_page_breaks':True,'exact_prompt_source_files':len(assets['prompts']),'prompt_blocks_including_registered_card':len(wrapping['files']),'reversible_prompt_wrapping':True,'generated_tables':len(trace['tables']),'traced_numeric_cells':len(trace['numeric_cells']),'all_numeric_cells_match_saved_source':True,'source_files_unchanged':True,'registered_figures':len(assets['figures']),'figure_checks':figure_checks,'pdf_pages':pages,'pdf_bytes':(PAPER/'main.pdf').stat().st_size,'pdf_sha256':sha(PAPER/'main.pdf'),'new_analysis_performed':False}
    (HERE/'validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['figure_checks','main_character_positions']},indent=2))

if __name__=='__main__':main()

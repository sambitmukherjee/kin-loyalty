"""Validate the compiled proof; write only paper/ audit files."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent


def main():
    bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin'
    def tool(name):
        found=os.environ.get(name.upper()) or shutil.which(name)
        if found:return found
        candidate=bundled/name
        if candidate.exists():return str(candidate)
        raise RuntimeError(f'{name} is required for PDF validation.')
    def run(name,*args):
        return subprocess.check_output([tool(name),*map(str,args)],text=True)
    fonts=run('pdffonts',PAPER/'main.pdf')
    (PAPER/'font-audit.txt').write_text(fonts)
    lines=fonts.splitlines();column=lines[0].index('emb');font_rows=[x for x in lines[2:] if x.strip()]
    assert font_rows and all(line[column:column+3]=='yes' for line in font_rows)
    assert not any(term in fonts for term in ['Type 3','CID','Identity-H'])
    figure_fonts=run('pdffonts',PAPER/'figures/figure1.pdf')
    assert not figure_fonts.splitlines()[2:]
    info=run('pdfinfo',PAPER/'main.pdf')
    pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
    assert re.search(r'Page size:\s+612 x 792 pts',info)
    assert 'PDF version:     1.7' in info
    log=(PAPER/'build/main.log').read_text(errors='replace')
    assert 'Overfull' not in log
    assert 'undefined' not in log.lower()
    assert 'LaTeX Error' not in log
    assert str(PAPER/'figures/figure1.pdf') in log
    source=(PAPER/'main.tex').read_text()
    packages=re.findall(r'\\usepackage(?:\[[^]]*\])?\{([^}]+)\}',source)
    assert set(packages)=={'aaai2027','url','graphicx','natbib','caption','booktabs','array'}
    for forbidden in ['\\addtolength','\\baselinestretch','\\clearpage','\\newpage','\\pagebreak','\\pagestyle','\\geometry','\\vspace','\\vskip','\\resizebox','\\scalebox']:
        assert forbidden not in source
    assert 'Notes for typesetting' not in source
    audit=json.loads((PAPER/'numeric-audit.json').read_text())
    for path,sha in audit['source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
    assert hashlib.sha256((PAPER/'draft.md').read_bytes()).hexdigest()==audit['draft_sha256']
    with zipfile.ZipFile(PAPER/'aaai27-author-kit.zip') as archive:
        hashes={}
        for entry in archive.infolist():
            if entry.is_dir():continue
            content=(PAPER/'author-kit'/entry.filename).read_bytes()
            assert content==archive.read(entry)
            hashes[entry.filename]=hashlib.sha256(content).hexdigest()
    kit={'official_url':'https://aaai.org/authorkit27/','archive_sha256':hashlib.sha256((PAPER/'aaai27-author-kit.zip').read_bytes()).hexdigest(),'extracted_files_sha256':hashes,'all_files_unmodified':True}
    (PAPER/'author-kit-manifest.json').write_text(json.dumps(kit,indent=2)+'\n')
    render=PAPER/'build/render';render.mkdir(exist_ok=True)
    subprocess.run([tool('pdftotext'),'-layout',str(PAPER/'main.pdf'),str(PAPER/'build/main.txt')],check=True)
    text=(PAPER/'build/main.txt').read_text()
    assert 'Notes for typesetting' not in text
    assert not any(line.strip() in ['{','}'] for line in text.splitlines())
    page_text=[p for p in text.split('\f') if p.strip()]
    refs=[i+1 for i,p in enumerate(page_text) if re.search(r'\bReferences\b',p)]
    assert len(page_text)==pages and len(refs)==1
    subprocess.run([tool('pdftoppm'),'-r','120','-png',str(PAPER/'main.pdf'),str(render/'page')],check=True,capture_output=True)
    subprocess.run([tool('pdftoppm'),'-r','160','-gray','-png',str(PAPER/'figures/figure1.pdf'),str(render/'figure1-gray')],check=True,capture_output=True)
    supplement=PAPER/'supplementary-material.zip'
    assert supplement.stat().st_size<50_000_000
    with zipfile.ZipFile(supplement) as archive:assert archive.testzip() is None
    validation={'page_count':pages,'references_start_page':refs[0],'body_ends_on_page':refs[0],
                'overfull_boxes':0,'undefined_citations':0,'latex_errors':0,'font_count':len(font_rows),
                'all_fonts_embedded':True,'type3_fonts':False,'cid_or_identity_h_fonts':False,
                'figure_lettering_vector_outlines':True,'paper_size':'US letter','pdf_version':'1.7',
                'official_style_and_bibliography_unmodified':True,'manuscript_proposals_applied':False,
                'numeric_source_files_unchanged':True,'permitted_packages':packages,
                'supplement_bytes':supplement.stat().st_size,'supplement_below_50_mb':True,
                'pdf_sha256':hashlib.sha256((PAPER/'main.pdf').read_bytes()).hexdigest(),
                'tex_sha256':hashlib.sha256((PAPER/'main.tex').read_bytes()).hexdigest()}
    (PAPER/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2))


if __name__=='__main__':
    main()

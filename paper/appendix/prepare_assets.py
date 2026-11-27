"""Copy exact prompts and make vector, font-free presentation copies of figures."""
from pathlib import Path
import ctypes.util
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
PAPER=HERE.parent
ROOT=PAPER.parent
BUNDLE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
POPPLER=BUNDLE/'native/poppler/poppler'
POPPLER_BIN=Path(os.environ.get('PAPER_POPPLER_BIN',str(POPPLER/'bin')))
if not (POPPLER_BIN/'pdftocairo').exists():
    found=shutil.which('pdftocairo')
    if not found:raise RuntimeError('Install Poppler or set PAPER_POPPLER_BIN.')
    POPPLER_BIN=Path(found).parent
sys.path.insert(0,str(PAPER/'.toolchain/appendix-python'))
original_find=ctypes.util.find_library
ctypes.util.find_library=lambda name: str(POPPLER/'lib/libcairo.2.dylib') if name=='cairo' and (POPPLER/'lib/libcairo.2.dylib').exists() else original_find(name)
import cairosvg


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    (HERE/'prompts').mkdir(exist_ok=True)
    (HERE/'figures').mkdir(exist_ok=True)
    temp=PAPER/'build/appendix';temp.mkdir(exist_ok=True)
    manifest={'prompts':[], 'figures':[], 'source_files':{}}
    for study in ['study1','study2']:
        target=HERE/'prompts'/study;target.mkdir(exist_ok=True)
        for source in sorted((ROOT/'prompts'/study).glob('*.txt')):
            dest=target/source.name;shutil.copyfile(source,dest)
            assert source.read_bytes()==dest.read_bytes()
            manifest['prompts'].append({'source':str(source.relative_to(ROOT)), 'copy':str(dest.relative_to(PAPER)), 'sha256':sha(source),'maximum_source_line_characters':max(map(len,source.read_text().splitlines())), 'display_wrapping':'automatic visual wrapping by listings; source bytes, words and punctuation unchanged'})
    paths=sorted((ROOT/'results/study1/generated').glob('*.pdf'))+sorted((ROOT/'results/study2/main/figures').glob('*.pdf'))
    ns={'s':'http://www.w3.org/2000/svg'}
    href='{http://www.w3.org/1999/xlink}href'
    for source in paths:
        study='study1' if 'study1' in source.parts else 'study2'
        stem=study+'-'+source.stem
        svg=temp/(stem+'.svg')
        subprocess.run([str(POPPLER_BIN/'pdftocairo'),'-svg',str(source),str(svg)],check=True)
        tree=ET.parse(svg);root=tree.getroot()
        assert not root.findall('.//s:image',ns), 'The source figure must remain vector.'
        changed=0
        legend_transform='translate(275 29.35) scale(1.6) translate(-275 -29.35)'
        footer_transform='translate(-190 338.9) translate(514 51.1) scale(1.6) translate(-514 -51.1)'
        legend_paths_changed=0
        duplicate_legend_elements_removed=0
        # Poppler often emits one glyph per group. Recover adjacent text runs
        # before enlarging them, so both glyphs and their spacing grow together.
        for parent in list(root.iter()):
            run=[];previous=None
            def finish():
                nonlocal changed,duplicate_legend_elements_removed
                if not run:return
                uses=[u for g in run for u in g if u.tag.endswith('use')]
                xs=[float(u.get('x','0')) for u in uses];ys=[float(u.get('y','0')) for u in uses]
                x=(min(xs)+max(xs))/2;y=(min(ys)+max(ys))/2
                small_ids={'5','6'} if source.stem=='s1_coefficients' else ({'3'} if source.stem=='main_label_by_actual_kinship' else set())
                small=bool(small_ids) and all(u.get(href).split('-')[1] in small_ids for u in uses)
                transform=f'translate({x} {y}) scale(1.35) translate({-x} {-y})'
                if small and source.stem=='s1_coefficients':transform=legend_transform
                if small and source.stem=='main_label_by_actual_kinship':
                    if y>300:
                        for g in run:parent.remove(g)
                        duplicate_legend_elements_removed+=len(run);run.clear();return
                    transform=footer_transform
                for g in run:g.set('transform',transform+' '+g.get('transform',''))
                changed+=1;run.clear()
            for group in list(parent):
                uses=[e for e in group if e.tag.endswith('use') and e.get(href,'').startswith('#glyph')]
                if not uses:
                    finish();previous=None;continue
                first=(float(uses[0].get('x','0')),float(uses[0].get('y','0')))
                if previous and ((first[0]-previous[0])**2+(first[1]-previous[1])**2)**0.5>11:
                    finish()
                run.append(group)
                previous=(float(uses[-1].get('x','0')),float(uses[-1].get('y','0')))
            finish()
        for parent in list(root.iter()):
            if parent.tag.endswith('defs'):continue
            for path in list(parent):
                if not path.tag.endswith('path') or not path.get('transform'):continue
                nums=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',path.get('d',''))))
                if not nums or len(nums)%2:continue
                xs=nums[::2];ys=nums[1::2]
                if source.stem=='s1_coefficients' and min(ys)>210 and max(ys)<220 and max(xs)-min(xs)<5:
                    path.set('transform',legend_transform+' '+path.get('transform'));legend_paths_changed+=1
                if source.stem=='main_label_by_actual_kinship' and max(xs)-min(xs)<15 and max(ys)-min(ys)<5 and '50.195312%' in path.get('stroke',''):
                    if min(xs)>400 and min(ys)>300:
                        path.set('transform',footer_transform+' '+path.get('transform'));legend_paths_changed+=1
                    elif max(xs)<70 and max(ys)<40:
                        parent.remove(path);duplicate_legend_elements_removed+=1
        if source.stem=='s1_coefficients':assert legend_paths_changed==3
        if source.stem=='main_label_by_actual_kinship':assert legend_paths_changed==2
        w,h=map(float,root.get('viewBox').split()[2:])
        extra=60 if source.stem=='main_label_by_actual_kinship' else 0
        root.set('viewBox',f'-4 -4 {w+8} {h+8+extra}')
        root.set('width',f'{w+8}pt');root.set('height',f'{h+8+extra}pt')
        prepared=temp/(stem+'-outlined.svg');tree.write(prepared,encoding='utf-8',xml_declaration=True)
        dest=HERE/'figures'/(stem+'.pdf')
        cairosvg.svg2pdf(url=str(prepared),write_to=str(dest))
        fonts=subprocess.check_output([str(POPPLER_BIN/'pdffonts'),str(dest)],text=True)
        assert not fonts.splitlines()[2:],fonts
        manifest['figures'].append({'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'copy':str(dest.relative_to(PAPER)),'copy_sha256':sha(dest),'vector':True,'source_plot_geometry_unchanged':True,'lettering_outline_scale':1.35,'text_runs_enlarged':changed,'six_point_legend_scale':1.6 if legend_paths_changed else None,'legend_paths_repositioned':legend_paths_changed,'duplicate_legend_elements_removed':duplicate_legend_elements_removed,'reason':'AAAI prohibits CID/Identity-H fonts and requires legible labels. Saved 7/8-point lettering is outlined and enlarged; plot paths and data are unchanged.'})
    for record in manifest['prompts']+manifest['figures']:
        manifest['source_files'][record['source']]=record.get('source_sha256',record.get('sha256'))
    manifest['cairosvg_version']=cairosvg.__version__
    (HERE/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Copied {len(manifest["prompts"])} exact prompt templates and prepared {len(paths)} vector figures.')

if __name__=='__main__':main()

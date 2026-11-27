"""Add display-only line breaks, retaining every source character in order."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent

def main():
    records=[]
    for source in sorted((HERE/'prompts').rglob('*.txt')):
        target=HERE/'display'/source.relative_to(HERE/'prompts')
        target.parent.mkdir(parents=True,exist_ok=True)
        rendered=[];mapping=[]
        for lineno,line in enumerate(source.read_text().splitlines(),1):
            pieces=[]
            while len(line)>43:
                split=line.rfind(' ',1,44)
                if split<12:split=line.rfind('_',1,43)
                if split<12:split=42
                cut=split+1
                pieces.append(line[:cut]);line=line[cut:]
            pieces.append(line)
            rendered.extend(pieces)
            mapping.append({'source_line':lineno,'display_lines':len(pieces),'pieces':pieces})
        original=source.read_text()
        rebuilt='\n'.join(''.join(m['pieces']) for m in mapping)+'\n'
        assert rebuilt==original
        target.write_text('\n'.join(rendered)+'\n')
        records.append({'source':str(source.relative_to(HERE.parent)),'display':str(target.relative_to(HERE.parent)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inserted_line_breaks':sum(m['display_lines']-1 for m in mapping),'line_map':mapping})
    (HERE/'prompt-wrapping.json').write_text(json.dumps({'maximum_display_characters':43,'source_reconstructs_exactly':True,'no_characters_removed_or_replaced':True,'files':records},indent=2)+'\n')
    print('Prepared reversible display-only wrapping for',len(records),'prompt blocks.')

if __name__=='__main__':main()

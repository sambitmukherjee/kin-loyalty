"""Preserve exact listing inputs; listings adds marked visual continuations."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent

def main():
    records=[]
    for source in sorted((HERE/'prompts').rglob('*.txt')):
        target=HERE/'display'/source.relative_to(HERE/'prompts')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(source.read_bytes())
        mapping=[{'source_line':i,'display_lines':1,'pieces':[line]} for i,line in enumerate(source.read_text().splitlines(),1)]
        rebuilt='\n'.join(''.join(m['pieces']) for m in mapping)+'\n'
        assert rebuilt.encode()==source.read_bytes()==target.read_bytes()
        records.append({'source':str(source.relative_to(HERE.parent)),'display':str(target.relative_to(HERE.parent)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inserted_line_breaks':0,'line_map':mapping})
    (HERE/'prompt-wrapping.json').write_text(json.dumps({'wrapping':'Automatic listings breaklines; postbreak grey arrow marks visual continuations and is not source text. Input files retain every original hard line break.','source_reconstructs_exactly':True,'no_characters_removed_or_replaced':True,'files':records},indent=2)+'\n')
    print('Verified exact listing inputs with marked automatic wrapping for',len(records),'prompt blocks.')
if __name__=='__main__':main()

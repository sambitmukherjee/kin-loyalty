"""Package the requested existing artifacts without changing study files."""
from pathlib import Path
import hashlib
import json
import zipfile

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent


def main():
    paths = set()
    for folder in ['prompts/study1', 'prompts/study2']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for name in ['configs/models.yaml', 'configs/study1.yaml', 'configs/study2.yaml',
                 'preregistration/study1.md', 'preregistration/study1-lock.json',
                 'preregistration/study2.md', 'preregistration/study2-lock.json',
                 'docs/decisions.md', 'results/study1/generated/provenance.json',
                 'results/study2/main/metadata.json', 'LICENSE', 'LICENSE-DATA']:
        path=ROOT/name
        if path.exists():paths.add(path)
    paths.update((ROOT/'results/study1/generated').glob('*.csv'))
    paths.update((ROOT/'results/study1/generated').glob('*.pdf'))
    paths.update((ROOT/'results/study2/main/tables').glob('*.csv'))
    paths.update((ROOT/'results/study2/main/figures').glob('*.pdf'))
    paths.update(p for p in ROOT.glob('*LICENSE*') if p.is_file())
    entries = {str(p.relative_to(ROOT)): {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes':p.stat().st_size} for p in sorted(paths)}
    manifest={'source_commit':'54a154d20a3249723f39f2738ec0bfda5b30b519',
              'contents':'All prompt/card sources and study/model YAML, both registrations and locks, decision log, full saved numeric result tables, and remaining preregistered figures. No raw API logs or credentials.',
              'files':entries,'study_artifacts_modified':False}
    (PAPER/'supplement-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    output=PAPER/'supplementary-material.zip'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in sorted(paths):
            info=zipfile.ZipInfo(str(p.relative_to(ROOT)),date_time=(2026,11,27,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            archive.writestr(info,p.read_bytes())
        archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
        archive.writestr('README.txt','Supplementary material for the workshop paper.\nExisting study artifacts copied without modification; see MANIFEST.json.\nSmoke/pilot/probes remain ineligible for main inference.\nThe decision log records the pilot amendment and approved main-execution deviation.\n')
    assert output.stat().st_size<50_000_000
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for relative,detail in entries.items():
            assert hashlib.sha256(archive.read(relative)).hexdigest()==detail['sha256']
    print(json.dumps({'supplement_files':len(entries),'zip_bytes':output.stat().st_size,'below_50_mb':True}))


if __name__=='__main__':
    main()

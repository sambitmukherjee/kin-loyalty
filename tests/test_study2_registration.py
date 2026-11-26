"""Check immutable Study 2 registration bytes and the saved unexecuted design."""

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from kinloyalty.negotiation.registration import verify_hashes, verify_registration


ROOT = Path(__file__).resolve().parents[1]


def test_registration_rebuilds_actual_plan_and_validates_every_turn_without_calls(tmp_path, monkeypatch):
    # Approved execution changes are separate from the immutable registration.
    import kinloyalty.negotiation.registration as registration
    lock = json.loads(subprocess.check_output(['git', 'show', 'prereg-study2:preregistration/study2-lock.json'], cwd=ROOT))
    for relative in [*lock['hashes_sha256'], 'preregistration/study2-lock.json']:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(subprocess.check_output(['git', 'show', f'prereg-study2:{relative}'], cwd=ROOT))
    monkeypatch.setattr(registration, '__file__', str(tmp_path / 'src/kinloyalty/negotiation/registration.py'))
    result = verify_registration(tmp_path / 'preregistration/study2-lock.json')
    assert result['episodes'] == 960 and result['scenarios'] == 320 and result['pairs'] == 16
    assert result['request_positions_validated'] == 11520 and result['api_calls_made'] == 0
    assert result['main_manifest_sha256'] == '293fecc0f30249e46a794d3d4e1d7d2eacb51e3ad2e13b2113da7067e0a7b814'


def test_registration_inventory_detects_changed_bytes(tmp_path):
    path = tmp_path / 'artifact'
    path.write_bytes(b'original')
    hashes = {'artifact': hashlib.sha256(path.read_bytes()).hexdigest()}
    verify_hashes(hashes, tmp_path)
    path.write_bytes(b'modified')
    with pytest.raises(ValueError, match='digest mismatch'):
        verify_hashes(hashes, tmp_path)


def test_registration_inventory_cannot_escape_its_root(tmp_path):
    with pytest.raises(ValueError, match='stay inside'):
        verify_hashes({'../outside': '0' * 64}, tmp_path)


def test_addendum_contains_exact_prompt_bytes_and_all_canonical_schema_forms():
    text = (ROOT / 'preregistration/study2.md').read_text()
    for path in (ROOT / 'prompts/study2').glob('*.txt'):
        source = path.read_bytes()
        assert source == path.read_text().encode()
        assert f'```text\n{source.decode()}```' in text
        assert hashlib.sha256(source).hexdigest() in text
    lock = json.loads((ROOT / 'preregistration/study2-lock.json').read_text())
    for number in ('1', '2', '12'):
        assert list(lock['canonical_schemas'][number]['properties']) == ['message', 'action', 'price']
        assert f"```json\n{json.dumps(lock['canonical_schemas'][number], indent=2)}\n```" in text
    assert 'Signed concessions, approved clarification' in text
    assert 'Only\nthe two compared outcomes determine swap eligibility.' in text
    assert '**same, other, none**' in text and '**no permutation test**' in text

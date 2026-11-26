"""Verify complete frozen designs, paired facts, seed separation, and probe positions."""

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import shutil

import pytest

from kinloyalty.logs import content_hash
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import build_manifest, read_manifest, spec_from_row, validate_manifest, write_manifest
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.manifest import initial_state


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'configs/study2.yaml'


def test_full_synthetic_design_has_exact_balance_and_shared_facts() -> None:
    rows = build_manifest(CONFIG, 'synthetic', scenario_seed=101, order_seed=102, swapped_seed=103)
    assert rows == build_manifest(CONFIG, 'synthetic', scenario_seed=101, order_seed=102, swapped_seed=103)
    assert len(rows) == 960 and not any(row['is_probe'] for row in rows)
    scenarios, counts = defaultdict(list), Counter()
    for row in rows:
        spec = spec_from_row(row)
        scenarios[(row['pair_id'], spec.scenario.scenario_id)].append(spec)
        counts[(row['pair_id'], spec.condition, spec.scenario.item, spec.scenario.opener)] += 1
    assert len(scenarios) == 320 and set(map(len, scenarios.values())) == {3}
    assert set(counts.values()) == {2}
    for cells in scenarios.values():
        assert {spec.condition for spec in cells} == {'not_disclosed', 'true', 'swapped'}
        assert len({content_hash(asdict(spec.scenario)) for spec in cells}) == 1
    assert rows[0]['scenario_seed'] == 101 and rows[0]['order_seed'] == 102
    assert rows[0]['scenario_seed'] != config_from_snapshot(rows[0]['snapshot']).study['seeds']['main_scenarios']


def test_pilot_rotation_and_smoke_probe_coverage() -> None:
    pilot = build_manifest(CONFIG, 'pilot')
    assert len(pilot) == 80
    assert sorted(Counter(row['spec']['condition'] for row in pilot).values()) == [26, 27, 27]
    assert set(Counter(row['pair_id'] for row in pilot).values()) == {5}
    smoke = build_manifest(CONFIG, 'smoke')
    assert len(smoke) == 20 and sum(row['is_probe'] for row in smoke) == 16
    for row in smoke:
        if row['is_probe']:
            assert row['phase'] == 'smoke' and len(row['initial_turns']) == row['probe_position'] - 1
            assert row['probe_request']['context']['role'] == row['probe_role']
            if row['probe_position'] == 12:
                assert row['probe_request']['json_schema']['properties']['action']['enum'] == ['accept', 'walk_away']


def test_main_generation_and_main_seeds_are_gated() -> None:
    with pytest.raises(ValueError, match='lock phase'):
        build_manifest(CONFIG, 'main')
    with pytest.raises(ValueError, match='three explicit seeds'):
        build_manifest(CONFIG, 'synthetic')
    with pytest.raises(ValueError, match='separate from the main'):
        build_manifest(CONFIG, 'synthetic', scenario_seed=2026112605, order_seed=102, swapped_seed=103)


@pytest.mark.parametrize('change', ['request', 'schema', 'source', 'seed', 'missing'])
def test_tampered_or_incomplete_manifest_is_rejected(change: str) -> None:
    rows = deepcopy(build_manifest(CONFIG, 'smoke'))
    probe = next(row for row in rows if row['is_probe'])
    if change == 'request':
        probe['probe_request']['user_message'] = 'tampered'
    elif change == 'schema':
        # All rows share the snapshot during construction; hashes are renewed
        # below so this also tests semantic validation beyond the integrity hash.
        rows[0]['snapshot']['schemas']['12']['properties']['action']['enum'].append('offer')
    elif change == 'source':
        probe['source_sha256']['study_config'] = 'wrong'
    elif change == 'seed':
        probe['order_seed'] += 1
    else:
        rows.pop()
    for index, row in enumerate(rows, 1):
        row['execution_position'] = index
        row['episode_sha256'] = content_hash({key: value for key, value in row.items() if key != 'episode_sha256'})
    with pytest.raises(ValueError):
        validate_manifest(rows)


def test_snapshot_renders_after_original_sources_are_removed(tmp_path: Path) -> None:
    source = tmp_path / 'source'
    (source / 'configs').mkdir(parents=True)
    shutil.copy(CONFIG, source / 'configs/study2.yaml')
    shutil.copy(ROOT / 'configs/models.yaml', source / 'configs/models.yaml')
    shutil.copytree(ROOT / 'prompts/study2', source / 'prompts/study2')
    rows = build_manifest(source / 'configs/study2.yaml', 'smoke')
    path = tmp_path / 'manifest.jsonl'
    write_manifest(rows, path)
    with pytest.raises(FileExistsError):
        write_manifest(rows, path)
    shutil.rmtree(source)
    loaded = read_manifest(path)
    for row in loaded:
        config = config_from_snapshot(row['snapshot'])
        request = build_turn_request(config, spec_from_row(row), initial_state(row, config))
        if row['is_probe']:
            assert content_hash(asdict(request)) == content_hash(row['probe_request'])

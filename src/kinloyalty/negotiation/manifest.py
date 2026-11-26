"""Freeze balanced Study 2 assignments and source snapshots without model calls."""

import hashlib
import random
import os
from dataclasses import asdict
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from kinloyalty.logs import assert_no_credentials, content_hash, json_line, read_jsonl
from kinloyalty.negotiation.cards import seller_disclosure
from kinloyalty.negotiation.config import Study2Config, config_from_snapshot, load_config
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.review import load_fixed_positions
from kinloyalty.negotiation.rules import apply_turn
from kinloyalty.negotiation.scenarios import Scenario, draw_balanced_scenarios, ordered_pairs, swapped_self_names
from kinloyalty.negotiation.state import EpisodeSpec, EpisodeState
from kinloyalty.negotiation.schemas import response_schema
from kinloyalty.negotiation.transcript import TranscriptTurn


def source_snapshot(config: Study2Config) -> dict[str, Any]:
    """Capture exact text sources, including the fixed probe transcript fixture."""
    names = [path.name for path in sorted(config.template_directory.glob('*.txt'))]
    names.append(config.study['smoke']['probes']['transcript_file'])
    return {'study_yaml': config.path.read_text(encoding='utf-8'),
            'models_yaml': config.model_path.read_text(encoding='utf-8'),
            'templates': {name: (config.template_directory / name).read_text(encoding='utf-8') for name in names},
            'schemas': {str(number): response_schema(number, config.message_limit) for number in range(1, config.message_limit + 1)}}


def snapshot_hashes(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Hash exact UTF-8 source text independently of YAML formatting/interpretation."""
    digest = lambda value: hashlib.sha256(value.encode('utf-8')).hexdigest()
    return {'study_config': digest(snapshot['study_yaml']), 'model_config': digest(snapshot['models_yaml']),
            'templates': {name: digest(value) for name, value in snapshot['templates'].items()},
            'response_schemas': content_hash(snapshot['schemas'])}


def spec_from_row(row: dict[str, Any]) -> EpisodeSpec:
    """Decode one planned assignment without redrawing its scenario."""
    values = dict(row['spec'])
    values['scenario'] = Scenario(**values['scenario'])
    if values.get('custom_cards') is not None:
        values['custom_cards'] = tuple(values['custom_cards'])
    return EpisodeSpec(**values)


def initial_state(row: dict[str, Any], config: Study2Config) -> EpisodeState:
    """Restore a unit's initial state; only probes contain hand-written prior messages."""
    state = EpisodeState(spec_from_row(row).scenario, config.message_limit)
    for values in row['initial_turns']:
        state = apply_turn(state, TranscriptTurn(**values))
    return state


def build_manifest(
    config_path: str | Path, phase: str, *, scenario_seed: int | None = None,
    order_seed: int | None = None, swapped_seed: int | None = None, allow_main: bool = False,
) -> list[dict[str, Any]]:
    """Build a seeded plan; synthetic full designs require explicit non-main seeds.

    The actual main-seed plan is gated until the later lock phase. Smoke plans
    contain four natural episodes and sixteen individually marked schema probes.
    """
    config = load_config(config_path)
    if phase not in {'synthetic', 'smoke', 'pilot', 'main'}:
        raise ValueError('Unknown Study 2 phase.')
    seeds = config.study['seeds']
    if phase == 'main' and not allow_main:
        raise ValueError('Actual main-manifest generation requires the separately approved lock phase.')
    if phase == 'synthetic':
        supplied = (scenario_seed, order_seed, swapped_seed)
        if any(type(value) is not int for value in supplied) or set(supplied) & {seeds['main_scenarios'], seeds['main_order'], seeds['swapped_names']}:
            raise ValueError('Synthetic plans require three explicit seeds separate from the main design.')
    else:
        scenario_seed = seeds[f'{phase}_scenarios'] if scenario_seed is None else scenario_seed
        order_seed = seeds[f'{phase}_order'] if order_seed is None else order_seed
        swapped_seed = seeds['swapped_names'] if swapped_seed is None else swapped_seed
    snapshot = source_snapshot(config)
    hashes = snapshot_hashes(snapshot)
    rows = []
    def add(spec, prefix=(), probe_role=None, position=None):
        row = {'schema_version': 1, 'study': 'study2', 'phase': phase,
               'pair_id': spec.scenario.pair_id, 'spec': asdict(spec),
               'is_probe': probe_role is not None, 'probe_role': probe_role, 'probe_position': position,
               'initial_turns': [asdict(turn) for turn in prefix], 'snapshot': snapshot,
               'source_sha256': hashes, 'scenario_seed': scenario_seed, 'order_seed': order_seed,
               'swapped_seed': swapped_seed, 'mock_seed': seeds['mock']}
        # Freeze probe requests as well as the source/prefix that generated them.
        row['probe_request'] = asdict(build_turn_request(config, spec, initial_state(row, config))) if row['is_probe'] else None
        rows.append(row)
    for pair_index, (buyer, seller) in enumerate(ordered_pairs(config)):
        if phase == 'smoke' and buyer != seller:
            continue
        scenarios = draw_balanced_scenarios(config, buyer_model=buyer, seller_model=seller,
                                             seed=scenario_seed, batch_id=phase)
        names = swapped_self_names(config, buyer_model=buyer, count=len(scenarios), seed=swapped_seed) if buyer == seller else None
        if phase == 'pilot':
            scenarios = tuple(next(s for s in scenarios if s.item == item['name'] and
                                  s.opener == ('buyer' if (pair_index + index) % 2 == 0 else 'seller'))
                              for index, item in enumerate(config.study['items']))
        elif phase == 'smoke':
            scenarios = scenarios[:1]
        for index, scenario in enumerate(scenarios):
            conditions = config.study['conditions'] if phase in {'synthetic', 'main'} else (
                [config.study['conditions'][(pair_index + index) % 3]] if phase == 'pilot' else ['not_disclosed'])
            for condition in conditions:
                alternative = names[index] if names and condition == 'swapped' else None
                spec = EpisodeSpec(f'{scenario.scenario_id}:{condition}', buyer, seller, condition, scenario, alternative, phase)
                add(spec)
        if phase == 'smoke':
            fixed = load_fixed_positions(config)
            for role in config.study['smoke']['probes']['roles']:
                for position in config.study['smoke']['probes']['positions']:
                    scenario, prefix = fixed.position(config, buyer_model=buyer, seller_model=seller,
                                                       role=role, message_number=position)
                    spec = EpisodeSpec(f'study2:smoke:probe:{buyer}:{role}:k{position}', buyer, seller,
                                       'not_disclosed', scenario, phase='smoke')
                    add(spec, prefix, role, position)
    random.Random(order_seed).shuffle(rows)
    for index, row in enumerate(rows, 1):
        row['execution_position'] = index
        row['episode_sha256'] = content_hash(row)
    validate_manifest(rows)
    return rows


def validate_manifest(rows: list[dict[str, Any]]) -> None:
    """Check identities, frozen sources, probe positions, and shared plan bindings."""
    if not rows:
        raise ValueError('A Study 2 manifest cannot be empty.')
    seen = set()
    first = rows[0]
    config = config_from_snapshot(first['snapshot'])
    if config.schemas != {str(k): response_schema(k, config.message_limit) for k in range(1, config.message_limit + 1)}:
        raise ValueError('Frozen schemas differ from this implementation; explicit review is required.')
    for index, row in enumerate(rows, 1):
        unsigned = {key: value for key, value in row.items() if key != 'episode_sha256'}
        if row['schema_version'] != 1 or row['study'] != 'study2' or row['execution_position'] != index or row['episode_sha256'] != content_hash(unsigned):
            raise ValueError('Invalid Study 2 manifest row hash or position.')
        if row['snapshot'] != first['snapshot'] or row['phase'] != first['phase'] or row['source_sha256'] != snapshot_hashes(row['snapshot']):
            raise ValueError('Manifest rows must share their exact frozen source snapshot.')
        if any(row[key] != first[key] for key in ('scenario_seed', 'order_seed', 'swapped_seed', 'mock_seed')):
            raise ValueError('Manifest rows must share their design/order seed metadata.')
        spec = spec_from_row(row)
        if spec.custom_cards is not None:
            raise ValueError('Study 2 manifests require the configured buyer-only disclosure, not custom cards.')
        if spec.episode_id in seen or spec.phase != row['phase'] or spec.scenario.pair_id != row['pair_id']:
            raise ValueError('Duplicate or inconsistent episode identity.')
        seen.add(spec.episode_id)
        seller_disclosure(config, buyer_model=spec.buyer_model, seller_model=spec.seller_model,
                          condition=spec.condition, swapped_model=spec.swapped_model)
        state = initial_state(row, config)
        request = build_turn_request(config, spec, state)
        if row['is_probe']:
            if row['phase'] != 'smoke' or row['probe_position'] not in (config.message_limit - 1, config.message_limit) or row['probe_role'] != request.context['role']:
                raise ValueError('Invalid forced-position probe identity.')
            if len(state.turns) + 1 != row['probe_position'] or content_hash(row['probe_request']) != content_hash(asdict(request)):
                raise ValueError('Probe request differs from its frozen transcript position.')
        elif row['initial_turns'] or row['probe_request'] is not None:
            raise ValueError('Natural episodes cannot contain a probe prefix/request.')
    _check_balance(rows, config)


def _check_balance(rows: list[dict[str, Any]], config: Study2Config) -> None:
    phase = rows[0]['phase']
    natural = [row for row in rows if not row['is_probe']]
    probes = [row for row in rows if row['is_probe']]
    pairs = ordered_pairs(config)
    groups = defaultdict(list)
    for row in natural:
        spec = spec_from_row(row)
        groups[(spec.buyer_model, spec.seller_model)].append(spec)
        item = next((item for item in config.study['items'] if item['name'] == spec.scenario.item), None)
        if item is None or item['reference_price'] != spec.scenario.reference_price:
            raise ValueError('Scenario item/reference price differs from the design.')
        step = config.study['limits']['rounding_increment']
        for field, bounds in [('seller_min', 'seller_multiplier'), ('buyer_max', 'buyer_multiplier')]:
            value, reference = getattr(spec.scenario, field), spec.scenario.reference_price
            low, high = config.study['limits'][bounds]
            if value % step or not low * reference - step / 2 <= value <= high * reference + step / 2:
                raise ValueError('Scenario private limit is outside its configured rounded range.')
    if phase in {'synthetic', 'main'}:
        if probes or len(natural) != config.study['main']['expected_episodes'] or set(groups) != set(pairs):
            raise ValueError('Full design lacks its exact pair/episode allocation.')
        for (buyer, seller), specs in groups.items():
            scenarios = defaultdict(list)
            for spec in specs:
                scenarios[spec.scenario.scenario_id].append(spec)
            if len(scenarios) != config.study['main']['scenarios_per_pair']:
                raise ValueError('Incorrect number of scenarios within a pair.')
            unique = []
            for cells in scenarios.values():
                if Counter(spec.condition for spec in cells) != Counter(config.study['conditions']) or len({content_hash(asdict(spec.scenario)) for spec in cells}) != 1:
                    raise ValueError('Scenario facts/conditions are not matched across cards.')
                unique.append(cells[0].scenario)
            expected = {(item['name'], opener): count for item in config.study['items']
                        for opener, count in config.study['scenario_design']['replicates_per_item_opener'].items()}
            if Counter((scenario.item, scenario.opener) for scenario in unique) != Counter(expected):
                raise ValueError('Item/opener balance is incorrect.')
            if buyer == seller:
                names = Counter(spec.swapped_model for spec in specs if spec.condition == 'swapped')
                expected_names = Counter(swapped_self_names(config, buyer_model=buyer, count=len(unique), seed=rows[0]['swapped_seed']))
                if names != expected_names:
                    raise ValueError('Swapped self-pair name allocation is incorrect.')
    elif phase == 'pilot':
        if probes or len(natural) != config.study['pilot']['expected_episodes'] or set(groups) != set(pairs):
            raise ValueError('Pilot pair/episode allocation is incorrect.')
        for pair_index, pair in enumerate(pairs):
            specs = groups[pair]
            if len(specs) != config.study['pilot']['episodes_per_pair'] or len({s.scenario.scenario_id for s in specs}) != len(specs):
                raise ValueError('Pilot scenarios must be distinct within each pair.')
            for index, item in enumerate(config.study['items']):
                cells = [s for s in specs if s.scenario.item == item['name']]
                if len(cells) != 1 or cells[0].condition != config.study['conditions'][(pair_index + index) % 3]:
                    raise ValueError('Pilot condition rotation/item allocation is incorrect.')
    elif phase == 'smoke':
        expected_pairs = {(model, model) for model in config.model_order}
        if set(groups) != expected_pairs or any(len(cells) != 1 or cells[0].condition != 'not_disclosed' for cells in groups.values()):
            raise ValueError('Smoke requires one not-disclosed self-pair episode per model.')
        expected = {(model, role, k) for model in config.model_order for role in ('buyer', 'seller')
                    for k in (config.message_limit - 1, config.message_limit)}
        actual = [(spec_from_row(row).buyer_model, row['probe_role'], row['probe_position']) for row in probes]
        if len(actual) != len(expected) or set(actual) != expected:
            raise ValueError('Smoke probes require every model/role/position exactly once.')
        fixed = load_fixed_positions(config)
        for row in probes:
            spec = spec_from_row(row)
            scenario, prefix = fixed.position(config, buyer_model=spec.buyer_model, seller_model=spec.buyer_model,
                                               role=row['probe_role'], message_number=row['probe_position'])
            if spec.buyer_model != spec.seller_model or spec.condition != 'not_disclosed' or spec.scenario != scenario or content_hash(row['initial_turns']) != content_hash([asdict(turn) for turn in prefix]):
                raise ValueError('Probe differs from the fixed hand-written position.')
    else:
        raise ValueError('Unknown manifest phase.')


def write_manifest(rows: list[dict[str, Any]], path: str | Path) -> None:
    """Write a new self-contained plan without replacing any existing artifact."""
    validate_manifest(rows)
    assert_no_credentials(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(''.join(map(json_line, rows)))
        stream.flush()
        os.fsync(stream.fileno())


def read_manifest(path: str | Path) -> list[dict[str, Any]]:
    """Read and validate a saved manifest without consulting current source files."""
    rows = read_jsonl(path)
    validate_manifest(rows)
    return rows

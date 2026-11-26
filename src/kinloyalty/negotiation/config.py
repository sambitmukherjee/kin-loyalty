"""Load Study 2 design data without changing the shared model configuration."""

from dataclasses import dataclass
from copy import deepcopy
from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Study2Config:
    """Keep study data, the unchanged model roster, and resolved source paths."""

    path: Path
    study: dict[str, Any]
    roster: dict[str, Any]
    model_path: Path
    template_directory: Path
    templates: dict[str, str] | None = None
    schemas: dict[str, dict[str, Any]] | None = None

    @property
    def model_order(self) -> tuple[str, ...]:
        """Return the explicit roster order used for pairing and name rotation."""
        return tuple(self.study["model_order"])

    @property
    def models(self) -> dict[str, dict[str, Any]]:
        """Expose the existing model identities and API settings read-only by convention."""
        return self.roster["models"]

    @property
    def message_limit(self) -> int:
        """Return the configured total message limit for both participants."""
        return self.study["protocol"]["message_limit"]


def load_config(path: str | Path = "configs/study2.yaml") -> Study2Config:
    """Read relative paths and reject inconsistent design counts before rendering."""
    path = Path(path).resolve()
    study = yaml.safe_load(path.read_text(encoding="utf-8"))
    model_path = (path.parent / study["models_file"]).resolve()
    roster = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    config = Study2Config(
        path, study, roster, model_path,
        (path.parent / study["prompt_directory"]).resolve(),
    )
    _validate(config)
    return config


def template_text(config: Study2Config, filename: str) -> str:
    """Read exact template bytes from a frozen snapshot when one is available."""
    if config.templates is not None:
        return config.templates[filename]
    return (config.template_directory / filename).read_text(encoding="utf-8")


def config_from_snapshot(snapshot: dict[str, Any]) -> Study2Config:
    """Load a self-contained frozen configuration without consulting current files."""
    return deepcopy(_parse_snapshot(snapshot['study_yaml'], snapshot['models_yaml'],
                                    tuple(sorted(snapshot['templates'].items())),
                                    json.dumps(snapshot['schemas'], separators=(',', ':'))))


@lru_cache(maxsize=8)
def _parse_snapshot(study_yaml: str, models_yaml: str, templates: tuple[tuple[str, str], ...], schemas: str) -> Study2Config:
    config = Study2Config(
        Path('/frozen/configs/study2.yaml'), yaml.safe_load(study_yaml),
        yaml.safe_load(models_yaml), Path('/frozen/configs/models.yaml'),
        Path('/frozen/prompts/study2'), dict(templates), json.loads(schemas),
    )
    _validate(config)
    return config


def _validate(config: Study2Config) -> None:
    study = config.study
    order = config.model_order
    if study["study"] != "study2" or study["schema_version"] != 1:
        raise ValueError("Expected Study 2 configuration schema version 1.")
    if len(order) < 2 or len(set(order)) != len(order) or set(order) != set(config.models):
        raise ValueError("model_order must contain every roster model exactly once.")
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', key) for key in order):
        raise ValueError('Model keys must be safe filename components.')
    if study["pairs"] != "all_ordered_including_self":
        raise ValueError("Unsupported ordered-pair allocation.")
    if study["conditions"] != ["not_disclosed", "true", "swapped"]:
        raise ValueError("Study 2 requires the three specified disclosure conditions.")
    if study["names"] != {"buyer": "Alex", "seller": "Jordan"}:
        raise ValueError("Study 2 uses only the Alex/Jordan name pair.")
    if type(config.message_limit) is not int or config.message_limit < 2:
        raise ValueError("message_limit must be an integer of at least two.")
    items = study["items"]
    if not items or len({item["name"] for item in items}) != len(items):
        raise ValueError("Item names must be nonempty and distinct.")
    if any(not isinstance(item["name"], str) or not item["name"].strip()
           or type(item["reference_price"]) is not int or item["reference_price"] <= 0
           for item in items):
        raise ValueError("Each item needs a name and positive whole-dollar reference price.")
    limits = study["limits"]
    if type(limits["rounding_increment"]) is not int or limits["rounding_increment"] <= 0:
        raise ValueError("Price rounding requires a positive whole-dollar increment.")
    if limits["rounding"] != "half_up":
        raise ValueError("Only the documented nearest-multiple half-up rule is supported.")
    for name in ("seller_multiplier", "buyer_multiplier"):
        bounds = limits[name]
        if len(bounds) != 2 or not 0 < bounds[0] < bounds[1]:
            raise ValueError("Limit multipliers must be positive increasing intervals.")
    design = study["scenario_design"]
    if design["openers"] != ["buyer", "seller"]:
        raise ValueError("Balanced scenarios require both openers.")
    replicates = design["replicates_per_item_opener"]
    if (not isinstance(replicates, dict) or set(replicates) != set(design["openers"])
            or any(type(count) is not int or count < 0 for count in replicates.values())
            or not sum(replicates.values()) or not design["shared_across_conditions"]):
        raise ValueError("Scenarios require opener replication counts and shared condition facts.")
    if design["random_stream"] != "sha256_seed_pair_purpose_python_random":
        raise ValueError("Unsupported scenario random-stream convention.")
    rotation = design["self_pair_swapped_names"]
    if rotation != {"allocation": "as_evenly_as_possible",
                    "shortfall": "next_model_in_cyclic_roster", "assignment": "seeded_shuffle"}:
        raise ValueError("Unsupported self-pair name rotation.")
    scenarios = len(items) * sum(replicates.values())
    main = study["main"]
    if (main["scenarios_per_pair"] != scenarios
            or main["episodes_per_pair_condition"] != scenarios
            or main["expected_pairs"] != len(order) ** 2
            or main["expected_episodes"] != len(order) ** 2 * scenarios * len(study["conditions"])):
        raise ValueError("Main counts disagree with the configured balance.")
    seeds = list(study["seeds"].values())
    if any(type(seed) is not int for seed in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("Design, order, and analysis seeds must be distinct integers.")

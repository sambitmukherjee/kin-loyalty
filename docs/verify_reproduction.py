"""Compare reproduced paper artifacts with the committed reference outputs.

This command reads existing files. It does not run an analysis, change a result,
or make a model call. NumPy is supplied by either frozen study environment.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = {
    "study1": ROOT / "results/study1/generated",
    "study2": ROOT / "results/study2/main",
}
METADATA = {"study1": "provenance.json", "study2": "metadata.json"}


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory_errors(directory):
    """Check every inventory entry and require it to cover all output files."""
    inventory = json.loads((directory / "artifacts.sha256.json").read_text())
    files = {
        str(path.relative_to(directory))
        for path in directory.rglob("*")
        if path.is_file() and path.name != "artifacts.sha256.json"
    }
    errors = []
    if set(inventory) != files:
        errors.append("The checksum inventory does not cover exactly the output files.")
    for name, expected in inventory.items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()):
            errors.append(f"The inventory contains an external path: {name}.")
        elif not path.is_file() or file_hash(path) != expected:
            errors.append(f"The recorded checksum does not match: {name}.")
    return errors


def array_comparison(reference, actual):
    """Compare every array, including its name, shape, type and missing values."""
    differences = []
    with np.load(reference, allow_pickle=False) as left:
        with np.load(actual, allow_pickle=False) as right:
            names = sorted(set(left.files) | set(right.files))
            for name in names:
                if name not in left or name not in right:
                    differences.append(name)
                    continue
                a, b = left[name], right[name]
                if a.shape != b.shape or a.dtype != b.dtype:
                    differences.append(name)
                    continue
                equal_nan = np.issubdtype(a.dtype, np.inexact)
                if not np.array_equal(a, b, equal_nan=equal_nan):
                    differences.append(name)
    return {
        "count": len(names),
        "all_exactly_equal_including_nan": not differences,
        "different_arrays": differences,
        "archive_byte_identical": reference.read_bytes() == actual.read_bytes(),
    }


def metadata_comparison(study, reference, actual):
    """Explain checkout-specific differences without ignoring scientific settings."""
    before = json.loads(reference.read_text())
    after = json.loads(actual.read_text())
    informational = []
    unexpected = []

    def walk(a, b, prefix=()):
        if a == b:
            return
        field = ".".join(prefix)
        if study == "study1" and prefix == ("inputs_sha256",):
            if sorted(a.values()) == sorted(b.values()):
                informational.append({"field": field, "reason": "Input paths changed; file digests match."})
            else:
                unexpected.append(field)
            return
        if study == "study1" and prefix == ("package_source_sha256",):
            # Current main also contains Study 2. Existing Study 1 analysis files
            # must still match, even when additional modules are present.
            analysis_files = {name for name in a if name.startswith("analysis/")}
            if all(name in b and a[name] == b[name] for name in analysis_files):
                informational.append({"field": field, "reason": "Source inventory changed; existing Study 1 analysis digests match."})
            else:
                unexpected.append(field)
            return
        provenance_fields = {("git_commit",), ("code_dirty",)} if study == "study1" else {
            ("provenance", "git_commit"), ("provenance", "code_dirty")
        }
        if prefix in provenance_fields:
            informational.append({"field": field, "reference": a, "reproduced": b})
            return
        if isinstance(a, dict) and isinstance(b, dict):
            for key in sorted(set(a) | set(b)):
                if key not in a or key not in b:
                    unexpected.append(".".join((*prefix, key)))
                else:
                    walk(a[key], b[key], (*prefix, key))
        else:
            unexpected.append(field)

    walk(before, after)
    return {"informational_differences": informational, "unexpected_fields": unexpected}


def compare_study(study, actual):
    reference = REFERENCES[study]
    actual = actual.resolve()
    reference_files = {str(p.relative_to(reference)) for p in reference.rglob("*") if p.is_file()}
    actual_files = {str(p.relative_to(actual)) for p in actual.rglob("*") if p.is_file()}
    unexpected = []
    if reference_files != actual_files:
        return {
            "matched": False,
            "missing_files": sorted(reference_files - actual_files),
            "extra_files": sorted(actual_files - reference_files),
        }

    inventory = {
        "reference": inventory_errors(reference),
        "reproduced": inventory_errors(actual),
    }
    if any(inventory.values()):
        unexpected.append("Invalid checksum inventory.")
    tables = sorted(name for name in reference_files if name.endswith(".csv"))
    figures = sorted(name for name in reference_files if name.endswith((".pdf", ".png")))
    different_tables = [name for name in tables if (reference / name).read_bytes() != (actual / name).read_bytes()]
    different_figures = [name for name in figures if (reference / name).read_bytes() != (actual / name).read_bytes()]
    unexpected.extend(different_tables + different_figures)
    archive = "resampling_distributions.npz" if study == "study1" else "resamples.npz"
    arrays = array_comparison(reference / archive, actual / archive)
    if not arrays["all_exactly_equal_including_nan"]:
        unexpected.append("Resampling arrays differ.")
    metadata = metadata_comparison(study, reference / METADATA[study], actual / METADATA[study])
    unexpected.extend("Metadata: " + field for field in metadata["unexpected_fields"])
    other = reference_files - set(tables) - set(figures) - {archive, METADATA[study], "artifacts.sha256.json"}
    different_other = [name for name in sorted(other) if (reference / name).read_bytes() != (actual / name).read_bytes()]
    unexpected.extend(different_other)
    return {
        "matched": not unexpected,
        "csv_tables": {"count": len(tables), "all_byte_identical": not different_tables},
        "figures": {"count": len(figures), "all_byte_identical": not different_figures},
        "resampling_arrays": arrays,
        "metadata": metadata,
        "checksum_inventory_errors": inventory,
        "unexpected_differences": unexpected,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study1", type=Path, required=True, help="Reproduced Study 1 output directory.")
    parser.add_argument("--study2", type=Path, required=True, help="Reproduced Study 2 output directory.")
    parser.add_argument("--report", type=Path, help="Write a new JSON report outside all compared output directories.")
    args = parser.parse_args()
    if args.report:
        protected = [*REFERENCES.values(), args.study1, args.study2]
        if any(args.report.resolve().is_relative_to(path.resolve()) for path in protected):
            parser.error("The report must be outside the reference and reproduced output directories.")
        if args.report.exists():
            parser.error("The report path already exists; choose a new file.")
    try:
        studies = {name: compare_study(name, getattr(args, name)) for name in REFERENCES}
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Comparison failed: {error}\n")
    result = {"matched": all(study["matched"] for study in studies.values()), "studies": studies}
    text = json.dumps(result, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x") as stream:
            stream.write(text)
    print(text, end="")
    raise SystemExit(0 if result["matched"] else 1)


if __name__ == "__main__":
    main()

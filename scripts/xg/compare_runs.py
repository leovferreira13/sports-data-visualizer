#!/usr/bin/env python3
"""Verify two complete local audit/feature runs and compare every output byte."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from ingest_statsbomb import AuditError, canonical, sha256, unique_keys

CHUNK_SIZE = 1024 * 1024


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verified_run(directory):
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise AuditError("Run directory is missing or not a directory")
    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise AuditError("Run must contain a regular manifest.json")
    try:
        manifest = json.loads(manifest_path.read_bytes(), object_pairs_hook=unique_keys,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))
    except (ValueError, UnicodeError) as exc:
        raise AuditError("Invalid manifest JSON") from exc
    if (not isinstance(manifest, dict) or manifest.get("complete") is not True
            or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1
            or not isinstance(manifest.get("outputs"), dict) or not manifest["outputs"]):
        raise AuditError("Incomplete or incompatible run manifest")
    identity = {k: v for k, v in manifest.items() if k != "run_id"}
    if manifest.get("run_id") != sha256(canonical(identity).encode()):
        raise AuditError("Manifest run identity does not match its contents")
    for name, digest in manifest["outputs"].items():
        if (not isinstance(name, str) or name in ("", ".", "..", "manifest.json")
                or "/" in name or "\\" in name
                or not isinstance(digest, str) or not re.fullmatch("[a-f0-9]{64}", digest)):
            raise AuditError("Invalid output filename or hash in manifest")
    expected = {"manifest.json", *manifest["outputs"]}
    if {p.name for p in directory.iterdir()} != expected:
        raise AuditError("Run file inventory differs from manifest (missing or extra files)")
    for name in sorted(expected):
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise AuditError("Run outputs must be regular files, not links or directories")
        if name != "manifest.json" and file_hash(path) != manifest["outputs"][name]:
            raise AuditError(f"Output hash mismatch: {name}")
    return directory, manifest, expected


def same_bytes(left, right):
    with left.open("rb") as a, right.open("rb") as b:
        while True:
            ac, bc = a.read(CHUNK_SIZE), b.read(CHUNK_SIZE)
            if ac != bc:
                return False
            if not ac:
                return True


def compare_runs(left_dir, right_dir):
    if Path(left_dir).resolve() == Path(right_dir).resolve():
        raise AuditError("Comparison requires two distinct run directories")
    left, left_manifest, left_files = verified_run(left_dir)
    right, right_manifest, right_files = verified_run(right_dir)
    if left_files != right_files:
        raise AuditError("The two runs have different output inventories")
    for name in sorted(left_files):
        if not same_bytes(left / name, right / name):
            raise AuditError(f"Runs differ byte for byte: {name}")
    # Recheck identity/integrity after comparison to detect concurrent modifications.
    if verified_run(left)[1] != left_manifest or verified_run(right)[1] != right_manifest:
        raise AuditError("Run changed during comparison")
    return {"run_id": left_manifest["run_id"], "files": sorted(left_files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-dir", type=Path, required=True, help="First completed immutable run directory")
    parser.add_argument("--right-dir", type=Path, required=True, help="Second completed immutable run directory")
    args = parser.parse_args()
    try:
        result = compare_runs(args.left_dir, args.right_dir)
    except (AuditError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for name in result["files"]:
        print(f"PASS: {name} verified and byte-identical")
    print(f"PASS: complete comparison; run_id={result['run_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Strict JSON and immutable, private scientific run publication (stdlib only)."""

import json
import os
from pathlib import Path
import platform
import shutil
import tempfile

from compare_runs import verified_run
from features import CONTRACT_PATH
from ingest_statsbomb import AuditError, canonical, sha256, unique_keys

PROJECT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = PROJECT / "model/training-protocol.json"


def load_json(data):
    try:
        return json.loads(data, object_pairs_hook=unique_keys,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError) as exc:
        raise AuditError("Invalid scientific JSON") from exc


def read_json(path):
    return load_json(Path(path).read_bytes())


def protocol():
    return read_json(PROTOCOL_PATH)


def code_identity():
    paths = sorted((PROJECT / "scripts/xg").glob("*.py"))
    paths += sorted((PROJECT / "model").glob("*.json"))
    paths += [PROJECT / "scripts/xg/requirements.lock", PROJECT / "lib/presets.ts",
              PROJECT / "tests/fixtures/training-presets.json"]
    return {p.relative_to(PROJECT).as_posix(): sha256(p.read_bytes()) for p in paths}


def output_root(output, source):
    raw = Path(output).absolute()
    if any(p.is_symlink() for p in [raw, *raw.parents]):
        raise AuditError("Output roots cannot contain links")
    root, source = raw.resolve(), Path(source).resolve()
    derived = PROJECT / "data/derived"
    if (root == PROJECT or PROJECT in root.parents) and derived not in [root, *root.parents]:
        raise AuditError("Project outputs must stay under ignored data/derived")
    if root == source or source in root.parents:
        raise AuditError("Output root must be outside the source run")
    return root


def publish(output, source, phase, files, provenance, guard):
    root = output_root(output, source)
    root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".staging-", dir=root))
    try:
        for name, contents in files.items():
            if Path(name).name != name or name == "manifest.json":
                raise AuditError("Invalid scientific output name")
            (stage / name).write_bytes(contents if isinstance(contents, bytes)
                                      else canonical(contents).encode())
        manifest = {"schema_version": 1, "complete": True, "phase": phase,
                    "python_version": platform.python_version(), **provenance,
                    "outputs": {p.name: sha256(p.read_bytes()) for p in stage.iterdir()}}
        manifest["run_id"] = sha256(canonical(manifest).encode())
        (stage / "manifest.json").write_text(canonical(manifest), encoding="utf-8")
        guard()
        destination = root / manifest["run_id"]
        if destination.exists() or destination.is_symlink():
            _, existing, names = verified_run(destination)
            if existing != manifest or any((destination / n).read_bytes() != (stage / n).read_bytes() for n in names):
                raise AuditError("Immutable scientific run conflict")
        else:
            os.rename(stage, destination)
        return destination
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def recheck(directory, manifest, codes):
    if verified_run(directory)[1] != manifest or code_identity() != codes:
        raise AuditError("Input, configuration or code changed during the run")

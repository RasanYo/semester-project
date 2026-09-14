"""Download-with-provenance.

The corpus and every raw file are a cache; the manifest is the fact. Anything
this module fetches is recorded with its URL, the date it was fetched, its
sha256 and its size, so a reader can tell whether the file they hold is the one
a number was computed from.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from .config import DATA_RAW, MANIFEST_PATH, REPO_ROOT

USER_AGENT = "mediapos/0.1 (ETHZ semester project; rasanhy@gmail.com)"
_TIMEOUT = 120


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Manifest:
    """Accumulates one entry per downloaded artefact, then writes itself out."""

    def __init__(self, path: Path = MANIFEST_PATH) -> None:
        self.path = path
        self.entries: list[dict[str, Any]] = []
        self.notes: dict[str, Any] = {}

    def record(self, *, name: str, url: str, path: Path, **extra: Any) -> None:
        self.entries.append(
            {
                "name": name,
                "url": url,
                "local_path": _repo_relative(path),
                "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                **extra,
            }
        )

    def note(self, key: str, value: Any) -> None:
        """Record a fact about the run that is not a file -- counts, the rule."""
        self.notes[key] = value

    def write(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "notes": self.notes,
            "sources": self.entries,
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return self.path


def fetch(
    url: str,
    dest: Path | str,
    *,
    manifest: Manifest | None = None,
    name: str | None = None,
    force: bool = False,
    headers: dict[str, str] | None = None,
    allow_missing: bool = False,
    **record_extra: Any,
) -> Path | None:
    """GET `url` into `dest`, recording provenance.

    A cached file is reused unless `force`. With `allow_missing`, a 404 returns
    None instead of raising -- some per-object Swissvotes workbooks simply do
    not exist, and that is data, not a failure.
    """
    dest = DATA_RAW / dest if not Path(dest).is_absolute() else Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if force or not dest.exists():
        hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
        resp = requests.get(url, headers=hdrs, timeout=_TIMEOUT)
        if allow_missing and resp.status_code == 404:
            return None
        resp.raise_for_status()
        dest.write_bytes(resp.content)

    if manifest is not None:
        manifest.record(name=name or dest.name, url=url, path=dest, **record_extra)
    return dest

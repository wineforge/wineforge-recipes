#!/usr/bin/env python3
"""Download remote recipe inputs and verify their pinned SHA-256 digests."""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

from validate import load_document

MAX_SOURCE_BYTES = 256 * 1024 * 1024


def verify_source(url: str, expected: str) -> tuple[str, int]:
    request = urllib.request.Request(url, headers={"User-Agent": "wineforge-recipes/1"})
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - HTTPS checked below
        final_url = response.geturl()
        if not final_url.startswith("https://"):
            raise ValueError(f"redirect downgraded HTTPS: {final_url}")
        with tempfile.TemporaryFile() as sink:
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_SOURCE_BYTES:
                    raise ValueError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
                digest.update(chunk)
                sink.write(chunk)
    actual = digest.hexdigest()
    if actual != expected:
        raise ValueError(f"digest mismatch: expected {expected}, got {actual}")
    return actual, size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        recipe = load_document(path)
        for source in recipe.get("sources", []):
            if source.get("kind") != "remote":
                continue
            try:
                digest, size = verify_source(source["url"], source["sha256"])
                print(f"OK   {path.name}:{source['id']} {size} bytes sha256:{digest}")
            except (OSError, ValueError) as error:
                failed = True
                print(f"FAIL {path.name}:{source['id']} {error}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

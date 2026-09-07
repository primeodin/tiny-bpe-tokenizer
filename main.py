"""Thin wrapper so `python3 main.py train ...` works without installing."""

from __future__ import annotations

from tiny_bpe.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

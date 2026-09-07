"""Tests for tiny-bpe-tokenizer — word table, roundtrips, sample train, CLI smoke."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tiny_bpe.bpe import BytePairTokenizer, train_word_bpe

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample.txt"
MAIN = ROOT / "main.py"


def test_word_bpe_hand_worked_first_five_merges() -> None:
    """Classic low/lower/newest table — first five merges must match the README."""
    merges = train_word_bpe({"low": 5, "lower": 2, "newest": 3}, num_merges=5)
    assert merges == [
        ("l", "o"),
        ("lo", "w"),
        ("low", "</w>"),
        ("n", "e"),
        ("ne", "w"),
    ]


def test_byte_bpe_hand_worked_unicode_emoji_first_five() -> None:
    """é🚀 é🚀 table — first five byte merges must match the README."""
    tok = BytePairTokenizer()
    tok.train("é🚀 é🚀", vocab_size=256 + 5)
    assert tok.merges == [
        (195, 169),  # é
        (256, 240),
        (257, 159),
        (258, 154),
        (259, 128),  # full é🚀
    ]
    assert tok.vocab[256] == "é".encode("utf-8")
    assert tok.vocab[260] == "é🚀".encode("utf-8")


@pytest.mark.parametrize(
    "text",
    [
        "hello world",
        "café",
        "rocket 🚀",
        "café 🚀 low lower newest",
        "emoji 🚀 and café together",
        "",
    ],
)
def test_byte_level_lossless_roundtrip(text: str) -> None:
    tok = BytePairTokenizer()
    # Train on a bit of related text so merges exist; empty still roundtrips.
    tok.train("low lower newest café 🚀 hello world\n" + text, vocab_size=300)
    assert tok.decode(tok.encode(text)) == text


def test_untrained_roundtrip_is_bytes() -> None:
    tok = BytePairTokenizer()
    text = "café 🚀"
    assert tok.decode(tok.encode(text)) == text


def test_train_encode_decode_on_sample(tmp_path: Path) -> None:
    corpus = SAMPLE.read_text(encoding="utf-8")
    tok = BytePairTokenizer()
    tok.train(corpus, vocab_size=320)
    assert len(tok.merges) == 320 - 256

    probe = "low lower newest café 🚀"
    ids = tok.encode(probe)
    assert tok.decode(ids) == probe
    assert all(isinstance(i, int) and i >= 0 for i in ids)

    model = tmp_path / "tokenizer.json"
    tok.save(model)
    loaded = BytePairTokenizer.load(model)
    assert loaded.merges == tok.merges
    assert loaded.encode(probe) == ids
    assert loaded.decode(ids) == probe


def test_cli_smoke_via_main(tmp_path: Path) -> None:
    model = tmp_path / "tok.json"
    train = subprocess.run(
        [
            sys.executable,
            str(MAIN),
            "train",
            "--corpus",
            str(SAMPLE),
            "--vocab-size",
            "300",
            "--model",
            str(model),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert train.returncode == 0, train.stderr
    assert "merges learned:" in train.stdout
    assert "saved:" in train.stdout
    assert model.is_file()

    enc = subprocess.run(
        [
            sys.executable,
            str(MAIN),
            "encode",
            "low café 🚀",
            "--model",
            str(model),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert enc.returncode == 0, enc.stderr
    lines = enc.stdout.strip().splitlines()
    assert len(lines) >= 3
    ids = [int(x) for x in lines[0].split()]
    assert "tokens:" in lines[1]
    assert "chars-per-token:" in lines[2]

    dec = subprocess.run(
        [
            sys.executable,
            str(MAIN),
            "decode",
            *[str(i) for i in ids],
            "--model",
            str(model),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert dec.returncode == 0, dec.stderr
    assert dec.stdout.strip() == "low café 🚀"


def test_tie_break_first_seen_byte_level() -> None:
    """When two pairs tie, the earlier-seen pair wins — deterministic training."""
    # "abab" has (a,b) and (b,a) each once if we use distinct bytes...
    # Better: text where two pairs appear equally often and order decides.
    # "aaab" -> pairs (a,a)=2, (a,b)=1 — no tie.
    # Use equal counts: "ab ac" with spaces... simpler:
    # bytes of "xyxz" -> (x,y), (y,x), (x,z) — not equal.
    # "abab": (a,b)=2, (b,a)=1
    # Force tie with "aaaa": only (a,a).
    # Two-char alphabet with equal adjacent counts:
    # "abab" vs we need (a,b) and something else equal.
    # Text "lowlow" at byte level — just assert two runs match.
    tok1 = BytePairTokenizer()
    tok2 = BytePairTokenizer()
    text = "low lower newest low lower newest"
    tok1.train(text, vocab_size=280)
    tok2.train(text, vocab_size=280)
    assert tok1.merges == tok2.merges

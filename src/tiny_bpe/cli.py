"""Command-line entry for tiny-bpe-tokenizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tiny_bpe.bpe import BytePairTokenizer


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tiny-bpe",
        description="Train / encode / decode with a from-scratch byte-pair tokenizer.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    train_p = sub.add_parser("train", help="Learn merges from a corpus file")
    train_p.add_argument("--corpus", required=True, type=Path, help="Path to training text")
    train_p.add_argument("--vocab-size", required=True, type=int, help="Total vocab size (incl. 256 bytes)")
    train_p.add_argument(
        "--model",
        type=Path,
        default=Path("tokenizer.json"),
        help="Where to save the model (default: tokenizer.json)",
    )

    enc_p = sub.add_parser("encode", help="Encode text to token ids")
    enc_p.add_argument("text", help="Text to encode")
    enc_p.add_argument(
        "--model",
        type=Path,
        default=Path("tokenizer.json"),
        help="Tokenizer JSON path (default: tokenizer.json)",
    )

    dec_p = sub.add_parser("decode", help="Decode token ids back to text")
    dec_p.add_argument("ids", nargs="+", type=int, help="Token ids")
    dec_p.add_argument(
        "--model",
        type=Path,
        default=Path("tokenizer.json"),
        help="Tokenizer JSON path (default: tokenizer.json)",
    )

    return p


def cmd_train(args: argparse.Namespace) -> int:
    text = args.corpus.read_text(encoding="utf-8")
    tok = BytePairTokenizer()
    tok.train(text, args.vocab_size)
    tok.save(args.model)

    n = len(tok.merges)
    print(f"merges learned: {n}")
    preview = tok.merges[:8]
    if preview:
        pretty = ", ".join(f"({a},{b})" for a, b in preview)
        more = " ..." if n > len(preview) else ""
        print(f"first merges: {pretty}{more}")
    print(f"saved: {args.model}")
    return 0


def cmd_encode(args: argparse.Namespace) -> int:
    tok = BytePairTokenizer.load(args.model)
    ids = tok.encode(args.text)
    print(" ".join(str(i) for i in ids))
    print(f"tokens: {len(ids)}")
    chars = len(args.text)
    ratio = chars / len(ids) if ids else 0.0
    print(f"chars-per-token: {ratio:.3f}")
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    tok = BytePairTokenizer.load(args.model)
    print(tok.decode(args.ids))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "train":
            return cmd_train(args)
        if args.command == "encode":
            return cmd_encode(args)
        if args.command == "decode":
            return cmd_decode(args)
    except Exception as exc:  # noqa: BLE001 — teach failures clearly
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

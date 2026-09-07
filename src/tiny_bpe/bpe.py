"""Byte-pair encoding from scratch — byte-level train / encode / decode + word-BPE teaching helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def _best_pair(
    counts: dict[tuple, int], order: dict[tuple, int]
) -> tuple:
    """Pick the highest-count pair; ties go to the pair seen first (lowest order index)."""
    return max(counts.keys(), key=lambda p: (counts[p], -order[p]))


def _merge_sequence(ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    """Replace every non-overlapping occurrence of ``pair`` with ``new_id``."""
    a, b = pair
    out: list[int] = []
    i = 0
    n = len(ids)
    while i < n:
        if i < n - 1 and ids[i] == a and ids[i + 1] == b:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def _count_pairs(ids: list[int]) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    counts: dict[tuple[int, int], int] = {}
    order: dict[tuple[int, int], int] = {}
    for i in range(len(ids) - 1):
        pair = (ids[i], ids[i + 1])
        if pair not in counts:
            order[pair] = len(order)
            counts[pair] = 0
        counts[pair] += 1
    return counts, order


def train_word_bpe(
    word_freqs: dict[str, int], num_merges: int
) -> list[tuple[str, str]]:
    """Character-level BPE with ``</w>`` end markers — for the hand-worked teaching table.

    ``word_freqs`` maps whole words to frequencies (insertion order matters for ties).
    Returns the merge sequence as ``(left, right)`` string pairs.
    """
    if num_merges < 0:
        raise ValueError("num_merges must be >= 0")

    # Each word becomes a tuple of character tokens plus the end marker.
    words: dict[tuple[str, ...], int] = {}
    for word, freq in word_freqs.items():
        if freq <= 0:
            continue
        tokens = tuple(list(word) + ["</w>"])
        words[tokens] = words.get(tokens, 0) + freq

    merges: list[tuple[str, str]] = []
    for _ in range(num_merges):
        counts: dict[tuple[str, str], int] = {}
        order: dict[tuple[str, str], int] = {}
        for tokens, freq in words.items():
            for a, b in zip(tokens, tokens[1:]):
                pair = (a, b)
                if pair not in counts:
                    order[pair] = len(order)
                    counts[pair] = 0
                counts[pair] += freq
        if not counts:
            break
        best = _best_pair(counts, order)
        merges.append(best)
        a, b = best
        new_symbol = a + b
        new_words: dict[tuple[str, ...], int] = {}
        for tokens, freq in words.items():
            out: list[str] = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and tokens[i] == a and tokens[i + 1] == b:
                    out.append(new_symbol)
                    i += 2
                else:
                    out.append(tokens[i])
                    i += 1
            key = tuple(out)
            new_words[key] = new_words.get(key, 0) + freq
        words = new_words
    return merges


class BytePairTokenizer:
    """Byte-level BPE: base vocab 0–255, then learned merges."""

    def __init__(self) -> None:
        self.merges: list[tuple[int, int]] = []
        self.vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}

    # ------------------------------------------------------------------ train

    def train(self, text: str, vocab_size: int) -> None:
        """Learn merges from ``text`` until the vocabulary reaches ``vocab_size``.

        Base bytes occupy ids 0–255, so ``vocab_size`` must be >= 256.
        Ties (equal pair counts) break toward the pair seen first in the corpus.
        """
        if vocab_size < 256:
            raise ValueError("vocab_size must be >= 256 (byte base vocabulary)")

        ids = list(text.encode("utf-8"))
        merges: list[tuple[int, int]] = []
        vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}
        next_id = 256

        while next_id < vocab_size:
            counts, order = _count_pairs(ids)
            if not counts:
                break
            best = _best_pair(counts, order)
            a, b = best
            ids = _merge_sequence(ids, best, next_id)
            merges.append(best)
            vocab[next_id] = vocab[a] + vocab[b]
            next_id += 1

        self.merges = merges
        self.vocab = vocab

    # ------------------------------------------------------------- encode/decode

    def encode(self, text: str) -> list[int]:
        """Encode text to token ids by replaying merges in training order."""
        ids = list(text.encode("utf-8"))
        for offset, pair in enumerate(self.merges):
            new_id = 256 + offset
            ids = _merge_sequence(ids, pair, new_id)
        return ids

    def decode(self, ids: Iterable[int]) -> str:
        """Decode token ids back to a UTF-8 string.

        Unknown or out-of-range ids become the Unicode replacement character so
        bad id lists still print; valid Unicode round-trips stay lossless.
        """
        chunks: list[bytes] = []
        for i in ids:
            piece = self.vocab.get(i)
            if piece is None:
                chunks.append("\ufffd".encode("utf-8"))
            else:
                chunks.append(piece)
        return b"".join(chunks).decode("utf-8", errors="replace")

    # --------------------------------------------------------------- save/load

    def save(self, path: str | Path) -> None:
        """Write merges to JSON (vocab is rebuilt on load)."""
        path = Path(path)
        payload = {
            "version": 1,
            "merges": [[a, b] for a, b in self.merges],
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "BytePairTokenizer":
        """Load a tokenizer from a JSON merges file."""
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        tok = cls()
        merges = data.get("merges", [])
        tok.merges = [(int(a), int(b)) for a, b in merges]
        tok._rebuild_vocab()
        return tok

    def _rebuild_vocab(self) -> None:
        vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}
        for offset, (a, b) in enumerate(self.merges):
            vocab[256 + offset] = vocab[a] + vocab[b]
        self.vocab = vocab

    @property
    def vocab_size(self) -> int:
        return 256 + len(self.merges)

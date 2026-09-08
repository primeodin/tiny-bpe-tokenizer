# Contributing to tiny-bpe-tokenizer

Welcome. This repo is a **day-3 teaching BPE tokenizer** — train → encode → decode, byte-level, pure Python. Keep that bar in mind.

## Map (fork → PR)

1. **Fork** this repo on GitHub, then clone your fork:
   ```bash
   git clone https://github.com/<you>/tiny-bpe-tokenizer.git
   cd tiny-bpe-tokenizer
   ```
2. **Install** in editable mode with test deps:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Prove the wiring** before you change anything:
   ```bash
   pytest
   python3 main.py train --corpus data/sample.txt --vocab-size 400
   python3 main.py encode "low lower newest café 🚀"
   python3 main.py decode 108 111 119
   ```
   You want `12 passed`, and the train/encode/decode numbers in the README **Expected stdout** block. No API key needed.
4. **Branch** for one small change:
   ```bash
   git checkout -b my-first-pr
   ```
5. **Ship** a focused PR back to `primeodin/tiny-bpe-tokenizer`:
   - one idea per PR
   - include or update a test when behavior changes
   - say what you ran (`pytest`, the train/encode smoke)

## Touch the algorithm safely

1. Core lives in `src/tiny_bpe/bpe.py` (train / encode / decode + word-BPE teaching helper).
2. CLI is `src/tiny_bpe/cli.py`; `main.py` is a thin wrapper.
3. Hand-worked tables in the README are **tests**, not decoration — if you change merge order or tie-break, update the matching test under `tests/` and the README table together.
4. Prefer extending a hand-worked table or adding a deterministic CLI smoke over a theory dump.

Keep the tie rule: **ties go to the pair seen first.** That keeps training deterministic across machines.

## Good first issues

Scoped tickets (file named in the issue body):

- [#3 — CLI design review (flags, output shape, ergonomics)](https://github.com/primeodin/tiny-bpe-tokenizer/issues/3)

Claim one with a comment, ask questions in the thread, then open the PR. Docs and design notes count.

## Shop rules

- **Keep it small.** No Hugging Face / SentencePiece pile-ons, no extra services "while we're here."
- **Hand-worked stays sacred.** Offline tests and the README tables must keep matching — no "close enough."
- **Byte-level base vocab.** Keep 0–255 so any UTF-8 (emoji included) survives.
- **Lossless roundtrip.** `decode(encode(s)) == s` is a test, not a promise you can soft-pedal.
- **Teach by running.** Prefer a table + a test over a pitch deck.
- **Match the voice.** Short, concrete, honest — shop notes, not marketing.

## What to skip

Please don't open PRs that:

- pull in a heavy tokenizer/ML framework for the default path
- require network or paid APIs to train or encode
- rewrite the README for marketing tone
- bundle unrelated refactors with a feature
- "fix" merge order by eye without updating the hand-worked tables + tests

Questions? Comment on the issue you're claiming — that thread is the right place.

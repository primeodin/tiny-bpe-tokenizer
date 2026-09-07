# tiny-bpe-tokenizer

> Day-3 of PrimeOdin’s daily public builds — train a byte-pair encoding tokenizer from scratch and watch text become token IDs.

**Train → encode → decode.** Byte-level BPE, pure Python, no framework soup. The merge table below was worked out by hand so your run has to match it — or one of us has a bug.

## 60-second start

```bash
git clone https://github.com/primeodin/tiny-bpe-tokenizer.git
cd tiny-bpe-tokenizer
pip install -e ".[dev]"
pytest
python3 main.py train --corpus data/sample.txt --vocab-size 400
python3 main.py encode "low lower newest café 🚀"
python3 main.py decode 108 111 119
```

**Expected stdout** (deterministic on this corpus + flags — yours should match):

```text
# pytest
...........                                                              [100%]
11 passed

# train
merges learned: 144
first merges: (101,32), (32,116), (101,110), (101,114), (115,32), (116,32), (46,32), (105,110) ...
saved: tokenizer.json

# encode  →  "low lower newest café 🚀"
280 298 259 32 357 339 32 365
tokens: 8
chars-per-token: 2.875

# decode 108 111 119  →  raw UTF-8 bytes for "low" (no merges needed)
low
```

If train/encode numbers drift, either the corpus changed or the merge tie-break broke — open an issue before "fixing" the algorithm by eye.

## Why a tokenizer is the right first look under the hood

Every model you have ever typed at starts by chopping your sentence into pieces it has seen before. Not words. Not letters. **Pieces.** BPE is the boring, greedy rule that decides where the cuts go.

Once you can run it by hand, three mysteries go away:

- why a "1,000 token" limit is not 1,000 words
- why emoji and non-English text cost more
- why models are oddly bad at spelling and counting letters

## The whole algorithm, in five lines

1. Start from the smallest units (bytes, or characters) so every text is representable.
2. Count every adjacent pair.
3. Merge the most frequent pair into one new symbol.
4. Record that merge, in order.
5. Repeat until you hit your vocabulary budget.

**Encoding** = replay the merges in order. **Decoding** = paste the symbols back together. That is the entire trick.

## Watch it merge (by hand)

Corpus — three words, with `</w>` marking the end of a word:

```
low     ×5
lower   ×2
newest  ×3
```

Start: every word is a list of single characters. `l o w </w>`, `l o w e r </w>`, `n e w e s t </w>`

| Step | Winning pair | Count | New symbol | Corpus after |
| --- | --- | --- | --- | --- |
| 1 | `l` + `o` | 7 | `lo` | `lo w </w>` · `lo w e r </w>` · `n e w e s t </w>` |
| 2 | `lo` + `w` | 7 | `low` | `low </w>` · `low e r </w>` · `n e w e s t </w>` |
| 3 | `low` + `</w>` | 5 | `low</w>` | `low</w>` · `low e r </w>` · `n e w e s t </w>` |
| 4 | `n` + `e` | 3 | `ne` | `low</w>` · `low e r </w>` · `ne w e s t </w>` |
| 5 | `ne` + `w` | 3 | `new` | `low</w>` · `low e r </w>` · `new e s t </w>` |

Step 1 is a tie: `l`+`o` and `o`+`w` both score 7. **Ties go to the pair seen first**, which keeps the training deterministic — your run has to match mine or one of us has a bug.

Notice what happened: `low` swallowed three merges before `newest` got one. Frequency buys short tokens. That is exactly why a common English word is 1 token and your name might be 4.

## What you just built

| Piece | Job |
| --- | --- |
| `bpe.py` | Byte-level train / encode / decode + word-BPE teaching helper |
| `cli.py` | `train` / `encode` / `decode` over argparse |
| `main.py` | Thin wrapper so `python3 main.py …` works |
| `data/sample.txt` | Few-KB teaching corpus (emoji + café included) |
| `tests/test_bpe.py` | Hand-worked merge table + lossless roundtrips + CLI smoke |

Design constraints the code holds to:

- Pure **Python 3.10+**, standard library only at runtime (`pytest` for tests)
- **Byte-level base vocabulary** (0–255) so any UTF-8 input survives — emoji included
- **Lossless:** `decode(encode(s)) == s` is a test, not a promise
- Deterministic merges (ties → pair seen first), no network calls, no secrets

## Change one thing

1. Raise `--vocab-size` and watch chars-per-token climb on the same string  
2. Swap `data/sample.txt` for your own notes and retrain  
3. Extend the hand-worked table past step 5 — keep the same tie rule  

## Help / good first issues

Scoped tickets live in [Issues](https://github.com/primeodin/tiny-bpe-tokenizer/issues). Open contribution ideas:

- **#2** — unicode / emoji hand-worked merge table (docs + test)
- **#3** — CLI design review (flags, output shape, ergonomics)

New to pull requests? Start at [first-commit-ai](https://github.com/primeodin/first-commit-ai), then come back.

## Daily builds series

Tiny, tested teaching repos — starter → mid. Ship one, read it, then climb:

| Lane | Repo | Why open it |
| --- | --- | --- |
| Starter chat | [first-commit-ai](https://github.com/primeodin/first-commit-ai) | Mock-first chat CLI + pytest |
| Starter RAG | [notes-rag](https://github.com/primeodin/notes-rag) | Retrieve, cite, answer over Markdown notes |
| Starter tokenizer (this) | [tiny-bpe-tokenizer](https://github.com/primeodin/tiny-bpe-tokenizer) | Watch text become token IDs — train, encode, decode |
| Attention mid | [attention-warrior](https://github.com/primeodin/attention-warrior) | Transformer attention you can hold in one hand |
| Shop skills | [mister-jay](https://github.com/primeodin/mister-jay) | Interactive DIY drills (vehicle, electrical, plumbing) — [live](https://primeodin.github.io/mister-jay/) |
| Literacy (Sinhala) | [jay-ai-sinhala](https://github.com/primeodin/jay-ai-sinhala) | Friends 70+ learning GitHub + AI — [live](https://primeodin.github.io/jay-ai-sinhala/) |
| Systems DIY | [camera-selector](https://github.com/primeodin/camera-selector) | NVR/Frigate camera planning — [live](https://primeodin.github.io/camera-selector/) |

Weekday cadence, in order: chat CLI → RAG → tokenizer (this, shipped) → tool agent → prompt lab → embeddings → vision → memory → shop-skill explainer.

Profile forge: [github.com/primeodin](https://github.com/primeodin)

## License

MIT

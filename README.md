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

You should see merges learned, token IDs with a chars-per-token ratio, and a decoded string. That means training and round-trips work before you touch a line of the algorithm.

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

| Repo | Level |
| --- | --- |
| [first-commit-ai](https://github.com/primeodin/first-commit-ai) | starter chat CLI |
| [notes-rag](https://github.com/primeodin/notes-rag) | starter RAG |
| **tiny-bpe-tokenizer** (this) | starter tokenizer |
| next: tiny tool-calling agent (ReAct, no framework soup) | mid |

Full roadmap on the profile: [github.com/primeodin](https://github.com/primeodin)

## License

MIT

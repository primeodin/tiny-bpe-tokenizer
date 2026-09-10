# Why a "1,000 token" limit is not 1,000 words

Short shop note. The README already shows merges buying short tokens for common words — this page answers the *budget* question: when a model card says **8k tokens**, how many English words is that?

## The inheritance rule

Context windows, API bills, and "max tokens" knobs all count **pieces the tokenizer emits**, not spaces you typed.

So:

- A short common word can be **1** token
- A rare word, a name, or a typo can be **3–6** tokens
- A teaching vocab (this repo, `--vocab-size 400`) still fragments everyday English hard — that is a feature for learning, not a bug

Shop rule: **measure with `encode`, don't guess from word count.**

## Hand-worked trap (default train)

Commands (must match the README 60-second start):

```bash
python3 main.py train --corpus data/sample.txt --vocab-size 400
python3 main.py encode "…"
```

Verified on that model (piece strings from decoding each id alone):

| Text | Words | Tokens | tok / word | What the pieces look like |
| --- | ---: | ---: | ---: | --- |
| `hello world` | 2 | **8** | 4.0 | `h` · `e` · `l` · `lo` · ` w` · `or` · `l` · `d` |
| `The quick brown fox jumps` | 5 | **22** | 4.4 | `T` · `he ` · `q`…`k` · spaces · ` f` · `o` · `x` · `jumps` as letters |
| `I love machine learning` | 4 | **12** | 3.0 | `I` · `lo` · `v` · `e ` · `mach` · `in` · `e ` · `lear` · `n` · `ing` |
| `low lower newest` | 3 | **7** | 2.3 | `low` · ` low` · `er` · `new` · `es` · `t` (corpus pets) |
| `café 🚀` | 2 | **3** | 1.5 | `café` · ` ` · `🚀` (after merges — see [why-bytes](why-bytes.md)) |

Two words of `hello world` ate **eight** tokens. Five words of brown-fox ate **twenty-two**. If you budgeted "1,000 words ≈ 1,000 tokens," you just overran by ~4× on ordinary English with this tiny shop vocab.

## Same sentence, bigger budget

Raise `--vocab-size` on the **same** corpus and re-encode. More merges → fewer pieces for strings the corpus actually practiced:

| `--vocab-size` | `hello world` tokens | `The quick brown fox jumps` tokens | `I love machine learning` tokens |
| ---: | ---: | ---: | ---: |
| 300 | 9 | 23 | 15 |
| **400** (README default) | **8** | **22** | **12** |
| 600 | 7 | 21 | 12 |
| 800 | 7 | 21 | 12 |

Notice: fox barely moves after 400 — this sample corpus never practiced "quick" / "jumps" enough to glue them. **Vocab size is not magic.** It only compresses what training saw often. A production tokenizer with a huge web crawl will pack brown-fox tighter; the rule stays the same: words ≠ tokens.

## Why models feel "bad at spelling"

If `hello` arrives as `h` `e` `l` `lo`, the model never saw the letter sequence as one symbol. Asking it to "count the letters in hello" is asking it to reason across fragment boundaries it was not trained to treat as letters. Same story as the README mystery list — the budget and the spelling weirdness are the same cut.

## Shop tip (with judgment)

**When someone quotes a token limit, ask which tokenizer and run one encode on a real paragraph.** Safe hack for teaching: encode the same sentence at vocab 300 and 800, write the two counts on the whiteboard, then ask how many "words" fit in a 1,000-token box under each. That drill sticks harder than another diagram.

Unsafe on a live bill: estimating prompt size by `len(text.split())` and shipping it to a paid API. Spaces are not the meter. The meter is the merge table — measure it, or you find out when the 429 / truncated reply arrives.

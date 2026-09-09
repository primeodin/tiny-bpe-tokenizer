# Why bytes, not characters?

Short shop note. The README already walks a hand-worked `é🚀` merge table — this page answers the *design* question: why does the base vocab start at bytes `0–255` instead of Unicode code points?

## Character-level fails

If every new glyph gets its own symbol on day one, the vocab explodes the moment you leave ASCII:

- `é`, `ñ`, `中`, and every emoji are second-class — either missing or special-cased
- A fresh language (or one new emoji) means a fresh hole in the table
- You never get a clean "every string is representable" guarantee without a giant, brittle chart

Teaching on characters feels friendly until the first café menu. Then the lesson is about missing symbols, not about merges.

## Byte-level wins

UTF-8 already maps every Unicode string to a sequence of bytes. Start the vocab at those 256 values and:

- Any UTF-8 string is representable from day one (no mystery glyphs)
- Merges glue frequent byte pairs into readable chunks over time
- Emoji and accented Latin are the same algorithm as `low` / `lower` — just longer at the start

That is the whole trick. Bytes are the boring floor. Merges are the interesting part.

## Cost demo: `café` and `🚀`

Before any merge, count UTF-8 bytes (what the tokenizer actually sees):

| Text | Glyphs (what you see) | UTF-8 bytes | Cost before merges |
| --- | --- | --- | --- |
| `cafe` | 4 letters | `99 97 102 101` | **4** |
| `café` | 4 letters | `99 97 102 195 169` | **5** (`é` = `C3 A9`) |
| `🚀` | 1 emoji | `240 159 154 128` | **4** (`F0 9F 9A 80`) |

Same "four characters" in the editor; different bills at the register. `café` pays one extra byte for the accent. A fresh rocket pays four until merges glue it.

After training, frequent pairs collapse — the README unicode/emoji table shows `é` merging first, then the rocket assembling step by step into one token. Do not memorize that table here; open it when you want the worked merges:

→ [Watch bytes merge (unicode + emoji)](../README.md#watch-bytes-merge-unicode--emoji)

## Shop tip (with judgment)

**Start teaching on ASCII corpora** so the first merges are readable (`l`+`o` → `lo`). Switch in a `café` / emoji line only after the learner can predict the next merge on `low` / `lower` / `newest`.

Jumping straight to a multilingual dump makes lesson one feel like noise, not magic — the algorithm is the same, but the symbols look like hex soup before the story clicks. Once the merge rule is solid, the café line is the right slap: "one letter" is not "one token."

When the corpus is production multilingual text, byte-level is the right default. When the audience is day-one learners, ASCII first is kindness, not a cop-out.

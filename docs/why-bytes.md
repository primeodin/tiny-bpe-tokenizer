# Why bytes come first

Byte-level BPE starts with the 256 possible byte values, not a list of letters. That is the small move that lets it represent any UTF-8 text from day one.

## Characters run out of runway

A character vocabulary needs an entry for every glyph it expects to meet. New scripts, rare symbols, and emoji either enlarge that list forever or become a special unknown token. `é` and `🚀` should not be second-class input.

Bytes avoid that bargain. UTF-8 turns every string into values from 0 through 255, and the tokenizer already has all of them before training. BPE can then learn useful multi-byte pieces from the corpus.

## The receipt

Before any merges, UTF-8 costs these bytes:

| Text | UTF-8 bytes | Starting cost |
| --- | --- | --- |
| `café` | `63 61 66 c3 a9` | 5 bytes |
| `🚀` | `f0 9f 9a 80` | 4 bytes |

So a fresh byte vocabulary can encode both strings immediately. It does not need a predeclared `é` or rocket token.

The first cost is not the final cost. If `café` or `🚀` appears often in training text, merges can glue neighbouring bytes into learned pieces. The [unicode and emoji table in the README](../README.md#watch-bytes-merge-unicode--emoji) shows that happening step by step. The merge list is learned from the corpus, so another corpus may make different bargains.

## Shop tip

When teaching, start with ASCII text. You can see and predict each merge without decoding byte sequences in your head. Once the next merge feels obvious, add a `café` or `🚀` line. Starting with multilingual text is real, but it can make the first lesson feel like noise instead of the same small counting rule.

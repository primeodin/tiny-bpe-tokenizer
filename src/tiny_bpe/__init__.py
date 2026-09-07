"""Tiny byte-pair encoding tokenizer — train, encode, decode from scratch."""

from tiny_bpe.bpe import BytePairTokenizer, train_word_bpe

__version__ = "0.1.0"
__all__ = ["BytePairTokenizer", "train_word_bpe", "__version__"]

from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part and part.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        current_chunk: list[str] = []
        for sentence in sentences:
            current_chunk.append(sentence)
            if len(current_chunk) >= self.max_sentences_per_chunk:
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk).strip())

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        normalized_text = text.strip()
        if len(normalized_text) <= self.chunk_size:
            return [normalized_text]

        return self._split(normalized_text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []

        if len(current_text) <= self.chunk_size:
            return [current_text.strip()]

        if not remaining_separators:
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        separator = remaining_separators[0]
        if not separator:
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        parts = [part.strip() for part in current_text.split(separator) if part and part.strip()]
        if len(parts) <= 1:
            return self._split(current_text, remaining_separators[1:])

        groups: list[str] = []
        current_group: list[str] = []
        for part in parts:
            candidate = separator.join(current_group + [part]) if current_group else part
            if not current_group or len(candidate) <= self.chunk_size:
                current_group.append(part)
            else:
                groups.append(separator.join(current_group))
                current_group = [part]

        if current_group:
            groups.append(separator.join(current_group))

        chunks: list[str] = []
        for group in groups:
            if len(group) <= self.chunk_size:
                chunks.append(group)
            else:
                if len(remaining_separators) > 1:
                    chunks.extend(self._split(group, remaining_separators[1:]))
                else:
                    chunks.extend([group[i : i + self.chunk_size] for i in range(0, len(group), self.chunk_size)])

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0

    common_length = min(len(vec_a), len(vec_b))
    a = vec_a[:common_length]
    b = vec_b[:common_length]

    norm_a = math.sqrt(sum(value * value for value in a))
    norm_b = math.sqrt(sum(value * value for value in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return _dot(a, b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        chunkers = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3).chunk(text),
            "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
        }

        result: dict = {}
        for strategy_name, chunks in chunkers.items():
            avg_length = sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0.0
            result[strategy_name] = {
                "count": len(chunks),
                "avg_length": avg_length,
                "chunks": chunks,
            }

        return result

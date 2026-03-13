from __future__ import annotations


def multiply_vector(vector: list[float], weight: float) -> list[float]:
    return [value * weight for value in vector]


def add_vectors(left: list[float], right: list[float]) -> list[float]:
    validate_same_dimension(left, right)
    return [l + r for l, r in zip(left, right)]


def validate_same_dimension(left: list[float], right: list[float]) -> None:
    if len(left) != len(right):
        raise ValueError(
            f"Vector dimensions do not match. left={len(left)}, right={len(right)}"
        )


def to_pgvector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


def zero_vector(size: int) -> list[float]:
    return [0.0] * size

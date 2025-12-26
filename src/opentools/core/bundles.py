from __future__ import annotations

from typing import Iterable, Sequence

from .tools import ToolBundle, ToolSpec
from .types import ModelName


def build_bundle(model: ModelName, specs: Sequence[ToolSpec]) -> ToolBundle:
    if model == "anthropic":
        from opentools.adapters.models.anthropic.bundle import to_anthropic_bundle

        return to_anthropic_bundle(list(specs))

    if model == "openai":
        from opentools.adapters.models.openai.bundle import to_openai_bundle

        return to_openai_bundle(list(specs))

    if model == "gemini":
        from opentools.adapters.models.gemini.bundle import to_gemini_bundle

        return to_gemini_bundle(list(specs))

    if model == "ollama":
        from opentools.adapters.models.ollama.bundle import to_ollama_bundle

        return to_ollama_bundle(list(specs))

    if model == "openrouter":
        from opentools.adapters.models.openrouter.bundle import (
            to_openrouter_bundle,
        )

        return to_openrouter_bundle(list(specs))

    raise ValueError(f"Unknown model: {model!r}")


def cached_bundle_for(
    *,
    model: ModelName,
    specs: Iterable[ToolSpec],
    cache: dict[tuple[ModelName, tuple[str, ...], tuple[str, ...]], ToolBundle],
    include: tuple[str, ...],
    exclude: tuple[str, ...],
) -> ToolBundle:
    """
    Helper for domain services that want to cache bundles by
    (model, include, exclude).
    """

    key = (model, include, exclude)
    if key in cache:
        return cache[key]

    specs_list = list(specs)
    bundle = build_bundle(model, specs_list)
    cache[key] = bundle
    return bundle

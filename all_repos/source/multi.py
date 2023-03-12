from __future__ import annotations

from typing import NamedTuple


class MultiSource(NamedTuple):
    source: str
    settings: dict | None


def import_multi_source(settings: MultiSource):
    return __import__(settings["source"], fromlist=["__trash"])


class Settings(NamedTuple):
    sources: list[MultiSource]
    shared_settings: dict | None


def list_repos(settings: Settings) -> dict[str, str]:
    result = {}
    for multi in settings.sources:
        source_module = import_multi_source(multi)
        merged_settings = multi["settings"] | settings.shared_settings
        source_settings = source_module.Settings(**merged_settings)
        result = result | source_module.list_repos(source_settings)

    return result

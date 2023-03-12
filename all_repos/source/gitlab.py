from __future__ import annotations

from typing import NamedTuple

from all_repos import gitlab_api
from all_repos.util import hide_api_key_repr, load_api_key


class Settings(NamedTuple):
    username: str
    base_url: str = "https://gitlab.com/api/v4"
    archived: bool = False
    api_key: str | None = None
    api_key_env: str | None = None

    def __repr__(self) -> str:
        return hide_api_key_repr(self)


def list_repos(settings: Settings) -> dict[str, str]:
    repos = gitlab_api.get_all(
        f"{settings.base_url}/users/{settings.username}/projects",
        headers={"Private-Token": load_api_key(settings)},
    )
    return gitlab_api.filter_repos_from_settings(repos, settings)

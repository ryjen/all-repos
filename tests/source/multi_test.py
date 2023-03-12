from __future__ import annotations

import json
from unittest import mock

import pytest

from all_repos.source import github, gitlab_org, multi
from testing.mock_http import FakeResponse, urlopen_side_effect


def _resource_json(repo_name, repo_dir="github"):
    with open(f"testing/resources/{repo_dir}/{repo_name}.json") as f:
        return json.load(f)


def __multi_modules():
    yield github
    yield gitlab_org


def __multi_responses():
    yield __github_resp
    yield __gitlab_resp


__multi_modules = __multi_modules()
__multi_responses = __multi_responses()

__github_resp = [
    # full permissions
    _resource_json("git-code-debt"),
    # A contributor repo
    _resource_json("libsass-python"),
    # A fork
    _resource_json("tox"),
    # A private repo
    _resource_json("eecs381-p4"),
    # An archived repo
    _resource_json("poi-map"),
]

__gitlab_resp = _resource_json("org-listing", "gitlab")


def mock_import(settings):
    return next(__multi_modules)


@pytest.fixture
def test_settings():
    return multi.Settings(
        sources=[
            {
                "source": "all_repos.source.github",
                "settings": {"username": "abc"},
            },
            {
                "source": "all_repos.source.gitlab_org",
                "settings": {"org": "xyz"},
            },
        ],
        shared_settings={"archived": False, "api_key": "..."},
    )


@pytest.fixture
def repos_response(mock_urlopen):
    mock_urlopen.side_effect = urlopen_side_effect(
        {
            "https://api.github.com/user/repos?per_page=100": FakeResponse(
                json.dumps(__github_resp).encode(),
            ),
            "https://gitlab.com/api/v4/groups/xyz/projects?with_shared=False&include_subgroups=true": FakeResponse(
                json.dumps(__gitlab_resp).encode(),
            ),
        }
    )
    next(__multi_responses)


def test_settings_repr(test_settings):
    assert (
        repr(test_settings)
        == "Settings(sources=[{'source': 'all_repos.source.github', 'settings': {'username': 'abc'}}, {'source': 'all_repos.source.gitlab_org', 'settings': {'org': 'xyz'}}], shared_settings={'archived': False, 'api_key': '...'})"
    )


@pytest.mark.usefixtures("repos_response")
@mock.patch("all_repos.source.multi.import_multi_source", mock_import)
def test_list_repos(test_settings):
    res = multi.list_repos(test_settings)
    assert res == {
        "asottile/git-code-debt": "git@github.com:asottile/git-code-debt",
        "ronny-test/test-repo": "git@gitlab.com:ronny-test/test-repo.git",
    }

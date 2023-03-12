from __future__ import annotations

import json

import pytest

from all_repos.source.gitlab import Settings, list_repos
from testing.mock_http import FakeResponse, urlopen_side_effect


def _resource_json(name):
    with open(f"testing/resources/gitlab/{name}.json") as f:
        return json.load(f)


@pytest.fixture
def repos_response(mock_urlopen):
    mock_urlopen.side_effect = urlopen_side_effect(
        {
            "https://gitlab.com/api/v4/users/ronny-test/projects": FakeResponse(
                json.dumps(_resource_json("user-listing")).encode(),
            ),
        }
    )


def test_list_repos(repos_response):
    settings = Settings(api_key="key", username="ronny-test")
    ret = list_repos(settings)
    expected = {
        "ronny-test/test-repo": "git@gitlab.com:ronny-test/test-repo.git",
    }
    assert ret == expected


def test_settings_repr():
    assert repr(Settings(api_key="key", username="sass")) == (
        "Settings(\n"
        "    username='sass',\n"
        "    base_url='https://gitlab.com/api/v4',\n"
        "    archived=False,\n"
        "    api_key=...,\n"
        "    api_key_env=None,\n"
        ")"
    )

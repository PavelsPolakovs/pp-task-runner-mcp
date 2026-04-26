"""Unit tests for non-browser MCP tools (in-process, no subprocess)."""
import asyncio
import json
from unittest.mock import MagicMock, patch

from menu_mcp.constants import TASKS

FIRST_SKILL = next(iter(TASKS))


def call(app, tool, **kwargs):
    return asyncio.run(app.call_tool(tool, kwargs))


def text(result):
    return result[1]["result"]


class TestListSkills:
    def test_returns_all_skills(self, mcp_app):
        data = json.loads(text(call(mcp_app, "list_skills")))
        assert [s["name"] for s in data] == list(TASKS.keys())

    def test_includes_name_and_description(self, mcp_app):
        data = json.loads(text(call(mcp_app, "list_skills")))
        for item in data:
            assert "name" in item and "description" in item


class TestSelectSkill:
    def test_known_skill(self, mcp_app):
        assert f"Activated: {FIRST_SKILL}" in text(call(mcp_app, "select_skill", name=FIRST_SKILL))

    def test_unknown_skill(self, mcp_app):
        assert "Unknown skill" in text(call(mcp_app, "select_skill", name="__nonexistent__"))

    def test_sets_active_skill(self, mcp_app):
        call(mcp_app, "select_skill", name=FIRST_SKILL)
        assert FIRST_SKILL in text(call(mcp_app, "get_active_skill"))


class TestGetActiveSkill:
    def test_initially_empty(self, mcp_app):
        assert "No skill selected" in text(call(mcp_app, "get_active_skill"))

    def test_after_select(self, mcp_app):
        call(mcp_app, "select_skill", name=FIRST_SKILL)
        assert FIRST_SKILL in text(call(mcp_app, "get_active_skill"))


class TestUpdate:
    def test_success(self, mcp_app):
        mock = MagicMock(returncode=0, stdout="Already up to date.\n", stderr="")
        with patch("subprocess.run", return_value=mock):
            result = text(call(mcp_app, "update"))
        assert "Updated successfully" in result
        assert "Reconnect" in result

    def test_git_failure(self, mcp_app):
        mock = MagicMock(returncode=1, stdout="", stderr="fatal: not a git repo")
        with patch("subprocess.run", return_value=mock):
            result = text(call(mcp_app, "update"))
        assert "failed" in result.lower()
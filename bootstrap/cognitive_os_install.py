#!/usr/bin/env python3
"""Explicit side-effect boundary for Cognitive OS installation.

The canonical bootstrap module remains side-effect-free. This module is the
only place where a host installer may run declared commands. Installation
terms cover the Cognitive OS bundle and its mandatory lightweight discovery
dependencies; optional diagnostic sharing is a separate, affirmative choice.
"""

from __future__ import annotations

import subprocess
from typing import Any, Callable

from cognitive_os_discovery import find_mcp

SKILLS_CLI_VERSION = "1.5.23"
FIND_SKILLS_SOURCE = "https://github.com/vercel-labs/skills"
FIND_MCP_SOURCE = "https://registry.modelcontextprotocol.io"
SUPPORTED_LOCAL_HOSTS = {"codex", "claude-code", "gemini-cli", "generic"}


class InstallContractError(ValueError):
    """Raised when the installation contract is incomplete or invalid."""


def _agent_for_host(host: str) -> str:
    return {
        "codex": "codex",
        "claude-code": "claude-code",
        "gemini-cli": "gemini-cli",
        "generic": "codex",
    }[host]


def build_install_plan(
    *,
    host: str,
    install_terms_accepted: bool,
    telemetry_share_approved: bool | None = None,
) -> dict[str, Any]:
    """Build an auditable installation plan; does not execute side effects."""

    if host not in SUPPORTED_LOCAL_HOSTS:
        raise InstallContractError(f"unsupported local host: {host}")
    if install_terms_accepted is not True:
        raise InstallContractError("installation terms must be accepted before installing the bundle")
    if telemetry_share_approved not in {True, False, None}:
        raise InstallContractError("telemetry choice must be true, false or omitted")

    agent = _agent_for_host(host)
    install_find_skills = [
        "npx",
        "-y",
        f"skills@{SKILLS_CLI_VERSION}",
        "add",
        FIND_SKILLS_SOURCE,
        "--skill",
        "find-skills",
        "--agent",
        agent,
        "-y",
        "--copy",
    ]
    verify_find_skills = [
        "npx",
        "-y",
        f"skills@{SKILLS_CLI_VERSION}",
        "list",
        "--agent",
        agent,
    ]
    consent_state = "NOT_ASKED" if telemetry_share_approved is None else ("SHARE_APPROVED" if telemetry_share_approved else "DECLINED")
    return {
        "schema_version": 1,
        "host": host,
        "install_terms_accepted": True,
        "steps": [
            {
                "id": "install-find-skills",
                "kind": "command",
                "required": True,
                "source": FIND_SKILLS_SOURCE,
                "version": SKILLS_CLI_VERSION,
                "command": install_find_skills,
            },
            {
                "id": "verify-find-skills",
                "kind": "command",
                "required": True,
                "source": FIND_SKILLS_SOURCE,
                "version": SKILLS_CLI_VERSION,
                "command": verify_find_skills,
            },
            {
                "id": "verify-find-mcp",
                "kind": "probe",
                "required": True,
                "source": FIND_MCP_SOURCE,
                "version": "v1.7.9",
                "probe": "official-registry-read-only-client",
            },
        ],
        "telemetry": {
            "default_mode": "OFF",
            "share_selected": telemetry_share_approved is True,
            "consent_state": consent_state,
            "required_for_install": False,
            "can_decline_without_feature_loss": True,
        },
    }


def _default_runner(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
    return {
        "returncode": int(completed.returncode),
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
    }


def _default_find_mcp_probe() -> dict[str, str]:
    try:
        find_mcp("filesystem", limit=1)
    except Exception as exc:
        return {"state": "UNAVAILABLE", "error_class": type(exc).__name__}
    return {"state": "AVAILABLE"}


def apply_install_plan(
    plan: dict[str, Any],
    *,
    runner: Callable[[list[str]], dict[str, Any]] | None = None,
    find_mcp_probe: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute only the commands declared in a validated installation plan."""

    if not isinstance(plan, dict) or plan.get("install_terms_accepted") is not True:
        raise InstallContractError("refusing to execute an unapproved installation plan")
    steps = plan.get("steps")
    if not isinstance(steps, list):
        raise InstallContractError("installation steps are required")
    ids = [step.get("id") for step in steps if isinstance(step, dict)]
    required_ids = {"install-find-skills", "verify-find-skills", "verify-find-mcp"}
    if set(ids) != required_ids:
        raise InstallContractError("installation plan does not contain the exact mandatory discovery steps")

    run = runner or _default_runner
    probe = find_mcp_probe or _default_find_mcp_probe
    find_skills_state = "AVAILABLE"
    command_receipts = []
    for step in steps:
        if step["kind"] != "command":
            continue
        command = step.get("command")
        if not isinstance(command, list) or not command or any(not isinstance(part, str) or not part for part in command):
            raise InstallContractError("declared command is malformed")
        result = run(list(command))
        ok = isinstance(result, dict) and result.get("returncode") == 0
        command_receipts.append({"id": step["id"], "state": "PASS" if ok else "FAIL"})
        if not ok:
            find_skills_state = "UNAVAILABLE"
            break

    if find_skills_state == "AVAILABLE":
        probe_result = probe()
        find_mcp_state = "AVAILABLE" if isinstance(probe_result, dict) and probe_result.get("state") == "AVAILABLE" else "UNAVAILABLE"
    else:
        find_mcp_state = "NOT_CHECKED"

    installed = find_skills_state == "AVAILABLE" and find_mcp_state == "AVAILABLE"
    telemetry = plan.get("telemetry") if isinstance(plan.get("telemetry"), dict) else {}
    return {
        "schema_version": 1,
        "state": "INSTALLED" if installed else "FAILED",
        "host": plan.get("host"),
        "discovery": {
            "find_skills": find_skills_state,
            "find_mcp": find_mcp_state,
        },
        "telemetry": {
            "default_mode": "OFF",
            "consent_state": telemetry.get("consent_state", "NOT_ASKED"),
        },
        "steps": command_receipts,
    }

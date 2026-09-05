#!/usr/bin/env python3
"""Read-only external discovery clients bundled with Cognitive OS.

Discovery is not adoption: this module can search approved registries, but it
never installs, connects to, authenticates with, or executes a discovered
candidate.
"""

from __future__ import annotations

import json
from typing import Any, Callable
from urllib import request
from urllib.parse import urlencode

MCP_REGISTRY_BASE_URL = "https://registry.modelcontextprotocol.io"
MCP_REGISTRY_SERVERS_PATH = "/v0.1/servers"
MCP_REGISTRY_TIMEOUT_SECONDS = 30
MAX_QUERY_LENGTH = 256
MAX_RESULTS = 100


class DiscoveryClientError(ValueError):
    """Raised when a discovery request or registry response violates contract."""


def _validate_query(query: str) -> str:
    if not isinstance(query, str):
        raise DiscoveryClientError("query must be text")
    value = query.strip()
    if not value:
        raise DiscoveryClientError("query must not be blank")
    if len(value) > MAX_QUERY_LENGTH:
        raise DiscoveryClientError("query is too long")
    if any(char in value for char in "\r\n\x00"):
        raise DiscoveryClientError("query contains invalid control characters")
    return value


def _validate_limit(limit: int) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not (1 <= limit <= MAX_RESULTS):
        raise DiscoveryClientError(f"limit must be an integer from 1 to {MAX_RESULTS}")
    return limit


def _parse_server_list(payload: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not isinstance(payload, dict):
        raise DiscoveryClientError("registry response must be an object")
    servers = payload.get("servers")
    if not isinstance(servers, list) or any(not isinstance(item, dict) for item in servers):
        raise DiscoveryClientError("registry response servers must be a list of objects")
    metadata = payload.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise DiscoveryClientError("registry response metadata must be an object")
    count = metadata.get("count")
    if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 0):
        raise DiscoveryClientError("registry metadata count is invalid")
    next_cursor = metadata.get("nextCursor")
    if next_cursor is not None and not isinstance(next_cursor, str):
        raise DiscoveryClientError("registry metadata nextCursor is invalid")
    return servers, metadata


def find_mcp(
    query: str,
    *,
    limit: int = 10,
    opener: Callable[..., Any] | None = None,
    timeout: int = MCP_REGISTRY_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Search the Official MCP Registry without adopting a returned candidate.

    `opener` is injectable for deterministic tests. Production callers use
    `urllib.request.urlopen`. The registry has occasionally shown higher read
    latency, so the default timeout is deliberately 30 seconds.
    """

    value = _validate_query(query)
    count = _validate_limit(limit)
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout < 1 or timeout > 60:
        raise DiscoveryClientError("timeout must be an integer from 1 to 60 seconds")

    params = urlencode({"search": value, "limit": count})
    url = f"{MCP_REGISTRY_BASE_URL}{MCP_REGISTRY_SERVERS_PATH}?{params}"
    req = request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "cognitive-os/1.5 find-mcp",
        },
    )
    open_fn = opener or request.urlopen
    try:
        with open_fn(req, timeout=timeout) as response:
            raw = response.read()
    except Exception as exc:  # provider/network failure remains a bounded discovery failure
        raise DiscoveryClientError(f"official MCP registry request failed: {type(exc).__name__}") from exc

    if not isinstance(raw, (bytes, bytearray)) or len(raw) > 5_000_000:
        raise DiscoveryClientError("registry response is invalid or too large")
    try:
        payload = json.loads(bytes(raw).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DiscoveryClientError("registry response is not valid UTF-8 JSON") from exc

    servers, metadata = _parse_server_list(payload)
    return {
        "source": MCP_REGISTRY_BASE_URL,
        "endpoint": MCP_REGISTRY_SERVERS_PATH,
        "query": value,
        "limit": count,
        "servers": servers,
        "metadata": metadata,
        "installation_performed": False,
        "execution_performed": False,
        "next_action": "GAUNTLET_CANDIDATES_BEFORE_ADOPTION" if servers else "NO_CANDIDATES_FOUND",
    }

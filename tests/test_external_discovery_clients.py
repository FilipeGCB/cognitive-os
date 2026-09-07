import io
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_discovery import DiscoveryClientError, find_mcp  # noqa: E402


class _Response:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


class ExternalDiscoveryClientTests(unittest.TestCase):
    def test_find_mcp_queries_only_official_registry_with_encoded_search(self):
        seen = {}

        def opener(req, timeout=0):
            seen["url"] = req.full_url
            seen["method"] = req.get_method()
            seen["timeout"] = timeout
            return _Response({"servers": [], "metadata": {"count": 0}})

        result = find_mcp("file system / safe", limit=7, opener=opener)
        parsed = urlparse(seen["url"])
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "registry.modelcontextprotocol.io")
        self.assertEqual(parsed.path, "/v0.1/servers")
        self.assertEqual(query["search"], ["file system / safe"])
        self.assertEqual(query["limit"], ["7"])
        self.assertEqual(seen["method"], "GET")
        self.assertGreaterEqual(seen["timeout"], 20)
        self.assertEqual(result["servers"], [])
        self.assertEqual(result["source"], "https://registry.modelcontextprotocol.io")

    def test_find_mcp_rejects_unbounded_limit(self):
        for invalid in (0, 101, -1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(DiscoveryClientError):
                    find_mcp("filesystem", limit=invalid, opener=lambda *_args, **_kwargs: None)

    def test_find_mcp_rejects_blank_or_oversized_query(self):
        for invalid in ("", "   ", "x" * 257):
            with self.subTest(invalid=invalid[:20]):
                with self.assertRaises(DiscoveryClientError):
                    find_mcp(invalid, opener=lambda *_args, **_kwargs: None)

    def test_find_mcp_validates_server_list_shape(self):
        def opener(_req, timeout=0):
            return _Response({"servers": "not-a-list"})

        with self.assertRaises(DiscoveryClientError):
            find_mcp("filesystem", opener=opener)

    def test_find_mcp_preserves_candidate_metadata_without_executing_candidate(self):
        server = {
            "server": {
                "name": "io.example/filesystem",
                "version": "1.2.3",
                "description": "Example",
                "packages": [{"registryType": "npm", "identifier": "@example/mcp", "transport": {"type": "stdio"}}],
            },
            "_meta": {"official": {"status": "active"}},
        }

        def opener(_req, timeout=0):
            return _Response({"servers": [server], "metadata": {"count": 1, "nextCursor": "next"}})

        result = find_mcp("filesystem", opener=opener)
        self.assertEqual(result["servers"], [server])
        self.assertEqual(result["metadata"]["count"], 1)
        self.assertEqual(result["metadata"]["nextCursor"], "next")
        self.assertFalse(result["execution_performed"])
        self.assertFalse(result["installation_performed"])


if __name__ == "__main__":
    unittest.main()

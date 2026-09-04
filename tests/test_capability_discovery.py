import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_bootstrap import (  # noqa: E402
    CapabilityState,
    DiscoveryAsset,
    assess_candidate,
    plan_discovery,
    run_discovery_pipeline,
)


class CapabilityDiscoveryTests(unittest.TestCase):
    def test_existing_capability_is_preferred_over_external_discovery(self):
        state = CapabilityState(
            "Document/File Research",
            "AVAILABLE",
            "NOT_REQUIRED",
            "NOT_REQUIRED",
            "NOT_CALLED",
            None,
        )
        plan = plan_discovery(
            "Document/File Research",
            state,
            local_skills=["document-research"],
            external_assets=[DiscoveryAsset.blocked("find-skills")],
        )
        self.assertEqual(plan.action, "USE_EXISTING")
        self.assertIsNone(plan.external_asset_id)

    def test_local_skill_is_used_when_external_discovery_is_unavailable(self):
        state = CapabilityState(
            "Security Analysis",
            "UNAVAILABLE",
            "NOT_REQUIRED",
            "NOT_REQUIRED",
            "NOT_CALLED",
            None,
        )
        plan = plan_discovery(
            "Security Analysis",
            state,
            local_skills=["security-review"],
            external_assets=[DiscoveryAsset.blocked("find-skills")],
        )
        self.assertEqual(plan.action, "USE_LOCAL_SKILL")
        self.assertEqual(plan.discovery_class, "LOCAL_SKILL_DISCOVERY")

    def test_external_discovery_unavailable_is_explicit(self):
        state = CapabilityState(
            "Structured Crawl",
            "UNAVAILABLE",
            "NOT_REQUIRED",
            "NOT_REQUIRED",
            "NOT_CALLED",
            None,
        )
        plan = plan_discovery(
            "Structured Crawl",
            state,
            external_assets=[DiscoveryAsset.blocked("find-mcp")],
        )
        self.assertEqual(plan.action, "EXTERNAL_DISCOVERY_UNAVAILABLE")
        self.assertEqual(plan.external_availability, "UNAVAILABLE")
        self.assertEqual(plan.invocation, "NOT_CALLED")
        self.assertEqual(plan.fallback, "MANUAL_OR_COMPOSED_RESEARCH")

    def test_discovery_asset_does_not_authorize_candidate(self):
        asset = DiscoveryAsset(
            id="approved-find-mcp",
            asset_type="EXTERNAL_MCP_DISCOVERY",
            source="https://example.invalid/find-mcp",
            owner="example",
            repository="example/find-mcp",
            maintainer="example-maintainer",
            version="1.0.0",
            license="Apache-2.0",
            mechanism="registry-search",
            status="APPROVED",
        )
        candidate = {
            "id": "unreviewed-candidate",
            "source": "https://example.invalid/candidate",
            "version": "1.0.0",
            "license": "MIT",
            "gauntlet_status": "UNKNOWN",
            "permissions": {"network": True},
        }
        assessment = assess_candidate(candidate, asset=asset, ephemeral=True)
        self.assertEqual(assessment.status, "QUARANTINED")
        self.assertFalse(assessment.execution_allowed)
        self.assertTrue(assessment.security_required)

    def test_ephemeral_execution_still_requires_gauntlet_and_consent(self):
        asset = DiscoveryAsset(
            id="approved-find-mcp",
            asset_type="EXTERNAL_MCP_DISCOVERY",
            source="https://example.invalid/find-mcp",
            owner="example",
            repository="example/find-mcp",
            maintainer="example-maintainer",
            version="1.0.0",
            license="Apache-2.0",
            mechanism="registry-search",
            status="APPROVED",
        )
        candidate = {
            "id": "read-only-candidate",
            "source": "https://example.invalid/candidate",
            "version": "1.0.0",
            "license": "MIT",
            "gauntlet_status": "PASS",
            "permissions": {"network": True, "write": False},
            "account_bound": True,
            "requires_specific_consent": True,
        }
        assessment = assess_candidate(candidate, asset=asset, ephemeral=True)
        self.assertEqual(assessment.status, "PERSISTENT_ADOPTION_PENDING_CONSENT")
        self.assertFalse(assessment.execution_allowed)
        self.assertTrue(assessment.consent_required)

    def test_authenticated_capability_without_run_consent_cannot_be_called(self):
        state = CapabilityState(
            "Grounded Corpus Research",
            "AVAILABLE",
            "AUTHENTICATED",
            "NOT_GRANTED",
            "NOT_CALLED",
            None,
            consent_required=True,
        )
        plan = plan_discovery("Grounded Corpus Research", state)
        self.assertEqual(plan.action, "REQUEST_RUN_CONSENT")
        self.assertEqual(plan.invocation, "NOT_CALLED")
        self.assertFalse(plan.execution_allowed)

    def test_registry_records_unproven_discovery_assets_as_blocked(self):
        registry = json.loads((ROOT / "adapters" / "registry.json").read_text(encoding="utf-8"))
        assets = registry["discovery_assets"]
        self.assertEqual({asset["status"] for asset in assets}, {"BLOCKED"})
        self.assertTrue(all(asset["identity_status"] == "UNPROVEN" for asset in assets))
        self.assertTrue(all(asset["source"] is None for asset in assets))

    def test_pipeline_triages_candidate_without_executing_it(self):
        asset = DiscoveryAsset(
            id="approved-find-skills",
            asset_type="EXTERNAL_SKILL_DISCOVERY",
            source="https://example.invalid/find-skills",
            owner="example",
            repository="example/find-skills",
            maintainer="example-maintainer",
            version="1.0.0",
            license="Apache-2.0",
            mechanism="registry-search",
            status="APPROVED",
        )
        state = CapabilityState("Metrics", "UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "NOT_CALLED", None)
        result = run_discovery_pipeline(
            "Metrics",
            state,
            external_assets=(asset,),
            candidate_records=({
                "id": "read-only-skill",
                "source": "https://example.invalid/read-only-skill",
                "version": "1.0.0",
                "license": "MIT",
                "gauntlet_status": "PASS",
                "permissions": {"network": False, "write": False},
            },),
        )
        self.assertEqual(result.shortlist, ("read-only-skill",))
        self.assertEqual(result.selected_candidate_id, "read-only-skill")
        self.assertEqual(result.invocation, "NOT_CALLED")
        self.assertEqual(result.result, "NOT_APPLICABLE")

    def test_network_only_candidate_is_not_promoted_to_account_consent_without_that_scope(self):
        asset = DiscoveryAsset(
            id="approved-find-mcp",
            asset_type="EXTERNAL_MCP_DISCOVERY",
            source="https://example.invalid/find-mcp",
            owner="example",
            repository="example/find-mcp",
            maintainer="example-maintainer",
            version="1.0.0",
            license="Apache-2.0",
            mechanism="registry-search",
            status="APPROVED",
        )
        assessment = assess_candidate({
            "id": "public-read-candidate",
            "source": "https://example.invalid/candidate",
            "version": "1.0.0",
            "license": "MIT",
            "gauntlet_status": "PASS",
            "permissions": {"network": True, "write": False},
        }, asset=asset, ephemeral=True)
        self.assertTrue(assessment.execution_allowed)
        self.assertFalse(assessment.consent_required)


if __name__ == "__main__":
    unittest.main()

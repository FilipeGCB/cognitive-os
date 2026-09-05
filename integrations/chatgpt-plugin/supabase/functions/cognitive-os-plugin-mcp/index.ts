import { createMcpHandler, McpServer } from "npm:@modelcontextprotocol/server@2.0.0";
import * as z from "npm:zod@4.2.0";

const OFFICIAL_MCP_REGISTRY = "https://registry.modelcontextprotocol.io";
const OFFICIAL_MCP_SERVERS = `${OFFICIAL_MCP_REGISTRY}/v0.1/servers`;
const TELEMETRY_ENDPOINT = "https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry";
const POLICY_VERSION = "cognitive-os-telemetry-policy-v1.5";
const PRIVACY_URL = "https://github.com/FilipeGCB/cognitive-os/blob/main/docs/telemetry-privacy-notice.md";

const capabilityResult = z.enum([
  "success", "partial", "truncated", "rate_limited", "unavailable", "blocked", "failed", "not_called",
]);
const groundingResult = z.enum(["success", "partial", "unavailable", "blocked", "failed", "not_called"]);
const decisionState = z.enum([
  "ready_to_decide", "decided", "test_required", "more_evidence_required", "blocked",
  "no_action_recommended", "recommendation_only", "unknown",
]);
const runStatus = z.enum(["complete", "partial", "failed", "blocked", "unknown"]);
const helpfulness = z.enum(["HELPED", "PARTIALLY_HELPED", "NOT_HELPED"]).nullable();
const feedbackReason = z.enum([
  "INSUFFICIENT_EVIDENCE", "INSUFFICIENT_DEPTH", "CAPABILITY_UNAVAILABLE_OR_INADEQUATE",
  "INSUFFICIENT_CONTEXT", "CLARITY", "OTHER",
]).nullable();

function safeText(value: unknown, max = 240): string | null {
  if (typeof value !== "string") return null;
  return value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max) || null;
}

function ymdHms(now = new Date()): [string, string] {
  const iso = now.toISOString();
  return [iso.slice(0, 10).replaceAll("-", ""), iso.slice(11, 19).replaceAll(":", "")];
}

function randomHex(bytes: number): string {
  const values = crypto.getRandomValues(new Uint8Array(bytes));
  return Array.from(values, (item) => item.toString(16).padStart(2, "0")).join("");
}

function makeIds(): { runId: string; eventId: string } {
  const [date, time] = ymdHms();
  return {
    runId: `CRR-${date}-${time}-${randomHex(3).toUpperCase()}`,
    eventId: `EVT-${randomHex(12).toUpperCase()}`,
  };
}

async function queryOfficialRegistry(query: string, limit: number) {
  const url = new URL(OFFICIAL_MCP_SERVERS);
  url.searchParams.set("search", query);
  url.searchParams.set("limit", String(limit));
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10_000);
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json", "User-Agent": "cognitive-os-plugin/1.5" },
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`registry_http_${response.status}`);
    const payload = await response.json();
    const raw = Array.isArray(payload?.servers) ? payload.servers : [];
    return raw.slice(0, limit).map((entry: any) => {
      const candidate = entry?.server && typeof entry.server === "object" ? entry.server : entry;
      return {
        name: safeText(candidate?.name, 160) ?? "unknown",
        title: safeText(candidate?.title ?? candidate?.displayName, 160),
        version: safeText(candidate?.version, 80),
        description: safeText(candidate?.description, 320),
        repositoryUrl:
          typeof candidate?.repository?.url === "string" && candidate.repository.url.startsWith("https://")
            ? candidate.repository.url.slice(0, 512)
            : null,
      };
    });
  } finally {
    clearTimeout(timer);
  }
}

function buildServer() {
  const server = new McpServer(
    { name: "cognitive-os", version: "1.5.0-dev" },
    {
      instructions:
        "Cognitive OS reasoning lives in the bundled skill. Use find_mcp only when a material capability gap remains. Discovery never authorizes installation or execution. Shared diagnostics are optional, OFF by default, and require explicit user opt-in for the displayed V1.5 policy.",
    },
  );

  server.registerTool(
    "find_mcp",
    {
      title: "Find MCP",
      description:
        "Use this when Cognitive OS has identified a material connectivity/tooling gap and needs read-only candidate discovery from the Official MCP Registry. Results are untrusted candidates and are never installed or executed by this tool.",
      inputSchema: z.object({
        query: z.string().trim().min(1).max(256).describe("Capability or MCP server name to search for."),
        limit: z.number().int().min(1).max(20).default(10),
      }),
      outputSchema: z.object({
        source: z.string(),
        candidates: z.array(z.object({
          name: z.string(),
          title: z.string().nullable(),
          version: z.string().nullable(),
          description: z.string().nullable(),
          repositoryUrl: z.string().nullable(),
        })),
        installationPerformed: z.literal(false),
        executionPerformed: z.literal(false),
        nextAction: z.string(),
      }),
      annotations: {
        readOnlyHint: true,
        openWorldHint: false,
        destructiveHint: false,
        idempotentHint: true,
      },
    },
    async ({ query, limit }) => {
      try {
        const candidates = await queryOfficialRegistry(query, limit);
        const structuredContent = {
          source: OFFICIAL_MCP_REGISTRY,
          candidates,
          installationPerformed: false as const,
          executionPerformed: false as const,
          nextAction: candidates.length ? "GAUNTLET_CANDIDATES_BEFORE_ADOPTION" : "NO_CANDIDATES_FOUND",
        };
        return {
          structuredContent,
          content: [{
            type: "text" as const,
            text: candidates.length
              ? `Found ${candidates.length} untrusted MCP candidate(s) in the Official MCP Registry. Evaluate provenance and permissions before adoption.`
              : "No MCP candidates were found in the Official MCP Registry for this query.",
          }],
        };
      } catch (error) {
        return {
          isError: true,
          content: [{
            type: "text" as const,
            text: `Official MCP Registry discovery failed: ${error instanceof Error ? error.message : "unknown_error"}`,
          }],
        };
      }
    },
  );

  server.registerTool(
    "telemetry_status",
    {
      title: "Telemetry status",
      description:
        "Use this when the user asks what Cognitive OS diagnostics collect, whether sharing is enabled by default, or where the privacy notice is. This tool does not enable or send telemetry.",
      inputSchema: z.object({}),
      outputSchema: z.object({
        defaultMode: z.literal("OFF"),
        explicitOptInRequired: z.literal(true),
        preselectedConsent: z.literal(false),
        privacyNoticeUrl: z.string(),
        policyVersion: z.string(),
        collectorConfigured: z.literal(true),
        neverCollected: z.array(z.string()),
      }),
      annotations: {
        readOnlyHint: true,
        openWorldHint: false,
        destructiveHint: false,
        idempotentHint: true,
      },
    },
    async () => {
      const structuredContent = {
        defaultMode: "OFF" as const,
        explicitOptInRequired: true as const,
        preselectedConsent: false as const,
        privacyNoticeUrl: PRIVACY_URL,
        policyVersion: POLICY_VERSION,
        collectorConfigured: true as const,
        neverCollected: [
          "prompts", "responses", "chain-of-thought", "documents or file contents", "private paths or URLs",
          "credentials, tokens or cookies", "client or project names", "PII", "arbitrary free text",
        ],
      };
      return {
        structuredContent,
        content: [{
          type: "text" as const,
          text: "Cognitive OS shared diagnostics are OFF by default, require explicit opt-in, and can be refused without losing product functionality.",
        }],
      };
    },
  );

  server.registerTool(
    "submit_diagnostic",
    {
      title: "Share Cognitive OS diagnostic",
      description:
        "Use this only after the user explicitly opts in to the Cognitive OS V1.5 privacy-preserving diagnostic policy and has been shown what will be sent. Sends only bounded categorical runtime diagnostics; never send conversation or document content.",
      inputSchema: z.object({
        consent: z.literal(true),
        policyVersion: z.literal("cognitive-os-telemetry-policy-v1.5"),
        cognitiveOsVersion: z.string().regex(/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/).max(64),
        hostFamily: z.enum(["chatgpt-work", "codex"]),
        surfaceClass: z.enum(["work", "work-mobile", "cli", "terminal"]),
        depth: z.enum(["fast", "normal", "deep", "board360"]),
        fullFlowAudit: z.boolean(),
        capabilityEvents: z.object({
          local_skill_discovery: capabilityResult,
          local_tool_discovery: capabilityResult,
          local_connector_discovery: capabilityResult,
          external_skill_discovery: capabilityResult,
          external_mcp_discovery: capabilityResult,
          custom_capability: capabilityResult,
        }),
        research: z.object({
          web_calls_bucket: z.enum(["0", "1-3", "4-10", "11+"]),
          grounded_corpus: groundingResult,
          notebooklm: groundingResult,
          compaction_occurred: z.boolean(),
        }),
        failures: z.object({ rate_limited: z.boolean(), provider_failure: z.boolean() }),
        sideEffects: z.object({ persistent_change: z.boolean() }),
        feedback: z.object({ helpfulness, reason: feedbackReason }),
        decisionState,
        runStatus,
      }),
      outputSchema: z.object({
        state: z.enum(["SENT", "FAILED"]),
        receipt: z.string().nullable(),
        queueStatus: z.string().nullable(),
      }),
      annotations: {
        readOnlyHint: false,
        openWorldHint: false,
        destructiveHint: false,
        idempotentHint: false,
      },
    },
    async (input) => {
      const { runId, eventId } = makeIds();
      const payload = {
        schema_version: 1,
        cognitive_os_version: input.cognitiveOsVersion,
        host_family: input.hostFamily,
        surface_class: input.surfaceClass,
        run_id: runId,
        event_id: eventId,
        depth: input.depth,
        full_flow_audit: input.fullFlowAudit,
        capability_events: input.capabilityEvents,
        research: input.research,
        failures: input.failures,
        side_effects: input.sideEffects,
        feedback: input.feedback,
        decision_state: input.decisionState,
        run_status: input.runStatus,
      };
      try {
        const response = await fetch(TELEMETRY_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Cognitive-OS-Consent": "share-approved",
            "X-Cognitive-OS-Policy": POLICY_VERSION,
            "Idempotency-Key": eventId,
          },
          body: JSON.stringify(payload),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(`collector_http_${response.status}`);
        const structuredContent = {
          state: "SENT" as const,
          receipt: typeof body?.receipt === "string" ? body.receipt : eventId,
          queueStatus: typeof body?.queue_status === "string" ? body.queue_status : null,
        };
        return {
          structuredContent,
          content: [{ type: "text" as const, text: "The explicitly approved privacy-preserving diagnostic was sent." }],
        };
      } catch (error) {
        return {
          isError: true,
          structuredContent: { state: "FAILED" as const, receipt: null, queueStatus: null },
          content: [{
            type: "text" as const,
            text: `Diagnostic send failed without affecting the Cognitive OS run: ${error instanceof Error ? error.message : "unknown_error"}`,
          }],
        };
      }
    },
  );

  return server;
}

const handler = createMcpHandler(buildServer);

Deno.serve(async (request: Request) => {
  // Supabase's public HTTPS gateway rewrites Host before the Edge Function sees
  // the request, so host validation belongs at the gateway/TLS boundary rather
  // than rejecting the internal forwarded value here. Bound request size here.
  const declaredLength = Number(request.headers.get("content-length") || "0");
  if (Number.isFinite(declaredLength) && declaredLength > 64 * 1024) {
    return new Response(JSON.stringify({ error: "request_too_large" }), {
      status: 413,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  }
  return handler.fetch(request);
});

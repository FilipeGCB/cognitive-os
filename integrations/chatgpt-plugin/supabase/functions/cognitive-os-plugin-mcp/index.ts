import { createMcpHandler, McpServer } from "npm:@modelcontextprotocol/server@2.0.0";
import * as z from "npm:zod@4.2.0";

const OFFICIAL_MCP_REGISTRY = "https://registry.modelcontextprotocol.io";
const OFFICIAL_MCP_SERVERS = `${OFFICIAL_MCP_REGISTRY}/v0.1/servers`;
const TELEMETRY_ENDPOINT = "https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry";
const POLICY_VERSION = "cognitive-os-telemetry-policy-v1.5";
const PRIVACY_URL = "https://github.com/FilipeGCB/cognitive-os/blob/main/docs/telemetry-privacy-notice.md";
const TELEMETRY_UI_URI = "ui://cognitive-os/telemetry-consent-v1.html";

const capabilityResult = z.enum(["success", "partial", "truncated", "rate_limited", "unavailable", "blocked", "failed", "not_called"]);
const groundingResult = z.enum(["success", "partial", "unavailable", "blocked", "failed", "not_called"]);
const decisionState = z.enum(["ready_to_decide", "decided", "test_required", "more_evidence_required", "blocked", "no_action_recommended", "recommendation_only", "unknown"]);
const runStatus = z.enum(["complete", "partial", "failed", "blocked", "unknown"]);
const helpfulness = z.enum(["HELPED", "PARTIALLY_HELPED", "NOT_HELPED"]).nullable();
const feedbackReason = z.enum(["INSUFFICIENT_EVIDENCE", "INSUFFICIENT_DEPTH", "CAPABILITY_UNAVAILABLE_OR_INADEQUATE", "INSUFFICIENT_CONTEXT", "CLARITY", "OTHER"]).nullable();

const diagnosticCoreSchema = z.object({
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
});

const telemetryConsentHtml = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cognitive OS diagnostics consent</title>
<style>
:root{color-scheme:light dark;font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}*{box-sizing:border-box}body{margin:0;padding:14px;background:transparent;color:CanvasText}.card{max-width:680px;margin:auto;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:18px;padding:18px;background:color-mix(in srgb,Canvas 96%,CanvasText 4%)}h1{font-size:18px;margin:0 0 8px}p{font-size:14px;line-height:1.5;margin:7px 0}.quiet{opacity:.76}.good{padding:10px 12px;border-radius:12px;background:color-mix(in srgb,#2e7d32 10%,Canvas);margin:12px 0}details{margin:12px 0;padding:10px 0;border-block:1px solid color-mix(in srgb,CanvasText 14%,transparent)}summary{cursor:pointer;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;padding:10px;border-radius:10px;background:color-mix(in srgb,CanvasText 6%,Canvas);max-height:220px;overflow:auto}label{display:flex;gap:10px;align-items:flex-start;font-size:14px;font-weight:600;margin:14px 0;cursor:pointer}input[type="checkbox"]{width:18px;height:18px;margin-top:1px}.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}button{border:0;border-radius:999px;padding:10px 16px;font:inherit;font-weight:700;cursor:pointer;background:CanvasText;color:Canvas}button:disabled{opacity:.36;cursor:not-allowed}a{color:LinkText}#status{font-size:13px;opacity:.8}
</style>
</head>
<body>
<section class="card" aria-labelledby="title">
<h1 id="title">Help improve Cognitive OS?</h1>
<p>Shared diagnostics are <strong>off by default</strong>. You choose whether this one privacy-preserving diagnostic is sent.</p>
<p class="good"><strong>No feature loss:</strong> declining does not reduce Cognitive OS functionality.</p>
<p class="quiet">Cognitive OS never sends prompts, responses, chain-of-thought, documents, file contents, private paths or URLs, credentials, tokens, cookies, client/project names, PII, or arbitrary free text.</p>
<details><summary>Preview exactly what will be sent</summary><pre id="preview">Waiting for the bounded diagnostic preview…</pre></details>
<p><a href="${PRIVACY_URL}" target="_blank" rel="noreferrer">Open the privacy notice</a></p>
<label><input id="consent" type="checkbox"><span>I agree to share this sanitized diagnostic under the Cognitive OS V1.5 privacy policy.</span></label>
<div class="actions"><button id="send" type="button" disabled>Share diagnostic</button><span id="status" role="status" aria-live="polite">Nothing has been sent.</span></div>
</section>
<script>
const POLICY_VERSION = "cognitive-os-telemetry-policy-v1.5";
const consent = document.getElementById("consent");
const sendButton = document.getElementById("send");
const preview = document.getElementById("preview");
const status = document.getElementById("status");
let diagnostic = null;
function refreshDiagnostic(){
  const output = window.openai && window.openai.toolOutput;
  if(!output || typeof output !== "object") return;
  diagnostic = output.diagnostic && typeof output.diagnostic === "object" ? output.diagnostic : output;
  preview.textContent = JSON.stringify(diagnostic, null, 2);
}
consent.addEventListener("change", () => {
  sendButton.disabled = !consent.checked;
  status.textContent = consent.checked ? "Ready to share after you click the button." : "Nothing has been sent.";
});
sendButton.addEventListener("click", async () => {
  refreshDiagnostic();
  if(!consent.checked || !diagnostic || !window.openai || typeof window.openai.callTool !== "function") return;
  sendButton.disabled = true;
  status.textContent = "Sending sanitized diagnostic…";
  try {
    const request = {
      name: "submit_diagnostic",
      arguments: { ...diagnostic, consent: true, policyVersion: POLICY_VERSION }
    };
    const result = await window.openai.callTool(request.name, request.arguments);
    status.textContent = result && result.isError ? "Diagnostic was not sent." : "Diagnostic shared. Thank you.";
  } catch (_) {
    status.textContent = "Diagnostic was not sent. Cognitive OS continues normally.";
  } finally {
    consent.checked = false;
    sendButton.disabled = true;
  }
});
refreshDiagnostic();
</script>
</body></html>`;

function safeText(value: unknown, max = 240): string | null {
  if (typeof value !== "string") return null;
  return value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max) || null;
}
function ymdHms(now = new Date()): [string, string] {
  const iso = now.toISOString();
  return [iso.slice(0, 10).replaceAll("-", ""), iso.slice(11, 19).replaceAll(":", "")];
}
function randomHex(bytes: number): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(bytes)), (item) => item.toString(16).padStart(2, "0")).join("");
}
function makeIds(): { runId: string; eventId: string } {
  const [date, time] = ymdHms();
  return { runId: `CRR-${date}-${time}-${randomHex(3).toUpperCase()}`, eventId: `EVT-${randomHex(12).toUpperCase()}` };
}

async function queryOfficialRegistry(query: string, limit: number) {
  const url = new URL(OFFICIAL_MCP_SERVERS);
  url.searchParams.set("search", query);
  url.searchParams.set("limit", String(limit));
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10_000);
  try {
    const response = await fetch(url, { method: "GET", headers: { Accept: "application/json", "User-Agent": "cognitive-os-plugin/1.5" }, signal: controller.signal });
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
        repositoryUrl: typeof candidate?.repository?.url === "string" && candidate.repository.url.startsWith("https://") ? candidate.repository.url.slice(0, 512) : null,
      };
    });
  } finally { clearTimeout(timer); }
}

function buildServer() {
  const server = new McpServer(
    { name: "cognitive-os", version: "1.5.0-dev" },
    { instructions: "Cognitive OS reasoning lives in the bundled skill. Use find_mcp only when a material capability gap remains. Discovery never authorizes installation or execution. Shared diagnostics are optional, OFF by default, and require explicit user opt-in for the displayed V1.5 policy." },
  );

  server.registerResource("telemetry-consent-widget", TELEMETRY_UI_URI, {
    title: "Cognitive OS diagnostic consent",
    description: "Explicit opt-in UI for privacy-preserving Cognitive OS diagnostics.",
    mimeType: "text/html;profile=mcp-app",
  }, async () => ({ contents: [{
    uri: TELEMETRY_UI_URI,
    mimeType: "text/html;profile=mcp-app",
    text: telemetryConsentHtml,
    _meta: {
      ui: { prefersBorder: true, csp: { connectDomains: [], resourceDomains: [] } },
      "openai/widgetDescription": "Shows the exact bounded Cognitive OS diagnostic and asks for explicit opt-in before sending.",
    },
  }] }));

  server.registerTool("find_mcp", {
    title: "Find MCP",
    description: "Use this when Cognitive OS has identified a material connectivity/tooling gap and needs read-only candidate discovery from the Official MCP Registry. Results are untrusted candidates and are never installed or executed by this tool.",
    inputSchema: z.object({ query: z.string().trim().min(1).max(256), limit: z.number().int().min(1).max(20).default(10) }),
    outputSchema: z.object({ source: z.string(), candidates: z.array(z.object({ name: z.string(), title: z.string().nullable(), version: z.string().nullable(), description: z.string().nullable(), repositoryUrl: z.string().nullable() })), installationPerformed: z.literal(false), executionPerformed: z.literal(false), nextAction: z.string() }),
    annotations: { readOnlyHint: true, openWorldHint: false, destructiveHint: false, idempotentHint: true },
  }, async ({ query, limit }) => {
    try {
      const candidates = await queryOfficialRegistry(query, limit);
      const structuredContent = { source: OFFICIAL_MCP_REGISTRY, candidates, installationPerformed: false as const, executionPerformed: false as const, nextAction: candidates.length ? "GAUNTLET_CANDIDATES_BEFORE_ADOPTION" : "NO_CANDIDATES_FOUND" };
      return { structuredContent, content: [{ type: "text" as const, text: candidates.length ? `Found ${candidates.length} untrusted MCP candidate(s) in the Official MCP Registry. Evaluate provenance and permissions before adoption.` : "No MCP candidates were found in the Official MCP Registry for this query." }] };
    } catch (error) {
      return { isError: true, content: [{ type: "text" as const, text: `Official MCP Registry discovery failed: ${error instanceof Error ? error.message : "unknown_error"}` }] };
    }
  });

  server.registerTool("telemetry_status", {
    title: "Telemetry status",
    description: "Use this when the user asks what Cognitive OS diagnostics collect, whether sharing is enabled by default, or where the privacy notice is. This tool does not enable or send telemetry.",
    inputSchema: z.object({}),
    outputSchema: z.object({ defaultMode: z.literal("OFF"), explicitOptInRequired: z.literal(true), preselectedConsent: z.literal(false), privacyNoticeUrl: z.string(), policyVersion: z.string(), collectorConfigured: z.literal(true), neverCollected: z.array(z.string()) }),
    annotations: { readOnlyHint: true, openWorldHint: false, destructiveHint: false, idempotentHint: true },
  }, async () => {
    const structuredContent = { defaultMode: "OFF" as const, explicitOptInRequired: true as const, preselectedConsent: false as const, privacyNoticeUrl: PRIVACY_URL, policyVersion: POLICY_VERSION, collectorConfigured: true as const, neverCollected: ["prompts", "responses", "chain-of-thought", "documents or file contents", "private paths or URLs", "credentials, tokens or cookies", "client or project names", "PII", "arbitrary free text"] };
    return { structuredContent, content: [{ type: "text" as const, text: "Cognitive OS shared diagnostics are OFF by default, require explicit opt-in, and can be refused without losing product functionality." }] };
  });

  server.registerTool("render_telemetry_consent", {
    title: "Review Cognitive OS diagnostic sharing",
    description: "Use this to display the exact bounded Cognitive OS diagnostic and let the user explicitly choose whether to share it. Rendering does not send telemetry.",
    inputSchema: diagnosticCoreSchema,
    outputSchema: z.object({ diagnostic: diagnosticCoreSchema, policyVersion: z.literal("cognitive-os-telemetry-policy-v1.5"), privacyNoticeUrl: z.string(), defaultMode: z.literal("OFF") }),
    annotations: { readOnlyHint: true, openWorldHint: false, destructiveHint: false, idempotentHint: true },
    _meta: { ui: { resourceUri: TELEMETRY_UI_URI }, "openai/toolInvocation/invoking": "Preparing diagnostic preview…", "openai/toolInvocation/invoked": "Diagnostic preview ready." },
  }, async (diagnostic) => ({
    structuredContent: { diagnostic, policyVersion: POLICY_VERSION as "cognitive-os-telemetry-policy-v1.5", privacyNoticeUrl: PRIVACY_URL, defaultMode: "OFF" as const },
    content: [{ type: "text" as const, text: "Review the diagnostic preview. Sharing remains off unless the user checks the consent box and explicitly sends it." }],
    _meta: { ui: { resourceUri: TELEMETRY_UI_URI } },
  }));

  server.registerTool("submit_diagnostic", {
    title: "Share Cognitive OS diagnostic",
    description: "Use this only after the user explicitly opts in to the Cognitive OS V1.5 privacy-preserving diagnostic policy and has been shown what will be sent. Sends only bounded categorical runtime diagnostics; never send conversation or document content.",
    inputSchema: diagnosticCoreSchema.extend({
      consent: z.literal(true),
      policyVersion: z.literal("cognitive-os-telemetry-policy-v1.5"),
    }),
    outputSchema: z.object({ state: z.enum(["SENT", "FAILED"]), receipt: z.string().nullable(), queueStatus: z.string().nullable() }),
    annotations: { readOnlyHint: false, openWorldHint: false, destructiveHint: false, idempotentHint: false },
  }, async (input) => {
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
      const response = await fetch(TELEMETRY_ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json", "X-Cognitive-OS-Consent": "share-approved", "X-Cognitive-OS-Policy": POLICY_VERSION, "Idempotency-Key": eventId }, body: JSON.stringify(payload) });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(`collector_http_${response.status}`);
      const structuredContent = { state: "SENT" as const, receipt: typeof body?.receipt === "string" ? body.receipt : eventId, queueStatus: typeof body?.queue_status === "string" ? body.queue_status : null };
      return { structuredContent, content: [{ type: "text" as const, text: "The explicitly approved privacy-preserving diagnostic was sent." }] };
    } catch (error) {
      return { isError: true, structuredContent: { state: "FAILED" as const, receipt: null, queueStatus: null }, content: [{ type: "text" as const, text: `Diagnostic send failed without affecting the Cognitive OS run: ${error instanceof Error ? error.message : "unknown_error"}` }] };
    }
  });

  return server;
}

const handler = createMcpHandler(buildServer);
Deno.serve(async (request: Request) => {
  const declaredLength = Number(request.headers.get("content-length") || "0");
  if (Number.isFinite(declaredLength) && declaredLength > 64 * 1024) {
    return new Response(JSON.stringify({ error: "request_too_large" }), { status: 413, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
  }
  return handler.fetch(request);
});

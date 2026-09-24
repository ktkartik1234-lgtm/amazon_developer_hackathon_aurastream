# AuraStream: Hackathon & Engineering Invariants

This document establishes the immutable operational and technical invariants for **AuraStream** to ensure a 100% compliant, verifiable, and zero-hallucination submission to the Amazon Developer Hackathon.

---

## 1. Hackathon Deadlines & Rules Invariants

| Invariant ID | Rule Description | Ground Truth Status | Verification Proof |
| :--- | :--- | :--- | :--- |
| `INV-DEADLINE` | Submission closes Friday, October 23, 2026 at 12:00 PM PT. AWS credit request by Oct 21, 2026. | ACTIVE | Calendar anchor: 2026-09-24 local time. |
| `INV-DIR-HYGIENE` | All project files, scripts, assets, configs, logs must reside inside `amazon_developer_hackathon_aurastream/`. Root directory must remain pristine. | MANDATORY | Checked on every commit/command. |
| `INV-PRIMARY-TRACK` | Primary Track is **Fire TV**. Must be demo-ready on Fire OS / Vega OS, or verified on Fire TV/Vega simulator. | CONFIRMED | Client target: 10-foot TV UI with spatial navigation. |
| `INV-AWS-BUILDER` | Mini-Challenge: **AWS Builder**. Must integrate AWS Bedrock (Claude 3.5 Sonnet / Nova Pro) and AgentCore with documented code. | CONFIRMED | Direct SDK imports & active runtime call. |
| `INV-OPEN-SOURCE` | Mini-Challenge: **Open Source**. Repository must be public with detectable MIT/Apache license in GitHub About section OR private with collaborator invites. | CONFIRMED | `LICENSE` file (MIT) committed to repo root. |
| `INV-COLLAB-INVITES`| If private repo, must invite: `chris-trag`, `knmeiss`, `giolaq`, `anishamalde`, `mosesroth`, `emersonsklar`, `testing@devpost.com`. Invites expire in 7 days; must be sent at submission. | SUBMISSION-DAY | Automated reminder in pre-flight checklist. |
| `INV-VIDEO-DURATION`| Video demo must be strictly **< 3:00 minutes** (under 180 seconds). Public YouTube or Vimeo, in English. | STRICT CAP | Final storyboard timed to 2 min 45 sec. |
| `INV-RUNTIME-CALL`  | Code must actively import and call required tech at runtime. No README-only vaporware. | STRICT ENFORCEMENT | Verified via automated test suite. |
| `INV-FRICTION-LOG`  | Document friction logs with all 6 required fields to qualify for the **+10% judging bonus**. | BONUS BOOST | Maintained in `FRICTION_LOG.md`. |

---

## 2. Technical System Invariants

1. **MCP Specification Compliance**:
   - Model Context Protocol version must be **`2025-11-25` or later**.
   - Transport: **Streamable HTTP Transport** (`text/event-stream` / Server-Sent Events + chunked HTTP POST).
   - Tool endpoints: Strict Pydantic models for schema generation.

2. **AWS Bedrock Integration Invariant**:
   - Bedrock calls must use official SDK signatures (`boto3.client('bedrock-runtime')` or `@aws-sdk/client-bedrock-runtime`).
   - Must support multi-modal payload schemas (base64 image frame + prompt + conversation history).
   - Graceful fallback: If AWS credentials are not configured in local testing, an explicit `--mock-aws` / deterministic telemetry fallback must be logged transparently, while the live AWS SDK call path is fully implemented and tested.

3. **Fire TV 10-Foot UI Invariants**:
   - D-Pad Key Codes: `ArrowUp (38)`, `ArrowDown (40)`, `ArrowLeft (37)`, `ArrowRight (39)`, `Enter (13)`, `Back (27)`.
   - Visual Focus States: Every interactive element must have a prominent high-contrast glow/scale transform (1.05x - 1.1x) with CSS `outline` / border.
   - Screen resolution: Optimized for 1080p (1920x1080) and 4K (3840x2160) TV viewports.

---

## 3. Zero-Hallucination Verification Checklist

- [ ] Every dependency declared in `package.json` or `pyproject.toml` / `requirements.txt` is verified to exist on registry.
- [ ] Every API endpoint has an automated test in `tests/` that executes with exit code 0.
- [ ] No phantom methods or unverified arguments in AWS or MCP calls.
- [ ] All friction log entries document real developer interactions.

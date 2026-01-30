# Ideas Backlog

## Core Concepts
Here we track the brainstorming session for the next generation of Devframework architecture.

### 1. Formal Specification as Prerequisite for Autonomy
**Problem:** Vague prompts ("Make a login page") lead to AI hallucinations and non-deterministic output.
**Solution:** Autonomy is only possible if the input is a rigorous, machine-readable specification (JSON/YAML).
**Principle:** "Garbage In, Garbage Out".
**Status:** Accepted Principle.

### 2. Iterative Arch-Code Loop (Cybernetic Feedback)
**Problem:** Linear pipelines (Spec -> Code -> Done) fail because first-draft code always has bugs.
**Solution:** A feedback loop where errors (tests/linters) are fed back to the *Architect* (to fix specs) or *Team Lead* (to retry task), not just to the Coder.
**Mechanism:** The loop continues until all programmatic success criteria are met.
**Status:** Accepted Pattern.

### 3. Role: AI Product Architect (Business-to-Tech Translator)
**Problem:** Users (Business Sponsors) think in value/flows, not in technical specs. There is a gap.
**Solution:** An AI agent that acts as a "Deep Interviewer". It translates vague business desires into strict JSON specifications, offering technical recommendations where the user lacks knowledge.
**Status:** Accepted Role.

### 4. Role: AI Team Lead (Smart Orchestrator)
**Problem:** A dumb script cannot manage failures or dynamic dependencies.
**Solution:** An "Operational Manager" agent responsible for:
- Breaking down specs into atomic coding tasks.
- Assigning the right agent (Model routing).
- Coordinating handoffs between frontend/backend.
- Enforcing QA gates ("Don't show this to the Architect yet").
**Status:** Accepted Role.

### 5. Virtual AI Squad Structure (The AI Software House)
**Concept:** We are building a Virtual Organization, not just a tool.
**Roles:**
1. **AI Product Owner**: Discovery & Business Logic.
2. **AI Architect**: Technical Strategy & Specs.
3. **AI Team Lead**: Operational Management & Dispatch.
4. **AI Developers**: Coding (Frontend, Backend, DB).
5. **AI QA Engineer**: Test coverage, E2E validation, breaking things.
6. **AI Security Officer (SecOps)**: Vulnerability scanning, secret management, compliance.
7. **AI DevOps / Platform Engineer**: CI/CD, Deployment, Infrastructure, External Integrations (Stripe, DBs).

### 6. The Framework as an Operating System (OS)
**Concept:** The Framework is not just a tool, but a layered OS bridging Intent and Execution.
**Layers:**
- **Human Interface Layer**: AI Architect interacting with the User to form Intent (Master Spec).
- **Orchestration Layer**: AI Team Lead managing resources, timelines, and agent lifecycles.
- **Execution Layer**: AI Workers (Dev, QA, Ops) performing atomic tasks in isolated environments (Worktrees).
**Status:** Accepted Concept.

### 7. Systematic Adoption Strategy (Legacy/Brownfield)
**Problem:** Applying the framework to existing "chaotic" projects is risky and complex.
**Solution:** A defined "Detox" process for legacy code.
**Algorithm:**
1. **Safety First**: Full backup/snapshot before touching anything.
2. **Reverse Engineering**: Analyze existing code to reconstruct the implied Specification (Logic, DB, API).
3. **Gap Analysis**: Compare "As-Is" code with "To-Be" architectural standards (missing tests, security holes).
4. **Interactive Refinement**: A targeted interview with the user based on findings ("I found user table but no reset password flow - is this intended?").
5. **Systematic Migration**: Incremental refactoring into the framework's structure.
**Status:** Accepted Strategy.

### 8. Headless CLI First (MVP Strategy)
**Concept:** Prioritize core logic stability over UI bells and whistles. The interface should be a simple Terminal Chat.
**Rationale:** "Interface is about UX, not Function". If the core logic (Discovery -> Spec -> Code) works in CLI, adding a Web UI later is trivial.
**Architecture:** The core must be "headless" (decoupled logic) to support future UI layers (Web, Voice, IDE Plugin) without refactoring.
**Status:** Accepted Principle.

## Proven Patterns from Auto-Claude Analysis
Patterns validated by existing market solutions (Auto-Claude) that should be adopted.

### 9. Memory Layer (Persistence)
**Concept:** Agents must share a persistent knowledge base (Memory Bank + Vector DB) to avoid "amnesia" between sessions.
**Value:** Critical for maintaining context in long-running projects.

### 10. Self-Validating QA Pipeline
**Concept:** Built-in loop where agents write tests, run them, and fix code *before* involving humans.
**Value:** Reduces noise for the human reviewer. Corresponds to our "Iterative Arch-Code Loop".

### 11. Command Allowlist (Security)
**Concept:** A strict whitelist of allowed shell commands (e.g., `git`, `npm install`, `pytest`) to prevent agents from executing destructive commands (e.g., `rm -rf /`).
**Value:** Critical safety for enterprise adoption.

### 12. Visual State Dashboard (Lightweight Kanban)
**Concept:** A real-time HTML/Markdown dashboard showing the status of each agent/task (Waiting, Running, Failed, Done).
**Value:** Provides transparency into the "black box" of parallel execution.

## Proven Patterns from Vibe Kanban Analysis
UX/Management patterns for the "Team Lead" layer.

### 13. Agent Meta-Management Layer
**Concept:** A centralized interface to manage multiple underlying agents (Claude Code, Codex, Aider) as "employees".
**Value:** Allows switching agents on the fly (e.g., using a cheaper model for boilerplate and a smarter one for architecture) without changing the core workflow.

### 14. Kanban as the Primary Interface (Future)
**Concept:** Representing the workflow not as a log stream, but as a board with columns (To Do, In Progress, Review, Done).
**Value:** Matches the mental model of Product Managers and Team Leads. Provides instant status visibility.

### 15. Centralized Agent Configuration (MCP)
**Concept:** A single config file defining capabilities/tools for all agents, rather than configuring each agent individually.
**Value:** Simplifies setup and ensures consistency across the "squad".

## Proven Patterns from OpenAI Codex Analysis
Core mechanisms for the Execution Engine.

### 16. Tool Feedback Loop (The "Unrolled Loop")
**Concept:** The agent's cycle must be: Model -> Tool Call -> **Execution Result (Observation)** -> Model.
**Shift:** We must feed the stdout/stderr of commands *back* to the agent immediately, allowing it to self-correct within the same task turn.
**Value:** Enables true autonomy (Self-Healing Code) without human intervention.

### 17. Structured Prompt Hierarchy
**Concept:** Prompts must follow a rigid structure:
1. **System**: Rules & Persona.
2. **Tools**: Capabilities definition.
3. **Context**: Relevant file snippets / Memory Bank.
4. **History**: Previous actions.
5. **Input**: Current user goal.
**Value:** Reduces hallucinations by giving the model a clear "mental model" of its environment.

## Implementation Ideas
- **Spec Compiler Tool**: A script to convert Discovery MD files into Master Spec JSON.
- **Gatekeeper Module**: A validator that blocks development until the Master Spec is 100% complete and valid.

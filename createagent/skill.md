---
name: create-agent
description: "Create custom agents (.agent.md) for specialized workflows. Use when you need a subagent for a specific job, tool restrictions, or role-based behavior. Guides role definition, tool selection, and iterative refinement."
argument-hint: "What job should this agent do?"
user-invocable: true
---

# Create Custom Agent

Guide to creating `.agent.md` files for specialized subagents with tailored behaviors, tool access, and constraints.

## When to Use

- **Specialized roles**: TypeScript debugger, Python test writer, code reviewer, documentation generator
- **Tool restrictions**: Read-only research agent, terminal-only DevOps agent
- **Workflow orchestration**: Multi-step implementations with coordinated file changes
- **Domain expertise**: Agents focused on specific languages, frameworks, or patterns

## Discovery & Planning

### 1. Identify the Agent's Job
Ask: **What specialized task should this agent handle?**
- Examples: "Debug TypeScript errors", "Write Python unit tests", "Review code quality", "Orchestrate multi-file workflows"
- Be specific—don't create generic agents

### 2. Clarify Tool Access
Determine which tools the agent needs:
- **Read-only** (search, read files, web research)
- **Read + Edit** (search, read, edit files, no terminal)
- **Full access** (read, edit, search, execute/terminal)
- **Custom** (specific tools only)

### 3. Choose Location
- **Workspace** (`.github/agents/` — team-shared, project-specific)
- **User profile** (`~/.claude/agents/` or equivalent — personal, cross-workspace)

## Agent Definition Template

Create `<agent-name>.agent.md` with this structure:

```markdown
---
description: "Use when: [trigger phrases and use cases for discovery]"
name: "Display Name"
tools: [read, edit, search, execute]  # Adjust based on tool access decision
user-invocable: true
---

You are a **[role and specialty]** specializing in [domain/language/task type].

## Core Competencies
- [Key skill 1]
- [Key skill 2]
- [Key skill 3]

## Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Constraints
- DO NOT [prohibition]
- DO NOT [prohibition]
- ONLY [focus area]

## Output Format
- [What this agent returns]
```

## Key Elements

### Description
- **Must include trigger phrases** ("Use when:") so the agent can auto-discover it
- Include specific keywords (language, framework, domain)
- Keep under 250 chars
- Example: `"Use when: debugging TypeScript errors, fixing type issues, analyzing compilation failures"`

### Tools Array
Common aliases:
- `read` — read files
- `edit` — edit files
- `search` — search files/text
- `execute` — run terminal commands
- `web` — fetch URLs, web search
- `agent` — invoke subagents

### Constraints
- Prohibitions (what it should NOT do)
- Focus (the ONE thing it specializes in)
- Make constraints concrete, not vague

### Output Format
Specify exactly what the agent should return (summary, code, analysis, etc.)

## Iteration Checklist

After drafting:
- [ ] Description includes trigger phrases
- [ ] Tools array matches job requirements (not over-privileged)
- [ ] Role/specialty is clear in opening paragraph
- [ ] Constraints are specific (e.g., "DO NOT run tests without permission" not "DO NOT be reckless")
- [ ] Output format describes deliverable explicitly
- [ ] Agent name matches folder name (if in `.github/agents/`)

## Example Agents

### TypeScript Debugger
```yaml
---
description: "Use when: debugging TypeScript errors, fixing type issues, analyzing compilation failures"
name: "TypeScript Debugger"
tools: [read, edit, search, execute]
---
You are a TypeScript debugging specialist...
```

### Python Test Writer
```yaml
---
description: "Use when: writing unit tests, improving test coverage, testing Python code"
name: "Python Test Writer"
tools: [read, edit, search]
---
You are a Python unit test expert...
```

### Workflow Orchestrator
```yaml
---
description: "Use when: breaking down complex coding tasks, implementing features across multiple files, orchestrating multi-step workflows"
name: "Workflow Orchestrator"
tools: [read, edit, search, execute]
---
You are a workflow orchestrator specializing in coordinated implementations...
```

## File Structure

For workspace-scoped agents:
```
.github/
├── agents/
│   ├── workflow-orchestrator.agent.md
│   ├── typescript-debugger.agent.md
│   └── python-test-writer.agent.md
```

For user-scoped agents:
```
~/.claude/agents/
├── workflow-orchestrator.agent.md
└── custom-analyzer.agent.md
```

## Validation

Once created, test by:
1. Opening an agent picker
2. Checking if agent appears with correct description
3. Selecting it and verifying tools work as intended
4. Refining constraints based on actual behavior

## Next Steps

After creating an agent, consider:
- Creating related agents for complementary tasks
- Writing `.instructions.md` files for project conventions
- Packaging workflow skills with associated agents

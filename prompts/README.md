# AI Prompts

These prompts are designed for public reviewers who clone the repo and use
Claude Code, OpenAI Codex, Claude Desktop, or another AI tool with local file and
SQL access.

Recommended first prompt:

```text
Use prompts/audit_every_figure.md and verify the ABCDE repo from local data.
```

For epoch/block anomaly review:

```text
Use prompts/temporal_anomaly_review.md and separate hop depth from chain timing.
```

The prompts intentionally force evidence grades and uncertainty. If an answer
does not cite SQL, tables, and limits, treat it as narrative, not a receipt.

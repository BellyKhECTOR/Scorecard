# AI Governance

## Principles

1. AI is an optional layer above reliable retrieval
2. The application works fully without AI
3. AI answers cite only retrieved Mazi source material
4. Human review is required before any answer is used externally

## Confidence Levels

| Level | Criteria |
|-------|----------|
| High | Multiple recent approved sources agree |
| Medium | One strong source or several historical sources agree |
| Low | Sources are old, incomplete or conflicting |
| Insufficient evidence | No reliable Mazi source found |

## Warnings

The system warns when:
- Sources are older than configured stale threshold (default 12 months)
- Sources conflict with each other
- No approved sources were found
- Answer came from unapproved historical material only

## Feedback Capture

Reviewer actions are recorded for future improvements:
- Accepted / Edited / Rejected / Escalated / Outdated

## What We Do NOT Do

- Uncontrolled autonomous reinforcement learning
- Auto-retrain models from feedback
- Submit generated answers without human review
- Use external knowledge to make claims about Mazi

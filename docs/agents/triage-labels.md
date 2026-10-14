# Triage labels

Use these repository labels when a skill refers to the corresponding role:

| Role and label | Meaning |
| --- | --- |
| `needs-triage` | A maintainer still needs to evaluate scope or suitability. Remove when that evaluation is demonstrably complete. |
| `needs-info` | More information is required. |
| `ready-for-agent` | Specification is sufficiently clear and suitable for an agent. |
| `ready-for-human` | Implementation requires human work. |
| `wontfix` | The owner decided this work will not be actioned. |

Each issue also has one type label: `bug`, `enhancement` or `documentation`. Inspect `gh label list` before use; creating labels requires owner agreement.

Labels express triage and suitability, not the Project lifecycle. A fully specified `ready-for-agent` issue can remain Backlog while blocked. This label grants no implementation permission, supersedes no dependency and releases no execution claim. Follow `issue-tracker.md` for Status, authorization, claims and reconciliation after scope or outcome changes.

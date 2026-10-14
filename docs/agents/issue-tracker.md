# Issue tracker: GitHub

Issues and specs live in `marcus-rk/SecureLeak`. Use `gh` from the repository root, or specify `--repo marcus-rk/SecureLeak`. The planning Project is [SecureLeak - Portfolio](https://github.com/users/marcus-rk/projects/3).

## Authorization and source of truth

Only create issues for owner-agreed plan items. A generic skill's publish, claim, resolve or frontier instruction remains subject to the owner's scope and this lifecycle. Newer owner decisions supersede older issue or PR text. Record decisions with their source and date; distinguish observed facts from suggestions.

Explicit task authorization can cover routine metadata maintenance within its scope without repeated confirmation. A specified issue, priority, assignment, label or Project status alone does not authorize implementation. Obtain owner agreement for new scope; mark a PR ready only when the owner explicitly asks, and merge only with owner authorization. Public writes require authorization, which may already be present in the task. Create labels only with owner agreement.

## Before work and claiming

1. Read the full issue, comments and newer owner decisions. Inspect acceptance criteria, native dependencies, parent and sub-issues, assignees, linked PRs and their current diffs, and the Project item. Resolve ambiguous issue/PR numbers with `gh pr view` or `gh issue view`.
2. Verify readiness and authorization separately. Native dependencies are the canonical blocker representation; parent/sub-issue relationships describe decomposition, not execution order. Use a clearly marked body fallback only when native relationships are unavailable. Inspect the reason a blocker closed: cancellation or supersession does not prove its deliverable exists.
3. Check for an existing execution claim, branch or PR before starting. Record both the accountable human and the execution claim (agent/session, branch and PR when available) in authorized tracker metadata. Assignment to the same human does not prevent two AI sessions duplicating work. Resolve a conflicting claim before implementation. Assign `marcus-rk` only when active responsibility is confirmed, not across the backlog.
4. For an owner-agreed new issue, create it in English with one type label (`bug`, `enhancement` or `documentation`). Add it to Project 3 and verify membership; maintain Area, Priority and applicable triage labels. For an existing issue, verify its current membership and fields before correcting them.

## Project fields and lifecycle

Current Area options: `Authentication and access`, `Security controls and uploads`, `Documentation and presentation`, `Agent tooling`. Priority options: `High`, `Medium`, `Low`. Read live field options before editing. Priority expresses relative importance; readiness expresses specification and blocker state; authorization is the owner's permission to act.

Status records the work lifecycle, independently of issue open/closed state and CI results:

| Status | Meaning |
| --- | --- |
| Backlog | Awaiting specification, dependencies or an owner decision. |
| Ready | Specified and unblocked; still requires implementation authorization and a free execution claim. |
| In progress | Authorized work has started, including a draft PR. Explicitly agreed preparation may start while dependencies block merge rather than start; record that distinction. |
| In review | A non-draft PR after the owner explicitly asks to mark it ready. Passing CI alone does not move work here. |
| Done | Accepted and delivered. Code work normally requires merging to the default branch and closing the issue; record the accepted outcome for non-code work. Cancellation is not delivery. |

Keep fields and labels aligned with evidence. `ready-for-agent` describes specification quality and agent suitability; it never overrides blockers, status, claims or authorization (see `triage-labels.md`).

## PR links, review and reconciliation

Use closing keywords only when the PR fully resolves the issue's latest agreed scope. Use non-closing references for parents, partial work, context and prerequisites. Inspect actual `closingIssuesReferences`, not only body wording, after scope changes and before review or merge. Remove stale closing relationships through their source and verify the result. If metadata describes a narrowed scope but the diff still exceeds it, report the implementation mismatch as a blocker; metadata correction does not fix code.

Review agents check agreed scope, validation evidence and closing relationships. Keep draft PR work In progress; the owner's explicit readiness gate still applies after review.

After pause, abandonment, replacement, scope change or reopening, reconcile status, labels, execution claim and linked PRs. Release or supersede stale claims explicitly. After completion or cancellation, reassess dependents and parents against the actual outcome and remaining prerequisites; do not automatically promote, start or close them. A closed blocker can be cancelled, and a parent can still have unresolved scope.

## Operations and wayfinding

Read with `gh issue view <n> --comments`, `gh pr view <n> --comments`, and `gh pr diff <n>`. Use structured JSON for fields and closing references. Use a body file for multiline issue/PR text. Verify every authorized write with a fresh read.

For wayfinding, a map is an owner-agreed issue labelled `wayfinder:map`; tickets are native sub-issues with `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling` or `wayfinder:task` labels. Where sub-issues are unavailable, use a map task list and `Part of #<map>` on the child. Add native blockers through `gh api repos/marcus-rk/SecureLeak/issues/<child>/dependencies/blocked_by` using the blocker's numeric database ID, not its issue number or node ID.

A frontier query identifies candidates only: inspect current blockers, claims and authorization before work. Recording an answer does not itself authorize closing a ticket or its map. Close only within explicit owner authorization and after acceptance criteria are met; update the map with the outcome and evidence.

**PRs as a request surface: no.** External PRs are not automatically feature requests; authorized PR maintenance and review still follow this lifecycle.

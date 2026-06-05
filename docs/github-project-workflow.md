# GitHub Project Workflow

This workflow turns Crypto Narrative Radar into a small, realistic tech-team project. Use it to practice how product and engineering teams break work into issues, move work across a board, and close tasks with validation.

## Recommended Board

Create a GitHub Project board with these columns:

```text
Backlog -> Ready -> In Progress -> Review -> Done
```

- Backlog: useful work that is not ready to start yet.
- Ready: clearly scoped issues with acceptance criteria.
- In Progress: one active issue at a time.
- Review: code is done, but tests, docs, or final checks are pending.
- Done: merged, verified, and explainable.

## Labels

Use a small label set:

```text
feature
bug
task
docs
test
data
metrics
reporting
dashboard
good first issue
portfolio
```

## Milestones

Use milestones to group outcomes:

```text
MVP Scaffold
Taxonomy + Validation
Data Pipeline
Narrative Metrics
Reports + Dashboard
Recruiter Polish
```

## Issue Types

- Feature: a user-facing or research-facing improvement.
- Task: focused engineering, testing, data, or documentation work.
- Bug: a failing test, broken script, bad output, or dashboard/report issue.

For this project, good issues usually mention one or more canonical terms from `CONTEXT.md`, such as Narrative Metrics, Narrative Ranking, Relative Strength, Volume Confirmation, Breadth of Participation, Concentration Review, Token Contributors, or Market Snapshot.

## Definition of Ready

An issue is ready when:

- the desired outcome is clear,
- acceptance criteria are written,
- likely files are listed,
- out-of-scope work is named,
- verification commands are identified.

## Definition of Done

An issue is done when:

- the requested files are created or updated,
- the implementation stays within scope,
- relevant tests or validation checks pass,
- generated cache files are not included,
- the result is explainable in an interview,
- the closing summary includes a suggested commit message.

## Starter Backlog

Use these as the first issues:

### feat: document project management workflow

Create a short workflow guide that explains the GitHub Project board, labels, milestones, and definition of done for this repository.

Acceptance criteria:

- [ ] Board columns are documented.
- [ ] Labels and milestones are documented.
- [ ] Definition of Ready and Definition of Done are documented.
- [ ] Workflow uses cautious market intelligence language.

### test: run full validation suite and document current status

Run the project's test suite and record the current result so future issues start from a known baseline.

Acceptance criteria:

- [ ] `python -m pytest` has been run.
- [ ] Any failing tests are captured as separate bug issues.
- [ ] Current validation status is summarized in the issue.

### docs: improve recruiter-facing project walkthrough

Review the README and make sure a recruiter can understand the project flow, outputs, and positioning without reading the code first.

Acceptance criteria:

- [ ] README describes the market intelligence workflow clearly.
- [ ] README avoids trading-signal language.
- [ ] Outputs and validation commands are easy to find.

### feat: add portfolio-ready issue examples

Create or refine issues that demonstrate how the project would be planned in a professional engineering workflow.

Acceptance criteria:

- [ ] At least five scoped issues exist.
- [ ] Each issue has acceptance criteria.
- [ ] Issues map to milestones or project areas.

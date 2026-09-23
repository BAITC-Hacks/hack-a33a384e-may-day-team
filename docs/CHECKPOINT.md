# Current Checkpoint

Updated: 2026-09-23

Current milestone: Career Quest project baseline (documentation only)

## Goal

Record confirmed case facts and dataset audit. Do not implement contest functionality.

## Done

- Official case selected for research: Career Quest.
- Dataset files were read and counted. The dataset was not modified and is not in this repository.
- Requirements that appear in the dataset README and in the milestone task are written in `docs/PROJECT.md`.
- Functional code has not been created.
- Project deploy has not been done.

## Current architecture

Not approved. No application, schema, API, or recommendation pipeline exists in this repository.

## Changed files

- `README.md`
- `AGENTS.md`
- `docs/PROJECT.md`
- `docs/CHECKPOINT.md`

## How to verify

- `git status` is clean after the documentation commit.
- `git diff` for that commit contains only the documents above.
- The commit does not contain `.env`, secrets, ZIP archives, raw dataset files, or application code.

## Git

Branch: main

Last commit: docs: establish Career Quest project baseline

Pushed: YES

## Deploy

URL:

Status: not deployed

## Known issues

- A separate official case brief was not in the workspace. Latency limits, a privacy policy, forbidden mechanics beyond the dataset rule on mandatory events, and a scoring rubric are not confirmed.
- Dataset README exception for repeats after `completed` names only `EV_036`. The history file also repeats `EV_001`, `EV_002`, and `EV_003` after `completed`.

## Decisions

- Case under research: Career Quest.
- Customer named for this case: Halyk Bank. Event: HackAlem AI.
- Raw dataset and ZIP stay out of git until the user confirms they must be committed.
- Stack, auth, schema, recommendation architecture, AI provider, PWA, admin, and final UX are not approved.

## Next

Deep Research results, then user decisions, then an MVP specification. Do not start implementation before that specification.

# Current Checkpoint

Updated: 2026-09-23

Current milestone: official Career Quest brief and documentation language policy aligned in the docs

## Goal

Record the official case requirements next to the dataset audit. Do not implement contest functionality.

## Done

- Official case selected: Career Quest. Voice Router is out of scope.
- The official brief was read in full. The DOCX is not in this repository.
- Dataset files were read and counted. The dataset was not modified and is not in this repository.
- `README.md`, `docs/PROJECT.md`, and this file include the brief's must-have, optional list, latency, privacy and security, employee/HR separation, forbidden mechanics, three hidden test profiles, scoring, one-command launch, and the AI explainability requirement.
- Canonical README language is Russian. Kazakh and English README translations are deferred.
- Functional code has not been created.
- Project deploy has not been done.

## Current architecture

Not approved. No application, schema, API, or recommendation pipeline exists in this repository.

The brief requires a web application with an AI layer, employee/HR permission separation, and one-command launch. Stack, auth mechanism, database, recommendation architecture, AI model, and UX are not chosen.

## Changed files

- `README.md`
- `AGENTS.md`
- `docs/PROJECT.md`
- `docs/CHECKPOINT.md`

## How to verify

- `git show --stat HEAD` contains only the four documents above.
- That commit does not contain the DOCX, ZIP, raw dataset, `.env`, secrets, or application code.
- `git status` is clean and `main` matches `origin/main`.

## Git

Branch: main

Last commit: docs: align Career Quest baseline with official spec

Pushed: YES

## Deploy

URL:

Status: not deployed

## Known issues

- CONFLICT: the brief says the data are in English with Kazakh and Russian translations. Audited JSON/CSV records are English. Kazakh and Russian text is in the dataset README files. Not resolved.
- DATASET INTERNAL: the dataset README names only `EV_036` as a repeat after `completed`. The history file also repeats `EV_001`, `EV_002`, and `EV_003`. Not resolved.
- AMBIGUITY: the brief requires at least three explanation factors and names four. Not resolved.

## Decisions

- Case: Career Quest for АО Народный Банк Казахстана at HackAlem AI.
- Raw dataset, ZIP, and the official DOCX stay out of git.
- Stack, auth mechanism, schema, recommendation architecture, AI provider, PWA, admin, and final UX are not approved.
- Optional brief items are not selected.
- Canonical README language: Russian.
- KZ/EN translations deferred until final documentation stage.

## Next

Deep Research results, then a cross-check, then user decisions and an MVP specification. Do not start implementation before that specification.

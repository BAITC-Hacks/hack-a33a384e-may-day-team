# Career Quest

Work in progress for the Halyk Bank case at HackAlem AI.

## Problem

The case provides synthetic employee profiles, skill requirements by role and grade, a catalog of development activities, and a participation history. The task is to show an employee where they stand and which development activities should come next.

## What the official case requires

- Employee profile and career trajectory.
- An AI recommendation of 1–3 next activities, with an explanation based on multiple factors.
- A progress update after an activity is completed.
- An HR view.
- Loading of additional test profiles and history in the same format.

Jury evaluation uses unknown test profiles. A recommendation based on only one factor is expected to fail those profiles.

Mandatory activities in the dataset are assigned by HR and are not recommendation targets.

## Data

The supplied dataset is synthetic. It contains no real people or companies.

Local audit of dataset version 1.0, snapshot date `2026-10-01`:

- 60 skills and 32 role profiles (8 roles, grades Junior / Middle / Senior / Lead)
- 200 employees
- 40 events
- 2,743 participation records, from `2024-10-01` through `2026-09-30`

The raw dataset is not in this repository.

## Status

Specification and research.

This repository does not yet implement recommendations, profiles, an HR view, data loading, or a user interface. Stack, authentication, data model, recommendation approach, AI provider, and UX are not decided.

There is no deploy and no live demo.

## Documents

- `docs/PROJECT.md` — confirmed facts and open decisions
- `docs/CHECKPOINT.md` — current project state
- `AGENTS.md` — rules for coding agents

# AI Process Analyst Documentation Map

**Project:** AI Process Analyst

**Version:** 0.1.0

**Status:** Draft

---

## Purpose

This document serves as the central navigation guide for the AI Process Analyst repository.

As the project grows, documentation will be organised into specialised documents. This map helps contributors quickly locate the authoritative source for each topic.

The repository follows a **Single Source of Truth** principle, where each topic is maintained in one primary location to minimise duplication and improve long-term maintainability.

---

# Repository Documentation

## Project Overview

| Topic                | Document              |
| -------------------- | --------------------- |
| Project Introduction | ../README.md          |
| Vision               | ../VISION.md          |
| Roadmap              | ../ROADMAP.md         |
| System Architecture  | ../ARCHITECTURE.md    |
| Contributing         | ../CONTRIBUTING.md    |
| Change History       | ../CHANGELOG.md       |
| Code of Conduct      | ../CODE_OF_CONDUCT.md |
| License              | ../LICENSE            |

---

## System Design

| Topic                     | Document                        |
| ------------------------- | ------------------------------- |
| Overall Workflow          | system_workflow.md              |
| Enterprise Process Schema | ../schemas/process.schema.md    |
| Prompt Engineering        | ../prompts/extraction_prompt.md |

---

## Agent Architecture

| Topic                   | Document                             |
| ----------------------- | ------------------------------------ |
| Agent Catalogue         | ../agents/README.md                  |
| Document Analysis Agent | ../agents/document_analysis_agent.md |

Additional agents will be added as development progresses.

---

## Implementation

| Topic            | Location             |
| ---------------- | -------------------- |
| Source Code      | ../src/              |
| Test Suite       | ../tests/            |
| Examples         | ../examples/         |
| Sample Documents | ../sample_documents/ |

---

## Research

| Topic          | Location          |
| -------------- | ----------------- |
| Research Notes | ../research/      |
| Meeting Notes  | ../meeting_notes/ |
| Presentations  | ../presentations/ |
| Design Notes   | ../design/        |

---

# Recommended Reading Order

If you are new to the project, follow this order:

1. README.md
2. VISION.md
3. ROADMAP.md
4. ARCHITECTURE.md
5. system_workflow.md
6. agents/README.md
7. schemas/process.schema.md
8. prompts/extraction_prompt.md

After understanding the documentation, explore the implementation in the `src` directory.

---

# Repository Growth Strategy

The repository is designed to evolve gradually.

Future documentation may include:

- Architecture Decision Records (ADR)
- API Documentation
- Deployment Guide
- Development Guide
- User Guide
- Administration Guide
- AI Evaluation Guide
- Release Notes

These documents will be introduced only when required to support the project's growth.

---

# Guiding Principle

Every document in this repository should have a clear purpose.

Whenever possible:

- Update the authoritative document rather than duplicating information.
- Keep documentation concise and focused.
- Prefer linking to related documents instead of repeating content.
- Ensure documentation evolves alongside the implementation.

This approach keeps the repository maintainable as it grows into a production-quality open-source project.

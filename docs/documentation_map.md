# AI Process Analyst Documentation Map

**Project:** AI Process Analyst

**Version:** v0.6.0

**Status:** Active

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

## Release Documentation

Release notes capture the functionality, architectural changes, testing, and milestone achievements for each published version of the project.

| Version | Milestone                                   | Document           |
| ------- | ------------------------------------------- | ------------------ |
| v0.6.0  | Enterprise Process Core                     | releases/v0.6.0.md |
| v0.5.0  | Enterprise Process Extraction Engine        | releases/v0.5.0.md |
| v0.4.0  | Retry Framework and Resilient LLM Execution | releases/v0.4.0.md |

Future releases will be added here as the project evolves.

---

## System Design

| Topic                        | Document                        |
| ---------------------------- | ------------------------------- |
| Overall Workflow             | system_workflow.md              |
| Enterprise Process Schema    | ../schemas/process.schema.md    |
| Enterprise Canonical Schemas | ../schemas/canonical/           |
| Prompt Engineering           | ../prompts/extraction_prompt.md |

---

## Agent Architecture

| Topic                       | Document                                 |
| --------------------------- | ---------------------------------------- |
| Agent Catalogue             | ../agents/README.md                      |
| Document Analysis Agent     | ../agents/document_analysis_agent.md     |
| Diagram Generation Agent    | ../agents/diagram_generation_agent.md    |
| Process Relationship Agent  | ../agents/process_relationship_agent.md  |
| Quality Review Agent        | ../agents/quality_review_agent.md        |
| Repository Management Agent | ../agents/repository_management_agent.md |

---

## Implementation

| Topic                | Location                |
| -------------------- | ----------------------- |
| Source Code          | ../src/                 |
| Enterprise Pipeline  | ../src/pipeline/        |
| Business Ontology    | ../src/ontology/        |
| Canonical Enrichment | ../src/enrichment/      |
| Knowledge Graph      | ../src/knowledge_graph/ |
| Rule Engine          | ../src/rules/           |
| Integration Layer    | ../src/integration/     |
| Schema Validation    | ../src/validator/       |
| Test Suite           | ../tests/               |
| Examples             | ../examples/            |
| Sample Documents     | ../sample_documents/    |

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
9. CHANGELOG.md
10. docs/releases/

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
- Design Specifications
- Operations Guide

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

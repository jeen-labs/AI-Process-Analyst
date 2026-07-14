# ADR-002 — Module Responsibilities

**Status:** Accepted

**Date:** 2026-07-10

---

# Context

As the project grows, responsibilities must remain clearly separated to prevent tightly coupled components.

---

# Decision

Each Python module has one primary responsibility.

| Module                | Responsibility                       |
| --------------------- | ------------------------------------ |
| document_catalog.py   | Discover available documents         |
| document_loader.py    | Load a document                      |
| document_reader.py    | Read document contents               |
| document_parser.py    | Prepare document text                |
| prompt_builder.py     | Build LLM prompts                    |
| llm_client.py         | Communicate with the LLM             |
| response_parser.py    | Parse LLM responses                  |
| schema_validator.py   | Validate extracted data              |
| process_repository.py | Store structured process information |
| agent_orchestrator.py | Coordinate AI agents                 |

---

# Rationale

Each module should answer only one question.

For example:

DocumentLoader answers:

> How do I obtain a document?

PromptBuilder answers:

> How do I construct the prompt?

LLMClient answers:

> How do I communicate with the model?

This separation simplifies testing and future enhancements.

---

# Consequences

Future contributors should avoid placing unrelated responsibilities into existing modules.

New functionality should normally be introduced as new modules rather than expanding existing ones beyond their primary purpose.

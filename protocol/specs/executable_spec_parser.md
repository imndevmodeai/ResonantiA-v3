# Executable Spec Parser (v3.5‑GP)

Goal
- Parse spec‑annotated Markdown/JSON into validation and tests (acceptance/compliance).

Annotation Blocks
```markdown
<!-- SPEC:WORKFLOW name="basic_analysis" must_have_tasks=["perform_search","summarize_results"] -->
```

Parser Responsibilities
- Extract directives; validate repo state (workflows present, fields present).
- Emit test cases under `tests/` with clear mapping to spec sections.

Outputs
- JSON index: `outputs/spec_index.json`
- Pytests in `tests/acceptance/` & `tests/compliance/`

# Living Specification: Executable Spec Parser (Phoenix)

## Purpose
Implements `ingest_canonical_specification` and `deconstruct_code_blueprints` for the Autopoietic System Genesis Workflow. Reads the canonical protocol (e.g., `ResonantiA_Protocol_v3.1-CA.md`) and extracts Section 7 file blueprints to drive code generation.

## Inputs
- `file_path`: path to canonical protocol MD.
- Optional `section_hint`: default `7`.

## Outputs
- `blueprints.json`: array of `{ file_path, specification, language }` for each defined artifact.
- `summary`: counts, missing items, anomalies.

## Parsing Rules
- Detect code fences in Section 7 (and sub-sections): infer filename from fence header or adjacent headings.
- Map languages: ```python→.py, ```json→.json, ```ts→.ts, etc.
- Normalize relative paths under `Three_PointO_ArchE/`, `workflows/`, `knowledge_graph/`.
- Ignore narrative text; include only fenced code/spec blocks.

## Error Handling
- If Section 7 not found: return `summary.missing_section=true` and empty blueprints.
- On malformed fence: add to `summary.anomalies[]` with line range.

## Contract (pseudo)
```json
{
  "action_type":"read_file",
  "inputs":{"file_path":"ResonantiA_Protocol_v3.1-CA.md"},
  "outputs":{"content":"string"}
}
```
Then
```json
{
  "action_type":"generate_text_llm",
  "inputs":{
    "prompt":"Extract Section 7 artifacts as JSON [{file_path,specification,language}]",
    "context_data":"{{ingest_canonical_specification.output.content}}"
  }
}
```

## Validation
- Cross-check file paths against repository layout (allow creation for missing).
- Lint `language==='python'` blocks with flake8 post-generation.

## CRDSP Links
- Workflow: `autopoietic_genesis_protocol.md` (Phoenix JSON blueprint).
- Engine: `workflow_engine.md` (for for_each code generation phase).

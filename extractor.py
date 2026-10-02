"""
extractor.py

Uses the Anthropic Claude API to extract structured clinical data from a
(pseudonymized) free-text clinical note. The output is a plain JSON object
that fhir_mapper.py turns into real FHIR resources.

Requires: pip install anthropic
Set your API key as an environment variable: ANTHROPIC_API_KEY
"""

import json
import os
from dataclasses import dataclass

try:
    import anthropic
except ImportError:
    anthropic = None


EXTRACTION_SCHEMA_PROMPT = """You are a clinical data extraction assistant.
Extract structured information from the clinical note below and return
ONLY valid JSON (no prose, no markdown fences) matching this schema:

{
  "patient_pseudonym": string,
  "birth_year": string,
  "conditions": [
    {"display": string, "icd10_code": string, "clinical_status": "active"|"resolved"}
  ],
  "medications": [
    {"display": string, "dosage": string, "frequency": string}
  ],
  "observations": [
    {"display": string, "value": string, "unit": string}
  ],
  "plan_notes": [string]
}

Only extract what is explicitly stated in the note. Do not infer or
hallucinate values. If a field is not present, omit it or use an empty list.

Clinical note:
---
{note_text}
---
"""


@dataclass
class ExtractionResult:
    raw_json: dict


def extract_structured_data(note_text: str, model: str = "claude-sonnet-4-5") -> ExtractionResult:
    if anthropic is None:
        raise RuntimeError(
            "The 'anthropic' package is not installed. Run: pip install anthropic"
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set the ANTHROPIC_API_KEY environment variable first.")

    client = anthropic.Anthropic(api_key=api_key)

    prompt = EXTRACTION_SCHEMA_PROMPT.replace("{note_text}", note_text)

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    text_output = response.content[0].text.strip()

    try:
        parsed = json.loads(text_output)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON. Raw output:\n{text_output}"
        ) from e

    return ExtractionResult(raw_json=parsed)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from anonymizer import pseudonymize

    if len(sys.argv) != 2:
        print("Usage: python extractor.py <path_to_note.txt>")
        sys.exit(1)

    raw_text = Path(sys.argv[1]).read_text(encoding="utf-8")
    redacted_text, redaction_log = pseudonymize(raw_text)

    print("--- Sending pseudonymized note to LLM (no raw PII leaves the system) ---")
    result = extract_structured_data(redacted_text)

    print("\n--- Extracted structured data ---")
    print(json.dumps(result.raw_json, indent=2))

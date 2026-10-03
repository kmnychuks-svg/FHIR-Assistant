"""
extractor.py

Extracts structured clinical data from a (pseudonymized) free-text
clinical note using an LLM. The output is a plain JSON object that
fhir_mapper.py turns into real FHIR resources.

Supports two backends, chosen via the LLM_BACKEND environment variable:

  LLM_BACKEND=ollama (default) — runs fully locally via Ollama, free,
      no API key, no data leaves your machine.
      Requires: Ollama installed and running (https://ollama.com),
      with a model pulled, e.g.:  ollama pull llama3.1
      Optional env vars:
        OLLAMA_HOST  (default: http://localhost:11434)
        OLLAMA_MODEL (default: llama3.1)

  LLM_BACKEND=anthropic — uses the Claude API.
      Requires: pip install anthropic, and ANTHROPIC_API_KEY set.
      Optional env var: ANTHROPIC_MODEL (default: claude-sonnet-4-5)
"""

import json
import os
import re
from dataclasses import dataclass

try:
    import requests
except ImportError:
    requests = None

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
    backend: str = ""
    model: str = ""


def _parse_json_response(text_output: str) -> dict:
    """Parse the model's JSON output, tolerating markdown code fences and
    stray prose that some local/open models add despite instructions."""
    cleaned = text_output.strip()

    # Strip ```json ... ``` or ``` ... ``` fences if present
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Last resort: grab the widest {...} span and try that
    brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Model did not return valid JSON. Raw output:\n{text_output}"
            ) from e

    raise ValueError(f"Model did not return valid JSON. Raw output:\n{text_output}")


def _extract_with_ollama(note_text: str, model: str) -> ExtractionResult:
    if requests is None:
        raise RuntimeError("The 'requests' package is not installed. Run: pip install requests")

    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    prompt = EXTRACTION_SCHEMA_PROMPT.replace("{note_text}", note_text)

    try:
        response = requests.post(
            f"{host}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": "json",  # ask Ollama to constrain output to valid JSON
                "options": {"temperature": 0},
            },
            timeout=120,
        )
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Could not reach Ollama at {host}. Is Ollama installed and running?\n"
            f"Install: https://ollama.com\n"
            f"Start it, then pull a model: ollama pull {model}\n"
            f"Underlying error: {e}"
        ) from e

    if response.status_code == 404:
        raise RuntimeError(
            f"Ollama model '{model}' not found. Pull it first: ollama pull {model}"
        )
    response.raise_for_status()

    data = response.json()
    text_output = data.get("message", {}).get("content", "")
    parsed = _parse_json_response(text_output)

    return ExtractionResult(raw_json=parsed, backend="ollama", model=model)


def _extract_with_anthropic(note_text: str, model: str) -> ExtractionResult:
    if anthropic is None:
        raise RuntimeError("The 'anthropic' package is not installed. Run: pip install anthropic")

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

    text_output = response.content[0].text
    parsed = _parse_json_response(text_output)

    return ExtractionResult(raw_json=parsed, backend="anthropic", model=model)


def extract_structured_data(note_text: str, model: str | None = None) -> ExtractionResult:
    backend = os.environ.get("LLM_BACKEND", "ollama").lower()

    if backend == "ollama":
        return _extract_with_ollama(note_text, model or os.environ.get("OLLAMA_MODEL", "llama3.1"))
    elif backend == "anthropic":
        return _extract_with_anthropic(note_text, model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"))
    else:
        raise ValueError(f"Unknown LLM_BACKEND '{backend}'. Use 'ollama' or 'anthropic'.")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from anonymizer import pseudonymize

    if len(sys.argv) != 2:
        print("Usage: python extractor.py <path_to_note.txt>")
        sys.exit(1)

    raw_text = Path(sys.argv[1]).read_text(encoding="utf-8")
    redacted_text, redaction_log = pseudonymize(raw_text)

    backend_name = os.environ.get("LLM_BACKEND", "ollama")
    print(f"--- Sending pseudonymized note to LLM backend='{backend_name}' (no raw PII leaves the system) ---")
    try:
        result = extract_structured_data(redacted_text)
    except (RuntimeError, ValueError) as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    print(f"\n--- Extracted structured data (backend={result.backend}, model={result.model}) ---")
    print(json.dumps(result.raw_json, indent=2))

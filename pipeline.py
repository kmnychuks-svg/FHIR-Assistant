"""
pipeline.py

End-to-end demo: clinical note (.txt) -> pseudonymized -> LLM extraction
-> FHIR Bundle -> human-readable letter.

Usage:
    python src/pipeline.py data/synthetic_notes/note_001.txt
"""

import json
import sys
from pathlib import Path

from anonymizer import pseudonymize
from extractor import extract_structured_data
from fhir_mapper import build_fhir_bundle
from letter_generator import generate_letter


def run_pipeline(note_path: str, output_dir: str = "examples"):
    note_text = Path(note_path).read_text(encoding="utf-8")
    stem = Path(note_path).stem
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    print(f"[1/4] Pseudonymizing {note_path} ...")
    redacted_text, redaction_log = pseudonymize(note_text)
    (out_dir / f"{stem}_redaction_log.json").write_text(
        json.dumps(redaction_log.as_list(), indent=2), encoding="utf-8"
    )

    print("[2/4] Extracting structured data via LLM ...")
    result = extract_structured_data(redacted_text)
    (out_dir / f"{stem}_extracted.json").write_text(
        json.dumps(result.raw_json, indent=2), encoding="utf-8"
    )

    print("[3/4] Mapping to FHIR Bundle ...")
    bundle = build_fhir_bundle(result.raw_json)
    bundle_dict = json.loads(bundle.json())
    (out_dir / f"{stem}_fhir_bundle.json").write_text(
        json.dumps(bundle_dict, indent=2), encoding="utf-8"
    )

    print("[4/4] Generating discharge letter ...")
    letter = generate_letter(bundle_dict)
    (out_dir / f"{stem}_letter.txt").write_text(letter, encoding="utf-8")

    print(f"\nDone. Outputs written to {out_dir}/")
    print(letter)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipeline.py <path_to_note.txt>")
        sys.exit(1)

    run_pipeline(sys.argv[1])

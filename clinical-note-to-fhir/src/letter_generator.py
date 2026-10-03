"""
letter_generator.py

Generates a human-readable discharge/referral letter from a FHIR Bundle.
This closes the loop: unstructured note -> structured FHIR data ->
readable clinical letter, demonstrating a realistic end-to-end workflow
for clinical documentation automation.
"""

import json
from pathlib import Path


def generate_letter(bundle_dict: dict) -> str:
    patient_pseudonym = "Unknown"
    birth_date = "Unknown"
    conditions = []
    medications = []
    observations = []

    for entry in bundle_dict.get("entry", []):
        resource = entry.get("resource", {})
        rtype = resource.get("resourceType")

        if rtype == "Patient":
            identifiers = resource.get("identifier", [])
            if identifiers:
                patient_pseudonym = identifiers[0].get("value", patient_pseudonym)
            birth_date = resource.get("birthDate", birth_date)

        elif rtype == "Condition":
            text = resource.get("code", {}).get("text", "Unspecified condition")
            conditions.append(text)

        elif rtype == "MedicationStatement":
            text = resource.get("medicationCodeableConcept", {}).get("text", "Unspecified medication")
            dosage_list = resource.get("dosage", [])
            dosage_text = dosage_list[0].get("text", "") if dosage_list else ""
            medications.append(f"{text} — {dosage_text}".strip(" —"))

        elif rtype == "Observation":
            text = resource.get("code", {}).get("text", "Unspecified observation")
            value = resource.get("valueString", "")
            observations.append(f"{text}: {value}")

    letter = f"""DISCHARGE / REFERRAL LETTER (generated from structured FHIR data)
=====================================================================

Patient (pseudonym): {patient_pseudonym}
Birth year (precision reduced for privacy): {birth_date}

Diagnoses:
{chr(10).join(f"  - {c}" for c in conditions) if conditions else "  (none recorded)"}

Current medications:
{chr(10).join(f"  - {m}" for m in medications) if medications else "  (none recorded)"}

Relevant observations:
{chr(10).join(f"  - {o}" for o in observations) if observations else "  (none recorded)"}

-----------------------------------------------------------------
This letter was generated automatically from structured clinical data
(FHIR R4) for demonstration purposes. It must be reviewed and signed
off by a licensed clinician before use in any real clinical workflow.
"""
    return letter


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python letter_generator.py <path_to_fhir_bundle.json>")
        sys.exit(1)

    bundle_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(generate_letter(bundle_data))

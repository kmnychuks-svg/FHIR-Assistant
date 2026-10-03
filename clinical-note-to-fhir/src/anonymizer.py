"""
anonymizer.py

Lightweight pseudonymization step for clinical notes before they are sent
to any external LLM API. This is a DEMONSTRATION of privacy-by-design
principles (relevant to DSGVO/GDPR Art. 25) and is NOT a certified
anonymization tool. In a real deployment, use a validated clinical NLP
de-identification pipeline (e.g. based on Presidio, or a certified
German-language clinical de-identification model).

What this does:
1. Detects likely patient names (simple heuristic: "Patient: <Name>" line)
2. Detects dates of birth and visit dates
3. Replaces them with stable pseudonyms / offsets
4. Logs every redaction made, so the pipeline is auditable

This keeps the "what data left the system" question answerable, which is
a key DSGVO accountability principle (Art. 5(2)).
"""

import re
import hashlib
from dataclasses import dataclass, field


@dataclass
class RedactionLog:
    entries: list = field(default_factory=list)

    def add(self, category: str, original: str, replacement: str):
        self.entries.append(
            {"category": category, "original_hash": _hash(original), "replacement": replacement}
        )

    def as_list(self):
        return self.entries


def _hash(value: str) -> str:
    """One-way hash so the log never stores the raw PII, only a fingerprint
    useful for consistency checks / audits."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()[:12]


NAME_PATTERN = re.compile(r"(Patient:\s*)([A-ZÄÖÜ][a-zäöüß]+(?:\s[A-ZÄÖÜ][a-zäöüß]+)+)")
DOB_PATTERN = re.compile(r"(DOB:\s*)(\d{4}-\d{2}-\d{2})")
VISIT_DATE_PATTERN = re.compile(r"(Visit date:\s*)(\d{4}-\d{2}-\d{2})")


def pseudonymize(note_text: str) -> tuple[str, RedactionLog]:
    """
    Replace direct identifiers in a clinical note with pseudonyms.
    Returns (redacted_text, RedactionLog).
    """
    log = RedactionLog()
    redacted = note_text

    def replace_name(match: re.Match) -> str:
        original_name = match.group(2)
        pseudonym = f"PATIENT-{_hash(original_name).upper()[:6]}"
        log.add("name", original_name, pseudonym)
        return f"{match.group(1)}{pseudonym}"

    def replace_dob(match: re.Match) -> str:
        original_dob = match.group(2)
        # Keep only year precision — common safe-harbor style approach
        year = original_dob.split("-")[0]
        replacement = f"{year}-XX-XX"
        log.add("date_of_birth", original_dob, replacement)
        return f"{match.group(1)}{replacement}"

    def replace_visit_date(match: re.Match) -> str:
        original_date = match.group(2)
        year = original_date.split("-")[0]
        replacement = f"{year}-XX-XX"
        log.add("visit_date", original_date, replacement)
        return f"{match.group(1)}{replacement}"

    redacted = NAME_PATTERN.sub(replace_name, redacted)
    redacted = DOB_PATTERN.sub(replace_dob, redacted)
    redacted = VISIT_DATE_PATTERN.sub(replace_visit_date, redacted)

    return redacted, log


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: python anonymizer.py <path_to_note.txt>")
        sys.exit(1)

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    redacted_text, redaction_log = pseudonymize(text)

    print("--- Redacted note ---")
    print(redacted_text)
    print("\n--- Redaction log (auditable, no raw PII stored) ---")
    for entry in redaction_log.as_list():
        print(entry)

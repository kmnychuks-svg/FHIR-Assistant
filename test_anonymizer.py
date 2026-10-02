"""
tests/test_anonymizer.py

Basic tests for the pseudonymization step. Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anonymizer import pseudonymize


SAMPLE_NOTE = """Patient: John Doe
DOB: 1985-03-14
Visit date: 2026-09-28

Chief complaint: cough.
"""


def test_name_is_redacted():
    redacted, log = pseudonymize(SAMPLE_NOTE)
    assert "John Doe" not in redacted
    assert "PATIENT-" in redacted


def test_dob_precision_is_reduced():
    redacted, log = pseudonymize(SAMPLE_NOTE)
    assert "1985-03-14" not in redacted
    assert "1985-XX-XX" in redacted


def test_visit_date_precision_is_reduced():
    redacted, log = pseudonymize(SAMPLE_NOTE)
    assert "2026-09-28" not in redacted
    assert "2026-XX-XX" in redacted


def test_log_does_not_contain_raw_pii():
    redacted, log = pseudonymize(SAMPLE_NOTE)
    log_str = str(log.as_list())
    assert "John Doe" not in log_str
    assert "1985-03-14" not in log_str


def test_log_has_expected_categories():
    redacted, log = pseudonymize(SAMPLE_NOTE)
    categories = {entry["category"] for entry in log.as_list()}
    assert "name" in categories
    assert "date_of_birth" in categories
    assert "visit_date" in categories

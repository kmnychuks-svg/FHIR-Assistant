"""
tests/test_fhir_mapper.py

Regression test for a real bug found when running the pipeline against
a local Ollama model: the model sometimes returns an observation value
that already includes the unit (e.g. value="94%", unit="%"), which used
to get concatenated into a duplicated "94% %". Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fhir_mapper import _format_value_with_unit


def test_duplicated_percent_unit_is_not_repeated():
    assert _format_value_with_unit("94%", "%") == "94%"


def test_duplicated_celsius_unit_is_not_repeated():
    assert _format_value_with_unit("38.1°C", "°C") == "38.1°C"


def test_separated_value_and_unit_are_combined():
    assert _format_value_with_unit("88", "bpm") == "88 bpm"
    assert _format_value_with_unit("94", "%") == "94 %"


def test_compound_value_with_unit_is_combined():
    assert _format_value_with_unit("128/82", "mmHg") == "128/82 mmHg"


def test_missing_unit_returns_value_only():
    assert _format_value_with_unit("94", "") == "94"


def test_missing_value_returns_unit_only():
    assert _format_value_with_unit("", "%") == "%"

"""
fhir_mapper.py

Maps the structured JSON produced by extractor.py into FHIR R4B resources
(Patient, Condition, MedicationStatement, Observation), bundled as a
FHIR Bundle, using the `fhir.resources` library (pinned to 7.1.0) for
schema validation.

Requires: pip install fhir.resources==7.1.0

This demonstrates interoperability with Germany's Telematikinfrastruktur /
ePA ecosystem, which is built on HL7 FHIR.
"""

import json
import uuid
from datetime import datetime, timezone

from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.reference import Reference


def _new_id() -> str:
    return str(uuid.uuid4())


def _format_value_with_unit(value: str, unit: str) -> str:
    """Combine a value and unit without duplicating the unit when the
    model already included it in the value (e.g. value="94%" unit="%",
    or value="38.1°C" unit="°C") — common with smaller/local models that
    don't strictly separate the two fields despite the schema."""
    value = (value or "").strip()
    unit = (unit or "").strip()

    if not unit:
        return value
    if not value:
        return unit
    if value.endswith(unit):
        return value

    return f"{value} {unit}"


def build_patient_resource(data: dict) -> Patient:
    patient_id = _new_id()
    patient = Patient(
        id=patient_id,
        identifier=[{"system": "urn:example:pseudonym", "value": data.get("patient_pseudonym", "unknown")}],
        birthDate=f"{data.get('birth_year', '1900')}-01-01" if data.get("birth_year") else None,
    )
    return patient


def build_condition_resources(data: dict, patient_ref: Reference) -> list[Condition]:
    conditions = []
    for cond in data.get("conditions", []):
        coding = Coding(
            system="http://hl7.org/fhir/sid/icd-10",
            code=cond.get("icd10_code", "unknown"),
            display=cond.get("display", ""),
        )
        condition = Condition(
            id=_new_id(),
            subject=patient_ref,
            code=CodeableConcept(coding=[coding], text=cond.get("display")),
            clinicalStatus=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                    code=cond.get("clinical_status", "active"),
                )]
            ),
        )
        conditions.append(condition)
    return conditions


def build_medication_resources(data: dict, patient_ref: Reference) -> list[MedicationStatement]:
    meds = []
    for med in data.get("medications", []):
        med_statement = MedicationStatement(
            id=_new_id(),
            status="active",
            subject=patient_ref,
            medicationCodeableConcept=CodeableConcept(text=med.get("display", "")),
            dateAsserted=datetime.now(timezone.utc).isoformat(),
            dosage=[{
                "text": f"{med.get('dosage', '')} {med.get('frequency', '')}".strip()
            }],
        )
        meds.append(med_statement)
    return meds


def build_observation_resources(data: dict, patient_ref: Reference) -> list[Observation]:
    obs_list = []
    for obs in data.get("observations", []):
        observation = Observation(
            id=_new_id(),
            status="final",
            code=CodeableConcept(text=obs.get("display", "")),
            subject=patient_ref,
            valueString=_format_value_with_unit(obs.get("value", ""), obs.get("unit", "")),
        )
        obs_list.append(observation)
    return obs_list


def build_fhir_bundle(data: dict) -> Bundle:
    patient = build_patient_resource(data)
    patient_ref = Reference(reference=f"Patient/{patient.id}")

    entries = [BundleEntry(resource=patient, fullUrl=f"urn:uuid:{patient.id}")]

    for condition in build_condition_resources(data, patient_ref):
        entries.append(BundleEntry(resource=condition, fullUrl=f"urn:uuid:{condition.id}"))

    for med in build_medication_resources(data, patient_ref):
        entries.append(BundleEntry(resource=med, fullUrl=f"urn:uuid:{med.id}"))

    for obs in build_observation_resources(data, patient_ref):
        entries.append(BundleEntry(resource=obs, fullUrl=f"urn:uuid:{obs.id}"))

    bundle = Bundle(
        id=_new_id(),
        type="collection",
        timestamp=datetime.now(timezone.utc).isoformat(),
        entry=entries,
    )
    return bundle


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: python fhir_mapper.py <path_to_extracted_data.json>")
        sys.exit(1)

    extracted_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    bundle = build_fhir_bundle(extracted_data)

    print(bundle.json(indent=2))

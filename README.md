# Clinical Note → FHIR Assistant

**[English](#english) | [Deutsch](#deutsch)**

---

## English

An end-to-end demo pipeline that turns unstructured clinical notes into
structured, interoperable healthcare data using an LLM and the HL7 FHIR
standard — the data format used across Germany's Telematikinfrastruktur
(TI), electronic patient record (ePA), and e-prescription (E-Rezept)
systems.

> ⚠️ **This project uses 100% synthetic / fictional patient data.** It is a
> technical demonstration, not a certified medical device or clinical
> tool. It must not be used with real patient data without proper
> regulatory clearance (MDR/IVDR), a DPIA, and clinical validation.

### What it does

```
Free-text clinical note
        │
        ▼
 [1] Pseudonymization  ──► redaction log (auditable, DSGVO Art. 5(2) in mind)
        │
        ▼
 [2] LLM extraction (Claude API) ──► structured JSON
        │
        ▼
 [3] FHIR mapping ──► valid FHIR R4 Bundle (Patient, Condition,
        │               MedicationStatement, Observation)
        ▼
 [4] Letter generation ──► human-readable discharge/referral letter
```

### Why this project

This repo demonstrates three things relevant to AI/automation roles in
German healthcare:

1. **Interoperability** — working with HL7 FHIR, the standard underlying
   Germany's digital health infrastructure (Gematik, ePA, E-Rezept).
2. **Privacy-by-design** — a pseudonymization step runs *before* any data
   reaches an external LLM API, with an auditable log of what was
   redacted (relevant to DSGVO Art. 25 "privacy by design").
3. **Practical LLM application** — structured data extraction from
   unstructured clinical text, a real, current use case in clinical
   documentation automation.

### Quick start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here

python src/pipeline.py data/synthetic_notes/note_001.txt
```

> Note: this project pins `fhir.resources==7.1.0` and imports from its
> `R4B` module, which implements FHIR R4B (the stable, widely deployed
> release closest to what Germany's TI/ePA/E-Rezept infrastructure uses).
> Newer `fhir.resources` versions (8.x) default to FHIR R5, which uses
> different field names — pin the version if you upgrade.

Outputs are written to `examples/`:
- `note_001_redaction_log.json` — what was pseudonymized
- `note_001_extracted.json` — structured data pulled from the note
- `note_001_fhir_bundle.json` — valid FHIR R4 Bundle
- `note_001_letter.txt` — generated discharge letter

### Running tests

```bash
pytest tests/
```

### Project structure

```
clinical-note-to-fhir/
├── data/synthetic_notes/   # synthetic clinical notes (no real patient data)
├── src/
│   ├── anonymizer.py       # pseudonymization + audit log
│   ├── extractor.py        # LLM-based structured extraction
│   ├── fhir_mapper.py      # maps extracted data to FHIR R4 resources
│   ├── letter_generator.py # FHIR data -> readable letter
│   └── pipeline.py         # runs the full flow end-to-end
├── tests/                  # unit tests for the anonymizer
├── examples/               # generated output examples
└── requirements.txt
```

### Limitations & disclaimer

- The anonymizer uses simple pattern matching, not a certified
  de-identification engine. Do not rely on it for real PHI.
- The LLM extraction step can make mistakes; outputs are not validated
  against a clinician and must not be used for real clinical decisions.
- No authentication, access control, or audit trail beyond the
  redaction log is implemented — this is not production-ready software.
- This project is for portfolio/demonstration purposes.

### License

MIT — see [LICENSE](LICENSE).

---

## Deutsch

Eine Demo-Pipeline, die unstrukturierte klinische Notizen mithilfe eines
LLM und des HL7-FHIR-Standards in strukturierte, interoperable
Gesundheitsdaten umwandelt — das Datenformat, das in der deutschen
Telematikinfrastruktur (TI), der elektronischen Patientenakte (ePA) und
beim E-Rezept verwendet wird.

> ⚠️ **Dieses Projekt verwendet ausschließlich synthetische / fiktive
> Patientendaten.** Es handelt sich um eine technische Demonstration,
> kein zertifiziertes Medizinprodukt. Eine Verwendung mit echten
> Patientendaten ohne entsprechende regulatorische Freigabe (MDR/IVDR),
> Datenschutz-Folgenabschätzung (DSFA) und klinische Validierung ist
> nicht zulässig.

### Funktionsweise

```
Freitext-Notiz
        │
        ▼
 [1] Pseudonymisierung ──► Protokoll (nachvollziehbar, DSGVO Art. 5(2))
        │
        ▼
 [2] LLM-Extraktion (Claude API) ──► strukturiertes JSON
        │
        ▼
 [3] FHIR-Mapping ──► gültiges FHIR-R4-Bundle (Patient, Condition,
        │               MedicationStatement, Observation)
        ▼
 [4] Briefgenerierung ──► lesbarer Entlass-/Überweisungsbrief
```

### Warum dieses Projekt

Dieses Repository zeigt drei für KI-/Automatisierungsrollen im deutschen
Gesundheitswesen relevante Kompetenzen:

1. **Interoperabilität** — Arbeiten mit HL7 FHIR, dem Standard hinter der
   digitalen Gesundheitsinfrastruktur in Deutschland (Gematik, ePA,
   E-Rezept).
2. **Privacy by Design** — ein Pseudonymisierungsschritt läuft, *bevor*
   Daten an eine externe LLM-API gesendet werden, mit nachvollziehbarem
   Protokoll (relevant für DSGVO Art. 25).
3. **Praktische LLM-Anwendung** — strukturierte Datenextraktion aus
   unstrukturiertem klinischem Text, ein reales, aktuelles
   Anwendungsfeld in der klinischen Dokumentationsautomatisierung.

### Schnellstart

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=dein_api_key

python src/pipeline.py data/synthetic_notes/note_001.txt
```

### Einschränkungen & Haftungsausschluss

- Der Anonymisierer nutzt einfaches Pattern-Matching, kein
  zertifiziertes Verfahren zur Deidentifikation.
- Die LLM-Extraktion kann Fehler machen und ist nicht klinisch validiert.
- Keine Authentifizierung, Zugriffskontrolle oder vollständige
  Audit-Trail-Funktion — keine produktionsreife Software.
- Dieses Projekt dient Portfolio-/Demonstrationszwecken.

### Lizenz

MIT — siehe [LICENSE](LICENSE).

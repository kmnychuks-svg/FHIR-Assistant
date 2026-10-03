# Clinical Note → FHIR Assistant

[![Tests](https://github.com/kmnychuks-svg/FHIR-Assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/kmnychuks-svg/FHIR-Assistant/actions/workflows/tests.yml)

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
 [2] LLM extraction (local Ollama, or Claude API) ──► structured JSON
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
   reaches an LLM, with an auditable log of what was redacted (relevant
   to DSGVO Art. 25 "privacy by design"). Using a local model (Ollama) by
   default means pseudonymized data doesn't even leave the machine.
3. **Practical LLM application** — structured data extraction from
   unstructured clinical text, a real, current use case in clinical
   documentation automation.

### Quick start (free, fully local — default)

By default this project uses [Ollama](https://ollama.com) to run the LLM
extraction step entirely on your own machine — no API key, no cost, no
data ever leaves your computer.

```bash
# 1. Install Ollama from https://ollama.com, then pull a model:
ollama pull llama3.1

# 2. Install Python dependencies:
pip install -r requirements.txt

# 3. Run the pipeline (LLM_BACKEND defaults to "ollama"):
python src/pipeline.py data/synthetic_notes/note_001.txt
```

If Ollama isn't running, the pipeline fails with a clear message telling
you to install/start it rather than a cryptic network error.

### Alternative: Claude API backend

```bash
pip install -r requirements.txt
pip install anthropic
export LLM_BACKEND=anthropic
export ANTHROPIC_API_KEY=your_key_here

python src/pipeline.py data/synthetic_notes/note_001.txt
```

Other env vars: `OLLAMA_HOST` (default `http://localhost:11434`),
`OLLAMA_MODEL` (default `llama3.1`), `ANTHROPIC_MODEL` (default
`claude-sonnet-4-5`).

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
 [2] LLM-Extraktion (lokal via Ollama, oder Claude API) ──► strukturiertes JSON
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
   Daten an ein LLM gesendet werden, mit nachvollziehbarem Protokoll
   (relevant für DSGVO Art. 25). Da standardmäßig ein lokales Modell
   (Ollama) verwendet wird, verlassen die pseudonymisierten Daten den
   eigenen Rechner gar nicht erst.
3. **Praktische LLM-Anwendung** — strukturierte Datenextraktion aus
   unstrukturiertem klinischem Text, ein reales, aktuelles
   Anwendungsfeld in der klinischen Dokumentationsautomatisierung.

### Schnellstart (kostenlos, vollständig lokal — Standard)

Standardmäßig nutzt dieses Projekt [Ollama](https://ollama.com), um die
LLM-Extraktion vollständig auf dem eigenen Rechner laufen zu lassen —
kein API-Key, keine Kosten, keine Daten verlassen den Computer.

```bash
# 1. Ollama installieren (https://ollama.com), dann Modell laden:
ollama pull llama3.1

# 2. Python-Abhängigkeiten installieren:
pip install -r requirements.txt

# 3. Pipeline ausführen (LLM_BACKEND ist standardmäßig "ollama"):
python src/pipeline.py data/synthetic_notes/note_001.txt
```

### Alternative: Claude-API

```bash
pip install -r requirements.txt
pip install anthropic
export LLM_BACKEND=anthropic
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

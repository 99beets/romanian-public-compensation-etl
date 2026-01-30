# Known Issues and Limitations

This document tracks known limitations and edge cases in the current pipeline.

## Data source limitations
- The AMEPIP dataset is currently available as a single PDF publication (August 2025).
- No official publication cadence or versioning guarantees are known at this time.
- Column semantics are partially undocumented and inferred empirically.

## Parsing / cleaning limitations
- Some salary fields contain ambiguous formats that require heuristic interpretation.
- Text artifacts introduced by PDF extraction may still surface in edge cases.
- OCR fallback is experimental and may introduce transcription errors for scanned documents.

## Modeling limitations
- Historical tracking across multiple reporting periods is not implemented.
- Incremental or CDC-style loads are intentionally out of scope for now.
- Identity resolution relies on best-effort normalization, not authoritative identifiers.

## Infrastructure limitations
- Cloud execution assumes manual triggering; no scheduler is deployed yet.
- Secrets management is environment-variable based and not centralized.

These issues are documented intentionally and may be addressed as the project evolves.

# Product Alpha Pilot Lab UI/UX Research Note

## Decision

Restructure Pilot Lab as a three-zone evidence workspace: ingest files, triage records, and export evidence. Preserve all in-memory file handling, staged replacement, deliberate clearing, validation, aggregation, route binding, and export semantics.

## Operational risks addressed

- Primary file ingestion was visually mixed with destructive replace and clear actions.
- Workspace file state and aggregate evidence readiness appeared as one undifferentiated status.
- Validation details dominated the interface before any evidence existed.
- Raw Markdown preview occupied primary space despite being a verification aid.
- Descriptive aggregate output could be mistaken for roadmap authority without persistent framing.

## Implemented experience

- Three numbered zones: Ingest files, Triage records, and Export evidence.
- Primary add-files target separated from workspace management.
- Replace and clear controls moved into progressive disclosure while retaining explicit confirmation behavior.
- Workspace metrics ordered from selected files through valid, rejected, and duplicate records.
- Accepted records and validation errors separated into distinct triage panels.
- Aggregate readiness, revision signals, and export actions grouped in a dedicated panel.
- Markdown preview moved into optional progressive disclosure.
- Local-only, no-storage, and no-roadmap-authority boundaries remain visible.
- Responsive layout, large action targets, visible focus, reduced-motion support, and forced-colors support.

## Validation boundary

This redesign improves workflow hierarchy and action clarity. It does not claim improved evidence quality, facilitator accuracy, learning effectiveness, public-release readiness, or product-market fit. Those require separate observation and review.

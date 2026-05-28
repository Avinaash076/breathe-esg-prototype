# DECISIONS.md

This document explains the main choices I made while building the prototype. I tried to keep the scope small enough to finish in the given time, but still close to how ESG data ingestion actually works.

## 1. I used file uploads instead of direct APIs

For this prototype, I decided to ingest SAP, utility, and travel data through uploaded files.

In a real implementation, SAP or travel systems may be connected through APIs. But for a 4-day assignment, building real SAP OData, BAPI, Concur, or utility API integrations would take too much setup and would not add much value to the review workflow.

Also, in many ESG reporting projects, the first data handoff is still usually a CSV or Excel export shared by the client team. So I treated file upload as the first realistic version.

What I handled:

- SAP-style CSV export for fuel/procurement
- Utility portal CSV export for electricity
- Travel platform style CSV export for flights, hotels, and ground transport

What I did not handle:

- Real SAP authentication
- Concur/Navan OAuth
- Utility provider APIs
- PDF bill extraction

## 2. I kept raw data and normalized data separately

I did not overwrite the original uploaded values.

Each uploaded row is stored as a raw record first. Then the system creates a normalized activity row from it.

This is important because analysts and auditors may need to know:

- what value came from the source file
- what value the system calculated
- whether the row was edited later
- which upload batch created it

For example, if SAP sends `500 L` for diesel, I keep that original value and also store the normalized unit/value separately.

## 3. I chose conservative unit conversion

I only convert units when the conversion is clear.

For example:

- `KG` can be converted to tonnes
- `MT` or `T` can be treated as tonnes
- `L` can be used for fuel only when the fuel type is clear
- unknown units are not guessed

I chose this because wrong automatic conversion is worse than asking an analyst to review the row.

If the system does not understand a unit, it marks the row as needing review instead of silently producing a bad number.

## 4. I treated utility billing periods carefully

For electricity data, I used billing period start and end dates instead of only one date.

Utility bills usually do not match calendar months exactly. For example, a bill may cover:

```text
15 Jan 2026 to 14 Feb 2026
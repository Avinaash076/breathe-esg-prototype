# TRADEOFFS.md

This prototype is not trying to be a full ESG platform. I kept the scope smaller because the main goal was to show the ingestion and review flow clearly.

The important flow I focused on was:

```text
upload file -> parse rows -> normalize what is safe -> flag issues -> analyst review -> lock for audit
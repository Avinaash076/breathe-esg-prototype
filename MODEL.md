# MODEL.md

This is the data model I used for the prototype.

The main goal was to make sure every row can be traced back to the file upload that created it. I did not want the app to only show clean ESG rows and lose the messy source context, because in real ESG work the reviewer needs to know where a number came from.

The app currently handles three types of data:

- SAP fuel/procurement data
- Utility electricity data
- Corporate travel data

I kept separate tables for these three sources because their fields are different enough that forcing everything into one table made the model harder to understand.

---

## Organization

`Organization` represents the client company.

Important fields:

- `id`
- `name`
- `created_at`

Every uploaded file and every record belongs to an organization.

Right now the prototype can run with one demo organization, but I still added this model because Breathe ESG would need to support multiple client companies. This also makes it easier to filter every query by organization later.

---

## DataIngestionLog

`DataIngestionLog` represents one uploaded file.

Important fields:

- `id`
- `organization`
- `source_type`
- `filename`
- `ingestion_timestamp`
- `row_count`
- `error_count`
- `warnings_count`
- `status`
- `error_details`

I added this because the upload itself needs to be tracked, not just the rows.

For example, if an analyst sees a suspicious electricity row, they should be able to know which file it came from and when it was uploaded.

This model also helps show upload-level information on the dashboard, such as:

- total rows uploaded
- number of warnings
- number of errors
- source type
- upload status

---

## ProcurementRecord

`ProcurementRecord` stores SAP-style fuel and procurement rows.

Important fields:

- `organization`
- `ingestion_log`
- `document_number`
- `line_item`
- `plant_code`
- `vendor_code`
- `vendor_name`
- `material_code`
- `material_description`
- `quantity_original`
- `unit_original`
- `quantity_tonnes`
- `amount`
- `currency`
- `procurement_date`
- `scope`
- `emission_category`
- `review_status`
- `review_comments`
- `reviewed_by`
- `reviewed_at`
- `suspicious_flag`
- `suspicious_reason`

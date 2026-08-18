# megaplast-mp-coverage

An automated daily raw-material stock coverage report for [Megaplast](https://megaplastgt.com), a plastics manufacturer in Guatemala. It replaces a manual, monthly spreadsheet process with a daily, automated reorder signal: pulling live inventory and consumption data from the company's ERP, computing days-of-coverage per material group, and emailing a formatted report before the workday starts.

## Why

Megaplast's purchasing decisions relied on someone manually pulling inventory and consumption numbers out of the ERP once a month and eyeballing what needed reordering. That's slow, error-prone, and means stockouts (or overstock) can go unnoticed for weeks. This project turns that into a daily, unattended pipeline: same data source, but computed and delivered automatically every weekday morning.

## What it does

1. Pulls on-hand inventory and 30 days of consumption transactions from Dynamics 365 Finance & Operations via its OData API.
2. Normalizes and classifies every item into one of the business's raw-material groups (raw material vs. everything else that shares the same warehouses; then item+configuration into named material groups).
3. Computes average daily consumption and days-of-coverage for both a 7-day and a 30-day trailing window.
4. Generates a formatted Excel report — grouped, in Spanish, with conditional highlighting on low-coverage groups.
5. Emails the report via Microsoft Graph, then cleans up the local copy.
6. Runs unattended every weekday morning via GitHub Actions, emailing a failure alert instead of the report if any step breaks.

## Architecture

```
D365 OData API
   │
   ├─ inventory.py    → on-hand quantity per item+configuration
   └─ consumption.py  → consumption transactions, last 30 days
        │
        ▼
   merge.py            outer-joins inventory + 7-day/30-day consumption
        │
        ▼
   grouping.py          maps item+configuration → 1 of 17 material groups
        │               (group_mapping.py), drops permanently-excluded
        │               items, buckets unrecognized items separately
        ▼
   calculate.py          days-of-coverage per group, both time windows
        │
        ▼
   excel_output.py       formatted .xlsx report
        │
        ▼
   send_email.py          emails the report via Microsoft Graph, deletes
                           the local file on success
```

Classification (`classification.py`) normalizes item-configuration codes (case, whitespace, known synonyms) before any grouping or joining happens, so the same physical material doesn't get split across multiple rows due to inconsistent data entry upstream in the ERP.

## Tech stack

- Python — `pandas` for data wrangling, `openpyxl` for report formatting
- `msal` — Azure AD client-credentials auth against D365 and Microsoft Graph
- `requests` — OData and Graph API calls
- GitHub Actions — scheduled execution (weekdays, 7:00 AM Guatemala time)

## Project structure

```
src/
  auth.py             MSAL client-credentials token acquisition
  inventory.py        D365 on-hand inventory pull + aggregation
  consumption.py      D365 consumption transactions pull + aggregation
  classification.py   item-configuration code normalization
  group_mapping.py     item+configuration → material group lookup table
  grouping.py           applies the group mapping, aggregates per group
  merge.py             joins inventory + consumption
  calculate.py          days-of-coverage calculations
  excel_output.py       report formatting and generation
  send_email.py          sends the report via Microsoft Graph
  main.py                 orchestrates the report-generation steps
.github/workflows/
  daily-report.yml        cron schedule + manual trigger
```

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Register an app in Azure AD with client-credentials access to:
   - Your D365 F&O environment's OData API
   - Microsoft Graph, with `Mail.Send` application permission (admin-consented)
3. Create a `.env` file in the project root with:
   ```
   CLIENT_ID=
   CLIENT_SECRET=
   TENANT_ID=
   D365_RESOURCE_URL=
   D365_DATA_URL=
   D365_CONSUMPTION_URL=
   SENDER_EMAIL=
   RECIPIENT_EMAIL=
   ```
   `RECIPIENT_EMAIL` accepts a comma-separated list for multiple recipients.

## Running it

- Generate a report locally without sending it:
  ```bash
  python src/main.py
  ```
- Generate and email the report (the full pipeline):
  ```bash
  python src/send_email.py
  ```
- In production, this runs automatically via the GitHub Actions workflow (`.github/workflows/daily-report.yml`), which needs the same variables above set as repository secrets. It can also be triggered manually from the Actions tab.

## Known limitations

- Raw-material identification uses a manual item-number prefix allowlist (`RAW_MATERIAL_PREFIXES` in `merge.py`), not an official D365 category field — a deliberate simplification, not an oversight.
- The item+configuration → group mapping (`group_mapping.py`) is a static snapshot from a manual classification pass; new item/configuration combinations that appear later surface in an "unclassified" note on the report rather than being silently dropped or guessed at.
- Inventory is summed across warehouses; per-warehouse granularity is intentionally not preserved in the report.

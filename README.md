# Day 1: API Data Extraction and Transformation

Fetches the customer directory from the JSONPlaceholder Users API, flattens the nested JSON, and exports a clean CSV for Duka Connect's analytics team.

## How to run

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python extract_customers.py
```

Output: `output/customers_clean.csv`

## Data structure (Task 2)

- The API returns a **list** of 10 **dicts** (one per user).
- Plain fields: `id` (int); `name`, `username`, `email`, `phone`, `website` (str).
- **Nested fields:**
  - `address` is a dict (1 level), and inside it `geo` is another dict, so `address` goes **2 levels deep** (`address.geo.lat`, `address.geo.lng`).
  - `company` is a dict, **1 level deep** (`name`, `catchPhrase`, `bs`).
- `lat` and `lng` arrive as strings and are converted to floats.

## Error handling (Task 8)

`fetch_users` raises a `FetchError` with a clear message. `main()` prints it and exits with code 1, so there is never a raw traceback.

For each case I changed only the `fetch_users(...)` call in `main()`, ran `python extract_customers.py`, then checked the exit code with `echo $LASTEXITCODE` in PowerShell. In every case one `Error: ...` line was printed, no traceback appeared, no CSV was written, and the exit code was 1.

| Case | How I tested it | Message shown | Exit code |
|------|-----------------|---------------|-----------|
| Wrong URL | Changed the URL to `jsonplaceholder.typicodeeee.com` | Error: Could not connect to the server. Check the URL and your internet. | 1 |
| Non-200 | Used `/userss` (404) | Error: API returned status 404, expected 200. | 1 |
| Timeout | Set `timeout=0.001` | Error: Request timed out after 0.001 seconds. | 1 |
| Not JSON | Used `https://example.com` (HTML, status 200) | Error: API response was not valid JSON. | 1 |

## Assumptions

- Missing or null fields (including a missing or null `address` / `company` object) default to an empty string `""` in `extract_core_fields`, which shows up as a blank cell. A missing `id` stays `None`.
- `build_structures` uses a list comprehension (names), a plain `for` loop ((id, email) tuples) and a dict comprehension (id → city). A missing city becomes `""`.
- `flatten_user` is recursive: any nested dict becomes underscore-joined keys, at any depth, with no hard-coded field names. Values that are not dicts (including lists) are kept as they are.
- Column names are lowercased to match the spec (`company_catchPhrase` → `company_catchphrase`), and `id` is renamed to `customer_id`.
- `address_geo_lat` / `address_geo_lng` are converted to floats; a value that can't be converted becomes empty (NaN) rather than crashing.
- Columns follow the order in the expected-output spec. Any extra field the API might add later is not included in the CSV.
- `zipcode` and `phone` stay as text so values like `92998-3874` and `1-770-736-8031 x56442` are not mangled.
- The CSV is written with `index=False`, to `output/customers_clean.csv`. The `output/` folder is created if missing, and re-running overwrites the file (it never appends).
- `extract_core_fields` and `build_structures` are implemented and tested for tasks 3 and 4; the exported CSV is built from the fully flattened records.

## Project structure

```
day1-api-extraction/
├── extract_customers.py
├── output/
│   └── customers_clean.csv
├── requirements.txt
└── README.md
```
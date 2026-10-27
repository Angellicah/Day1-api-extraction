"""
Day 1 - API Data Extraction and Transformation
Squad Python Specialization - Data Engineering

Fill in every function. Keep the signatures; you may add helpers of your own.
"""
import sys
import csv
import json
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
OUTPUT_PATH = Path("output") / "customers_clean.csv"

COLUMN_ORDER = [
    "customer_id", "name", "username", "email", "phone", "website",
    "address_street", "address_suite", "address_city", "address_zipcode",
    "address_geo_lat", "address_geo_lng",
    "company_name", "company_catchphrase", "company_bs",
]

FetchError = requests.exceptions.RequestException
def fetch_users(url: str = API_URL, timeout: float = 10.0) -> list[dict]:
    """Retrieve the list of users from the API.

    Must raise or report a clear error for: connection failures, timeouts,
    non-200 status codes and bodies that are not valid JSON.
    """
    class FetchError(Exception):
        """Raised when we can't get usable data from the API."""


def fetch_users(url: str = API_URL, timeout: float = 10.0) -> list[dict]:
    """(keep your original docstring here)"""
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        raise FetchError(f"Request timed out after {timeout} seconds.")
    except requests.exceptions.ConnectionError:
        raise FetchError("Could not connect to the server. Check the URL and your internet.")
    except requests.exceptions.RequestException as e:
        raise FetchError(f"Request failed: {e}")

    if response.status_code != 200:
        raise FetchError(f"API returned status {response.status_code}, expected 200.")

    try:
        return response.json()
    except ValueError:
        raise FetchError("API response was not valid JSON.")


def describe_structure(payload) -> None:
    """Print what Python types the payload and one record are made of."""
    print("Top-level payload:", type(payload).__name__)
    record = payload[0]
    print("One record:", type(record).__name__)

    def walk(value, indent=1):
        for key, val in value.items():
            print("  " * indent + f"{key}: {type(val).__name__}")
            if isinstance(val, dict):
                walk(val, indent + 1)

    walk(record)


def extract_core_fields(users: list[dict]) -> list[dict]:
    """Return one small dict per user with id, name, email, city and company name.

    Missing values default to "" (empty string) so nothing crashes.
    """
    result = []
    for user in users:
        address = user.get("address") or {}
        company = user.get("company") or {}
        result.append({
            "id": user.get("id"),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "city": address.get("city", ""),
            "company": company.get("name", ""),
        })
    return result


def build_structures(users: list[dict]) -> tuple[list, list[tuple], dict]:
    """Return (list_of_names, list_of_(id, email)_tuples, dict_of_id_to_city).

    Uses a list comprehension, a plain for loop and a dict comprehension.
    """
    # list comprehension: one name per user
    names = [user.get("name", "") for user in users]

    # plain for loop: build (id, email) tuples
    id_email_pairs = []
    for user in users:
        id_email_pairs.append((user.get("id"), user.get("email", "")))

    # dict comprehension: id -> city (empty string if address is missing)
    id_to_city = {
        user.get("id"): (user.get("address") or {}).get("city", "")
        for user in users
    }

    return names, id_email_pairs, id_to_city


def flatten_user(user: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Flatten one nested user record into a single-level dict.

    e.g. a nested address -> geo -> lat becomes the key address_geo_lat.
    Works for any depth and any field names (nothing is hard-coded).
    """
    flat = {}
    for key, value in user.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            flat.update(flatten_user(value, new_key, sep))  # go deeper
        else:
            flat[new_key] = value
    return flat


def to_dataframe(flat_users: list[dict]) -> pd.DataFrame:
    """Build a DataFrame with the columns in the expected-output order."""
    df = pd.DataFrame(flat_users)
    df.columns = [col.lower() for col in df.columns]
    df = df.rename(columns={"id": "customer_id"})

    for col in ["address_geo_lat", "address_geo_lng"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.reindex(columns=COLUMN_ORDER)

    print("DataFrame shape:", df.shape)
    print(df.dtypes)
    return df


def export_csv(df: pd.DataFrame, path: Path = OUTPUT_PATH) -> Path:
    """Write the DataFrame to CSV (creating the folder if needed) and return the path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def main() -> None:
    # TODO: wire the steps together and print a short run summary.
    pass


def main() -> None:
        try:
            users = fetch_users()
        except FetchError as e:
            print(f"Error: {e}")
            sys.exit(1)
        print(len(users), "users fetched")
        describe_structure(users)

if __name__ == "__main__":
    main()
    
def main() -> None:
    try:
       users = fetch_users()
    except FetchError as e:
        print(f"Error: {e}")
        sys.exit(1)
    print(f"Fetched {len(users)} users")
    describe_structure(users)

    flat_users = [flatten_user(u) for u in users]
    df = to_dataframe(flat_users)

    try:
        path = export_csv(df)
    except OSError as e:
        print(f"Error: could not write the CSV file: {e}")
        sys.exit(1)

    print(f"Done: {len(df)} rows, {len(df.columns)} columns written to {path}")


if __name__ == "__main__":
    main()  
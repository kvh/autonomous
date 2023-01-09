from autonomous_components.vendor.google_sheets.actions import ExportToGoogleSheets

from autonomous import (
    post,
    on_update,
    on_new_records,
    run_sql,
    Webhook,
    File,
    Table,
    SQL,
    manual,
)
from .seed_investors import data_seed_investors
import requests
import time


pdl_api_key = Parameter("pdl_api_key")
errors = Table("errors")
contacts = Table("contacts", unique_on="email")


@manual
def pdl_enrich(payload: dict):
    TRANCHE = payload.get("tranche", 20)

    PDL_URL = "https://api.peopledatalabs.com/v5/person/search"

    HEADERS = {"Content-Type": "application/json", "X-api-key": pdl_api_key}

    def write_contacts(record: dict):
        SQL_QUERY = f"""
        SELECT * FROM person
        where job_company_website='{record['investor_domain']}'
        and work_email is not null
        and (job_title_role is null or job_title_role = 'finance')
        and (job_company_size is null or job_company_size not in ('501-1000', '1001-5000', '5001-10000', '10001+'))

        """

        # Create a parameters JSON object
        PARAMS = {"sql": SQL_QUERY, "size": 5, "pretty": True}

        # Pass the parameters object to the Person Search API
        resp = requests.get(PDL_URL, headers=HEADERS, params=PARAMS)
        print(resp.status_code)
        print(resp.headers)
        response = resp.json()

        # Check for successful response
        if response["status"] == 200:
            data = response["data"]
            print(len(data))

            for person in data:
                person.update(record)
                contacts.append(person)
        elif response["status"] == 404:
            response.update(record)
            errors.append(response)
            print("Error:", response)
        else:
            resp.raise_for_status()

    max_rank = contacts.read_sql(
        f"select max(rank) as mx from {contacts} where tranche = :tranche",
        tranche=TRANCHE,
    )[0]["mx"]

    records = data_seed_investors.read_sql(
        f"select * from {data_seed_investors} where tranche = {TRANCHE} and rank > {max_rank} order by rank"
    )
    print(f"Finding contacts for {len(records)} firms in tranche {TRANCHE}")
    assert len(records) <= 100

    # skip_domains = {r["investor_domain"] for r in already_processed.read()}

    for record in records:
        print(record)
        time.sleep(10)
        write_contacts(record)
        if not should_continue():
            request_new_run(payload)
            break


sheets_export = ExportToGoogleSheets(
    contacts,
    "https://docs.googl...",
    "new_sheet",
    Connection("google-sheets"),
    mode="replace",
)
contacts.on_update(sheets_export)

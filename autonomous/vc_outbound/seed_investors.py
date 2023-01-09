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
)
from .crunchbase import crunchbase_orgs, crunchbase_fundings


data_seed_investors = Table("data_seed_investors")


@on_update(all=[crunchbase_fundings, crunchbase_orgs])
def filter_crunchbase():
    sql = """
    create table {data_seed_investors} as

    select
    * 
    from {crunchbase_zip}
    """
    run_sql(sql, crunchbase_zip=crunchbase_zip, data_seed_investors=data_seed_investors)

    data_seed_investors.snapshot("data_seed_investors_{now}")


# Equivalent to:
# filter_crunchbase = SQL("filter_crunchbase.sql", crunchbase_zip=crunchbase_zip, data_seed_investors=data_seed_investors)


# Re-use existing component
sheets_export = ExportToGoogleSheets(
    data_seed_investors,
    "https://docs.googl...",
    "new_sheet",
    Connection("google-sheets"),
)
data_seed_investors.on_update(sheets_export)

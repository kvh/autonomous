from autonomous import post, on_update, on_new_records, run_sql, Webhook, File, Table


crunchbase_zip = File("crunchbase_zip")
crunchbase_orgs = Table("crunchbase_orgs")
crunchbase_fundings = Table("crunchbase_fundings")


@cron.once
def download_crunchbase():
    resp = requests.get("crunchbase", stream=True)
    with crunchbase_zip.open("wb") as f:
        for chunk in resp.read_chunk():
            f.write(chunk)


@crunchbase_zip.on_write
def load_crunchbase():
    with crunchbase_zip.open("rb") as f:
        for chunk in unzip(f):
            records = read_csv()
            crunchbase_orgs.append(records)
            ...

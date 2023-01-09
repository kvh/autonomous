from .base import Table, Event, manual

test = Table("test")


@manual
def trigger(event: Event):
    test.append(event.payload)


@test.on_new_records
def handle_new_slack_mentions(event: Event):
    for record in event.table.consume_new_records():
        print(record)

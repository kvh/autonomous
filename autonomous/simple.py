from base import Table, Event, manual

test = Table("test")


@manual
def trigger(event: Event):
    test.append(event.payload)


@test.on_update
def handle_new_slack_mentions(event: Event):
    print(event.table.read())

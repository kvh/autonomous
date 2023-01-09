from autonomous import post, on_new_records, webhook
from autonomous_components.vendor.openai.cognition import completion as openai_completion

slack_mentions = Table("slack_mentions")
completions = Table("completions")
slack_responses = Table("slack_responses")
slack_reactions = Table("slack_responses")


@post("/slack-mentions")
def handle_slack_mentions(event: Event) -> int:
    payload = event.request.json()
    slack_mentions.append({"timestamp": datetime.now(timezone.utc), "payload": payload})
    return 200


# Above equivalent to the following shorthand
# mentions_webhook = Webhook("/slack-mentions", slack_mentions)


@slack_mentions.on_new_records
def handle_new_slack_mentions():
    for record in slack_mentions.consume_new_records():
        completion = build_completion_from_slack_mention(record)
        completions.append(completion)
        response = make_response(record, completion)
        slack_responses.append(response)
        post_slack_message(response)


reactions_webhook = Webhook("/slack-reactions", slack_reactions)


@cron.daily
def rebuild_model():
    build_response_model(slack_responses, slack_reactions)
from autonomous import cron, Records, Table, Webhook
from autonomous_components.vendor.openai.cognition import OpenAiCompletion
from autonomous_components.vendor.slack.action import SlackPostMessage


slack_mentions = Table("slack_mentions")
prompts = Table("completions")
completions = Table("completions")
slack_responses = Table("slack_responses")
slack_reactions = Table("slack_responses")


# Handle incoming Slack mentions for our bot
@post("/slack-mentions")
def handle_slack_mentions(request: Request) -> int:
    payload = request.json()
    slack_mentions.append({"timestamp": datetime.now(timezone.utc), "payload": payload})
    return 200


# Above is equivalent to the following shorthand:
# mentions_webhook = Webhook("/slack-mentions", slack_mentions)


# React to mentions in real-time
@slack_mentions.on_new_records
def handle_new_slack_mentions(new_records: Records):
    for record in new_records:
        slack_text = record["payload"]["event"]["text"]
        prompt = f"Respond to the following message with a friendly reply: {slack_text}"
        prompts.append({"prompt": prompt})


# Use pre-built completion function
prompts.on_new_records(OpenAiCompletion(completions, api_key="xxxx", temperature=0.8))

# Use pre-built slack component to send message
completions.on_new_records(
    SlackPostMessage(oauth_token="xxxx", message_template="{completion}")
)


# Capture reactions to the posts
reactions_webhook = Webhook("/slack-reactions", slack_reactions)


# Rebuild the fine-tuned model once a day
@cron.daily
def rebuild_model():
    build_response_model(completions, slack_reactions)

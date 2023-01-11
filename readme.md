# Anton - A web framework for autonomous apps

Anton is a high-performance (1 billion automations per second) production-grade framework for 
building autonomous data-driven applications. Autonomous apps are for artificial intelligences what 
MVC apps are for humans. Anton is used to power production or operational data-driven pipelines, 
automations, and applications.

Key features out of the box:

- Reactive, data-driven processing via http, webhooks, and schedules
- Huge ecosystem of pre-built event sources and actions
- Powerful AI models, via api or self-hosted
- Oauth service to connect with over 100+ services quickly
- One-command deployment to local or cloud
- Single or Multi-tenant deployments for customer data isolation
- First-class support for data processing and ETL (SQL support, native dbt integration)
- High performance (async through-put)
- Semantic and structural data typing via Pydantic, allowing modular event handling and code re-use

Built from best-of-breed software:

- Fastapi
- Python3 async
- Support for state-of-the-art AI and LLMs
- Nomad or Kubernetes deployments
- Postgres
- Pydantic schemas

## Theory of Autonomous Web Applications

All applications have a data -> decision -> action loop. For human-driven apps, this loop 
involves pulling data from a database, displaying it succinctly in a UI, accepting input via
mouse or keyboard, and then updating the database in response to user input. This typical app 
experience is powered by a Model-View-Controller (MVC) framework that handles the steps of storing 
data, displaying it, and processing user input.

Autonomous applications have the same loop, but different constraints -- the decision is handled
in software by programmatic logic or artificial intelligence. There is no need for displaying
information succinctly in a UI or providing limited input elements. The biggest challenges
switch to being those of context -- providing the AI with all the relevant data to make an
informed decision -- a human user has a huge body of implicit knowledge about the task at
hand -- and giving them the capability to take the correct action in the right external system.

This re-orients the application framework away from storing, serving, 
and responding to user input, and to a framework that prioritizes Sensing, Cognition, and Action 
(SCA).

SCA ("skah") frameworks like Anton are built ingest and operate with disparate and large data 
sources, process them with the most powerful data tools available, run large and complex
prompt / completion pipelines, take secure action in external systems, and checkpoint
with human decision makers via common communication channels to manually clear actions.


|  | Human-driven App | Autonomous App |
| --- | --- | --- |
| Actor | Human | AI, software |
| App Inputs | Mouse, keyboard | Event and data streams |
| App Outputs | Screen | External triggers / APIs, data |
| Execution | On-demand | Reactive - “always on” |
| UI/UX | Visual design and interactions | Prompt design, data cleaning and standardization |
| Permissioning | User accounts and permissions | API keys, secrets |
| Cross App coord. and comm. | Human operator | Semantically-typed data streams |


## Quick start example

Here's an example app that responds to Slack messages with an OpenAI GPT-3 completion. Our app
looks and acts a lot like a normal web app, but instead of just responding to inbound HTTP 
requests it also responds to data events on our defined Tables.

It also uses the library of pre-built event handlers.

slack-ai-bot/main.py
```python
from anton import cron, post, Records, Table, Webhook
from anton_components.vendor.openai.cognition import OpenAiCompletion
from anton_components.vendor.slack.action import SlackPostMessage


# Define reactive Tables
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
```

Deploying our app is as simple as filling out our deployment configuration file with the desired
resources and running the deploy command.

slack-ai-bot/autonomous.json
```json
{
    "storages": [
        {
            "type": "database",
            "url": "postgresql://localhost/db",
            "name": "local-pg"
        },
        {
            "type": "file",
            "url": "s3://bucket/path",
            "name": "s3-fs"
        }
    ],
    "runtimes": [
        {
            "dockerfile": "docker/DOCKERFILE",
            "name": "custom-python"
        }
    ],
  "deployment": {
    "engine": "kubernetes",
    "target": "local"
  }
}
```

```sh
$ autonomous deploy app

Deploying to 'local' with kubernetes... DONE

Live endpoints:
  localhost:3000/slack-mentions POST
 
Live schedules:
  rebuild_model    Daily
 
Storages online:
  postgres://....
  s3://...
```

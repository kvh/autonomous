<p align="center">
<img src="static/autonomous.svg"/>
</p>

# Autonomous - A web framework for reactive data apps

Autonomous is a high-performance (10k events per second) production-grade framework for 
building reactive data-driven web applications. Autonomous apps are for artificial intelligences 
what MVC apps are for humans, with a focus on events and api actions instead of UI and user input.
Autonomous is used to power production or operational pipelines, automations, and applications such as:

- GPT-powered docs search
- Re-enforcement learning Slack bot
- Order flow processing and management
- High-volume, real-time marketing data pipelines
- Algorithmic trading bot

Key features out of the box:

- Reactive, data-driven processing via http, webhooks, and schedules
- Powerful data abstractions for high-performance, high-volume data operations across any database, data warehouse, or S3
- One-command deployment to local or cloud with kubernetes or nomad
- Huge ecosystem of pre-built event sources and actions
- Native support for AI and LLM models, via api or self-hosted
- Oauth service to connect with over 100+ services quickly
- Single or Multi-tenant deployments for data isolation
- High performance (async through-put)
- Semantic and structural data typing, allowing modular event handling and code re-use

## Quick start example

Here's an example app that responds to Slack messages with an OpenAI GPT-3 completion. Our app
looks and acts a lot like a normal web app, but instead of just responding to inbound HTTP 
requests it also responds to data events on our defined Tables.

It also uses the library of pre-built event handlers.

`main.ts`

```typescript
import { cron, post, Records, Table, Webhook } from "autonomous";
import { OpenAiCompletion } from "autonomous-components";
import { SlackPostMessage } from "autonomous-components";


// Define reactive Tables
const slack_mentions = Table("slack_mentions");
const prompts = Table("completions");
const completions = Table("completions");
const slack_responses = Table("slack_responses");
const slack_reactions = Table("slack_responses");


// Handle incoming Slack mentions for our bot
post("/slack-mentions", (request: Request) => {
  const payload = request.json();
  slack_mentions.append({ timestamp: now(), payload: payload });
  return 200;
});

// React to mentions in real-time
slack_mentions.on_new_records((newRecords: Records) => {
  newRecords.each((record) => {
    const slack_text = record["payload"]["event"]["text"];
    const prompt = `Respond to the following message with a friendly reply: {slack_text}`;
    prompts.append({ prompt: prompt });
  });
});

// Use pre-built completion function to react to new prompts
prompts.on_new_records(OpenAiCompletion(completions, "xxxx", 0.8));

// Use pre-built slack component to send completions as messages
completions.on_new_records(SlackPostMessage("xxxx", "{completion}"));

// Capture reactions to the posts for feedback modeling
const reactions_webhook = Webhook("/slack-reactions", slack_reactions);

// Rebuild the fine-tuned model once a day
cron.daily((event) => {
  build_response_model(completions, slack_reactions);
});
```

Autonomous also supports python functions:

`main.py`

```python
from autonomous import cron, post, Records, Table, Webhook
from autonomous_components.vendor.openai.cognition import OpenAiCompletion
from autonomous_components.vendor.slack.action import SlackPostMessage


slack_mentions = Table("slack_mentions")

# Handle incoming Slack mentions for our bot
@post("/slack-mentions")
def handle_slack_mentions(request: Request) -> int:
    payload = request.json()
    slack_mentions.append({"timestamp": datetime.now(timezone.utc), "payload": payload})
    return 200

#....
```

Deploying our app is as simple as filling out our deployment configuration file with the desired
resources and running the deploy command.

`autonomous.json`

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
            "name": "custom-node"
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

## Autonomous Web Applications

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

SCA ("skah") frameworks like Autonomous are built ingest and operate with disparate and large data 
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

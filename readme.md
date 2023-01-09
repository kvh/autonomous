## Anton - A framework for autonomous apps

Anton is a high-performance (1 billion automations per second) production-grade framework for 
building autonomous applications. Autonomous apps are for artificial intelligences what MVC apps 
are for humans. 

### Killer features out of the box:

- reactive, event driven processing via webhooks, crons, and/or manual triggers
- huge ecosystem of pre-built event sources and actions
- powerful AI models, via api or self-hosted
- Oauth service to connect with over 100+ services quickly
- one-command deployment to local or cloud
- first class support for complex data processing
- live request/response support

### Built from best-of-breed software:

- fast-api
- python3 async
- GPT-3, GPT-J, support for sota and open-source LLMs
- nomad or kubernetes deployments
- postgres
- pydantic schemas

## Theory

All applications have a data -> decision -> action loop. For human-driven apps, this loop 
involves pulling data from a database, displaying it succinctly in a UI, accepting input via
mouse or keyboard, and then updating the database in response to this input. This typical app 
experience is powered by a Model-View-Controller framework that handles the steps of storing data,
displaying it, and processing user input.

Autonomous applications have the same loop, but different constraints

For human-driven apps we have MVC, for autonomous apps, it is SCA, the three essential functions:

- Sensing
- Cognition
- Action

Autonomous apps are not limited to just one type of AI or automation (e.g. next-token models)
but instead embrace the complex reality of developing production grade 
automations (data munging, ETL work, heuristics, and iterative dev cycles).

|  | Human-driven App | Autonomous App |
| --- | --- | --- |
| Actor | Human | AI, software |
| App Inputs | Mouse, keyboard | Event and data streams |
| App Outputs | Screen | External triggers / APIs, data |
| Execution | On-demand | Reactive - “always on” |
| UI/UX | Visual design and interactions | Prompt design, data cleaning and standardization |
| Permissioning | User accounts and permissions | API keys, secrets |
| Cross App coord. and comm. | Human operator | Semantically-typed data streams |

Anton runs on the KNAP stack (Kubernetes, Neural networks, APIs, and Postgres).

## Quick start example

slack-ai-bot/main.py
```python
from autonomous import post, on_new_records, webhook
from autonomous_components.vendor.openai.cognition import completion as openai_completion


slack_mentions = Table("slack_mentions")
completions = Table("completions")
slack_responses = Table("slack_responses")
slack_reactions = Table("slack_responses")


# Handle incoming Slack mentions for our bot
@post("/slack-mentions")
def handle_slack_mentions(request: Request) -> int:
    payload = reqest.json()
    slack_mentions.append({"timestamp": datetime.now(timezone.utc), "payload": payload})
    return 200


# Above equivalent to the following shorthand
# mentions_webhook = Webhook("/slack-mentions", slack_mentions)


# React to mentions in real-time
@on_new_records(slack_mentions)
def handle_new_slack_mentions(new_records: Records):
    for record in new_records:
        completion = build_completion_from_slack_mention(record)
        completions.append(completion)
        response = make_response(record, completion)
        slack_responses.append(response)
        
        post_slack_message(response)

        
reactions_webhook = Webhook("/slack-reactions", slack_reactions)


@cron.daily
def rebuild_model():
		build_response_model(slack_responses, slack_reactions)
```

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
            "name": "local-fs"
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
$ patterns deploy app

Deploying to local with kubernetes... DONE

Live endpoints:
  localhost:3000/slack-mentions POST
 
Live schedules:
  None
 
Storages online:
  postgres://....
  s3://...
```


### Apps that can be built with Anton (click to clone and deploy):

- Documentation slack bot
- Cold email and drip campaign (in 20 lines)
- Facebook marketing performance
- Stock trading bot
- Crypto trading bot

---




# Patterns OS - The Operating System for Machine Intelligences

Patterns OS is a new kind of operating system oriented towards machine intelligence instead of human intelligence. It's a framework and ecosystem for AI-driven applications and automations that provides clean abstractions and APIs to the "hardware" and "I/O" of machine-oriented systems: cloud infrastructure, AI models (cognition), data streams (perception), and external APIs (action).

The purpose of an Operating System is to provide clean abstractions and APIs so that:

- application developers can build efficiently without worrying about low-level details or re-solving common problems
- applications can work across a variety of deployment / hardware configurations
- end-users (machines in this case) can operate with a consistent user experience across applications
- inter-application communication, execution, and resource contention is handled in a stardardized way

Patterns provides all these same benefits, but with important distinctions for machine intelligence:

- Machines can operate continuously (reactive, event-driven architecture)
- In Human-oriented software, the constraint is presenting just the relevant information to the user on the screen, with minimal cognitive load
- In machine-oriented software, the constraint is data quantity and quality
- Human intelligences like consistent and response UI, machine intelligences like consistent and high-quality data
- Human intelligences are good at synthesizing across tasks, this allows applications to be task-specific, with coordination done by the user
- Machine intelligences are not (yet) good at synthesizing across tasks, so applications need stronger means of coordination and communication between each other to achieve a common goal
|  | Traditional OS | Machine-oriented OS |
| --- | --- | --- |
| Actor | Human | AI |
| App Inputs | Mouse, keyboard | Event and data streams |
| App Outputs | Screen, speakers | External triggers / APIs, data |
| Execution | On-demand | Reactive, event-driven - “always on” |
| Hardware abstraction | Local devices and drivers | Cloud infra and drivers |
| UI/UX | Visual design and interactions | Data cleaning and standardization, prompt design |
| Permissioning | User accounts and permissions | API keys, secrets |

## Abstractions and APIs

The Patterns Machine-oriented Operating System provides APIs over the following:

- Standard cognition apis
    - Sequence prediction (text, multi-modal)
    - Image generation (from text, from image/s + text)
    - Video generation (from text, from image + text, from video + text)
    - Model augmentation (fine-tuning) (any of the above — from examples)
    - RL / feedback learning (state-action-reward tuples)
- Script execution (Python, SQL, Javascript)
- Orchestration / execution (event-driven reactive execution)
- Event listening service (webhooks)
- Data streams and tables
- File storage
- Cloud compute (CPU, GPU)
- Cloud database (Postgres, Snowflake)
- Cloud storage (S3, GCS)
- Secret management
- Oauth management

See the full API spec below.

## Apps

Machine-oriented apps (mapps) are applications designed around machine decisioning and actions. In Patterns, they are defined by the following files:

- manifest.json - Defines the execution graph of the app, as well as the configuration and metadata
- script files - Python and SQL scripts, corresponding to nodes in the execution graph
- readme.md - Description and documentation for the app

```json
{
    "name": "my-app",
    "scripts": [
        {
            "file": "my_script.py",
        }
    ],
    "models": [
        {
            "name": "base-llm",
            "type": "next-token-text"
        },
        {
            "name": "fine-tuned-llm",
            "type": "next-token-text",
            "fine-tunable": true
        },
        {
            "name": "base-image-gen",
            "type": "text-to-image"
        }
    ],
    "stores": [
        {
            "table": "my_table",
            "storage": {
                "engine": "postgres"
            }
        },
        {
            "file": "my_file",
        }
    ]
}
```

## Deployment

To deploy an application, define a patterns.json file:

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
            "name": "local-fs"
        }
    ],
    "runtimes": [
        {
            "dockerfile": "docker/DOCKERFILE",
            "name": "custom-python"
        }
    ],
    "secrets": [
        {}
    ]

}

```

## Quick start

```sh
pip install patterns-os
```

```sh
patterns create app quick-start && cd quick-start
```

```sh
patterns add storage postgresql://localhost
```

```sh
patterns add script --from-template=patterns/slack-receive-messages@v0
```

```sh
patterns add script my_py.py && code my_py.py
```


```python
from patterns import File, Model, Parameter, Table 

import openai


messages = Table("slack_messages")
completions = Table("completions", "w")


for event in messages.as_stream():
    text = event["event"]["text"]
    completion = openai.completion(text)
    event["gpt3_completion"] = completion
    completions.append(event)
```

Send a test event to the slack webhook:

```sh
patterns webhook test --title="Slack messages" --data={"event":{"text":"hello world"}}
```

Will trigger `my_py.py` reactively with new data:

```sh
patterns table data completions

+-------------+-----------------------------------------+
| patterns_id | event                                   |
+-------------+-----------------------------------------+
| kk3di09e3p  | {"event": ..., "gpt3_completion": ...}  |
+-------------+-----------------------------------------+

```

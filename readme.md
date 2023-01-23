<p align="center">
<img src="static/autonomous.svg"/>
</p>

# Autonomous

Autonomous is a framework for building and deploying complex applications to the cloud.
Autonomous lets you run and deploy web apps, task queues, massively parallel compute jobs,
machine learning models, GPUs, streaming data flows, and much more with a single unified framework for code and infrastructure.

Things you can build with Autonomous:

- Async product and operations workflows
- Credit risk underwriting application
- Order flow processing and management
- Algorithmic trading bot
- Content moderation pipeline
- Stability AI slack bot

Key features out of the box:

- All configuration is defined in code. No yaml or json.
- Simple primitives for deploying web functions, endpoints, cron jobs, and large scale workers to any cloud
- Reactive, data-driven processing via http, webhooks, and schedules
- High performance configuration (10k events per second)
- Utilize GPUs for AI models

Built from best-in-class open-source components:

- Node.js
- Golang
- Temporal
- Kubernetes

## Quick start example

```typescript
import { App, TableStore, FileStore, images, Sleep} from "autonomous";
import { StabilityAi} from "autonomous-images";


const app = App(defaultImage=images.nodeBullseyeSlim);


// Primitives for storage
const images = FileStore(url="s3://bucket/name")
const messages = TableStore(engine="postgresql://localhost/db")


// Handle incoming Slack mentions for our bot
app.post("/slack-mentions", (request: Request) => {
  const payload = request.json();
  app.call("handle-slack-mention", payload);
  return 200;
});


// Async worker, takes off queue, requests GPU and memory resources, runs Stable Diffusion
app.function("handle-slack-mention", {gpu: "T4", mem: "128G", image: StabilityAi.stableDiffusion}, (message) => {
    const key = keyFromSlackMessage(message)
    messages.append(message)
    const prompt = message["event"]["text"];
    const image = stabilityAiImage(prompt);
    images.add(key, image)
    response = respondInSlack(message, image)
    app.call("handle-feedback", response)
})


// Durable functions
app.function("handle-feedback", (response) => {
  // Wait 2 days, then solicit feedback
  Sleep(2 * 24 * 3600)
  if (noFeedback(response)) {
    solicitFeedbackInSlack(response)
  }
})


// Rebuild the fine-tuned model once a day
app.cron("0 0 * * *", (event) => {
  buildResponseModel();
});
```

And then run:

```sh
$ autonomous deploy app

✓ Deployed to 'local'

✓ Endpoints:
├── localhost:3000/slack-mentions POST
└── localhost:3000/slack-reactions POST
 
✓ Crons:
└── rebuild_model Daily
 
✓ Stores:
├── postgresql://localhost/db
└── s3:/bucket/name
```

### Python

Autonomous also supports python functions:

`main.py`

```python
from autonomous import App


app = App()


# Handle incoming Slack mentions for our bot
@app.post("/slack-mentions")
def handle_slack_mentions(request: Request) -> int:
    payload = request.json()
    slack_mentions.append({"timestamp": datetime.now(timezone.utc), "payload": payload})
    return 200
```


## Common deployment scenarios

### Autonomous + Next.js

Autonomous is built to compliment a JAMstack deployment, powering the backend processing and logic for data
and AI intensive applications.

### Autonomous + Next.js

Autonomous is built to compliment a JAMstack deployment, powering the backend processing and logic for data
and AI intensive applications.



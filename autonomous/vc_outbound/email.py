from .vc_outbound.pdl import contacts


email_messages = Table("email_messages")
sent_emails = Table("sent_email_messages")


msg_template = """
Hey {first_name},

Nice to meet you, I'm the co-founder and CEO of Patterns (www.patterns.app). We're a Y-Combinator backed startup with a platform for connecting new AI models like ChatGPT to real business actions. My co-founder Chris Stanley and I have spent our careers building data workflows at companies like Google, Square, and our own startups and have finally built the platform we always wanted. In the four weeks since launching in November, we've signed up hundreds of customers, hit #1 on Hacker News, and found our revenue model.

We're lucky to be backed by angels who are bought into our long-term vision (e.g. CEO Kaggle, CTO Voltron, CFO Checkr, VP Data science Square) and early pilot customers like Braze, Klaviyo, and Caraway.

We're raising a seed round in the new year and you came across our radar as potential fit. Let me know if you're interested in receiving materials in January and scheduling an intro call, or if there is someone else at {investor_name} that would be better to talk to, please do forward.

Best,
Ken

Ken Van Haren: linkedin.com/in/kenvanharen
Chris Stanley: linkedin.com/in/chris-stanley-29b20519/
"""

subject_template = "{first_name} <> Ken"


@contacts.on_new_records
def prepare_emails(new_records: Records):
    prev_recipients = {r["recipient"] for r in email_messages.read()}

    for c in stream:
        if c["tranche"] != TRANCHE:
            continue
        if c["email"] in prev_recipients:
            print(f"Skipping prev {c['email']}")
            continue
        c["first_name"] = c["first_name"].title()
        prev_recipients.add(c["email"])
        email_messages.append(
            {
                "recipient": c["email"],
                "subject": subject.format(**c),
                "body": msg.format(**c),
                "tranche": c["tranche"],
            }
        )


@manual
def send_emails_for_tranche(payload: dict):
    TRANCHE = payload["tranche"]
    prev_recipients = {r["recipient"] for r in sent_emails.read()}
    msgs = email_messages.read_sql("select * from ... where tranche=:tranche")
    for msg in msgs:
        if msg["recipient"] in prev_recipients:
            continue
        send_gmail(msg)
        msg["status"] = "sent"
        sent_emails.append(msg)

"""
server.py - connects WhatsApp to the bot.

Meta sends every incoming WhatsApp message to /webhook. We pass the text to
brain.answer() and send the reply back through the WhatsApp Cloud API.
"""

import os
import threading

import requests
from dotenv import load_dotenv
from flask import Flask, request

from brain import answer

load_dotenv()

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
GRAPH_URL = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)
seen_message_ids = set()  # stops us replying twice if Meta re-sends a message


@app.get("/")
def home():
    return "Bot server is running."


@app.get("/webhook")
def verify():
    # Meta calls this once when you save the webhook, to check it's your server.
    if (
        request.args.get("hub.mode") == "subscribe"
        and request.args.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return request.args.get("hub.challenge", ""), 200
    return "Verification failed", 403


@app.post("/webhook")
def incoming():
    data = request.get_json(silent=True) or {}
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    msg_id = msg.get("id")
                    if msg_id in seen_message_ids:
                        continue
                    seen_message_ids.add(msg_id)
                    sender = msg.get("from")
                    if msg.get("type") == "text":
                        text = msg["text"]["body"]
                        threading.Thread(
                            target=handle, args=(sender, text), daemon=True
                        ).start()
                    else:
                        threading.Thread(
                            target=send_text,
                            args=(sender, "Sorry, I can only read text messages "
                                          "right now. Please type your question."),
                            daemon=True,
                        ).start()
    except Exception as e:
        print("[webhook error]", e)
    # Reply to Meta right away so it doesn't re-send the message.
    return "OK", 200


def handle(sender, text):
    print(f"[in]  {sender}: {text}")
    reply = answer(text)
    print(f"[out] {reply}")
    send_text(sender, reply)


def send_text(to, body):
    resp = requests.post(
        GRAPH_URL,
        headers={
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        },
        timeout=20,
    )
    if resp.status_code >= 300:
        print("[send error]", resp.status_code, resp.text)


if __name__ == "__main__":
    app.run(port=5000)
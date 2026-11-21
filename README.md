# WhatsApp FAQ Assistant for Coaching Classes

A WhatsApp assistant that answers parents' questions about fees, batch timings, admissions and faculty. It replies only from a business's own information sheet, and says "please contact the office" when it doesn't know instead of guessing.

**Demo:** [add the link to your LinkedIn post or video here]

> The demo uses a fictional coaching class ("Bright Path Academy"). It runs on Meta's free test number, so only numbers added as test recipients can message it.

## What it does

- Answers questions on WhatsApp from `business_info.txt`, in English, Hindi or Hinglish
- Refuses to invent fees, discounts or promises, and ignores attempts to override its rules
- Remembers the last few messages of each chat, so follow-ups like "and for class 12?" work
- Replies politely to non-text messages (voice notes, photos) by asking for a typed question
- Keeps the business details in one text file, so a new business means editing one file

## How it works

```
Parent's WhatsApp -> Meta WhatsApp Cloud API -> webhook (Flask server)
-> brain.py -> Gemini API (with the business info + rules) -> reply back through WhatsApp
```

- `server.py` receives messages from Meta's webhook, ignores duplicates, keeps per-customer chat history, and sends replies.
- `brain.py` builds the prompt from `business_info.txt` and calls the Gemini API. If the API fails, it returns a safe "contact the office" message.
- `test.py` checks which Gemini models your API key can use.

## Tech stack

Python, Flask, Google Gemini API, WhatsApp Cloud API (Meta), ngrok, python-dotenv, Git

## Run it yourself

1. Clone the repo and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac / Linux
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your own values (Gemini API key, WhatsApp access token, Phone Number ID, and a verify token you choose).
3. Edit `business_info.txt` with a business's fees, timings and policies.
4. Test the assistant in the terminal: `python brain.py`
5. Start the server: `python server.py`
6. Expose it with ngrok: `ngrok http 5000`
7. In your Meta app (WhatsApp, Webhooks), set the callback URL to `https://<your-ngrok-address>/webhook`, enter your verify token, and subscribe to **messages**.
8. Add your phone as a test recipient and message the test number.

If you get a "model not found" or "high demand" error, change `MODEL` in `brain.py` to another model your key supports (`python test.py` lists them).

## Limitations

- Runs locally with ngrok; it is not deployed to a server yet
- Uses Meta's test number, which has a recipient limit and a temporary access token
- Chat history is kept in memory and resets when the server restarts
- Text messages only
- Fictional sample data; accuracy on a real business depends on the information provided

## Next steps

- Host it on an always-on server with a permanent access token
- Collect parent name and class of interest and send leads to the owner
- Store chat history in a database

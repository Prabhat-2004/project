
import base64
import re
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Gmail categories and their Gmail search queries.
FILTERS = {
    "inbox": ("Inbox", "in:inbox"),
    "unread": ("Unread", "in:inbox is:unread"),
    "starred": ("Starred", "in:inbox is:starred"),
    "important": ("Important", "in:inbox is:important"),
    "sent": ("Sent", "in:sent"),
    "drafts": ("Drafts", "in:drafts"),
    "spam": ("Spam", "in:spam"),
    "trash": ("Trash", "in:trash"),
    "attachments": ("Attachments", "in:inbox has:attachment"),
}


def get_gmail_service():
    credentials_file = BASE_DIR / "credentials.json"

    if not credentials_file.exists():
        credentials_file = BASE_DIR / "credentials.json.json"

    if not credentials_file.exists():
        raise FileNotFoundError(
            "Place credentials.json or credentials.json.json beside gmail.py."
        )

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file), SCOPES
        )
        creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds)


def get_header(headers, name):
    for item in headers:
        if item.get("name", "").lower() == name.lower():
            return item.get("value", "")
    return ""


def get_body(payload):
    parts = []

    def walk(part):
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data")

        if mime == "text/plain" and data:
            try:
                data += "=" * (-len(data) % 4)
                decoded = base64.urlsafe_b64decode(data)
                parts.append(
                    decoded.decode("utf-8", errors="replace")
                )
            except Exception:
                pass

        for child in part.get("parts", []):
            walk(child)

    walk(payload)
    return "\n".join(parts).strip()


def fetch_emails(query="in:inbox", limit=20):
    service = get_gmail_service()

    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=limit
    ).execute()

    emails = []

    for index, message in enumerate(
        result.get("messages", []), start=1
    ):
        item = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = item.get("payload", {})
        headers = payload.get("headers", [])
        labels = item.get("labelIds", [])

        emails.append({
            "number": index,
            "id": item["id"],
            "sender": get_header(headers, "From"),
            "subject": get_header(headers, "Subject") or "(No subject)",
            "date": get_header(headers, "Date"),
            "snippet": item.get("snippet", ""),
            "body": get_body(payload),
            "unread": "UNREAD" in labels,
            "starred": "STARRED" in labels,
            "important": "IMPORTANT" in labels,
            "attachments": "ATTACHMENT" in labels,
        })

    return emails, result.get("resultSizeEstimate", len(emails))


def get_stats():
    service = get_gmail_service()
    stats = {}

    for key, (label, query) in FILTERS.items():
        result = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=1
        ).execute()

        stats[key] = result.get("resultSizeEstimate", 0)

    return stats


def process_command(command):
    command = command.lower().strip()
    command = re.sub(r"[.,!?]+$", "", command)

    if command in ("help", "commands", "what can you do"):
        return {
            "reply": (
                "Try read my emails, unread emails, starred emails, "
                "important emails, count emails, sent emails, "
                "drafts, spam, trash, attachments, search subject meeting, "
                "search from Google, read email one, or tell me a joke."
            )
        }

    if "joke" in command or "chutkula" in command:
        return {
            "reply": (
                "Why did the computer go to the doctor? "
                "Because it had a virus!"
            )
        }

    if "count" in command and "unread" in command:
        return {
            "reply": f"There are {get_stats()['unread']} unread inbox emails."
        }

    if "count" in command or "how many emails" in command:
        stats = get_stats()
        return {
            "reply": (
                f"Inbox: {stats['inbox']}. "
                f"Unread: {stats['unread']}. "
                f"Starred: {stats['starred']}. "
                f"Important: {stats['important']}."
            ),
            "stats": stats
        }

    command_filters = {
        "unread": ["unread emails", "show unread", "unread mail"],
        "starred": ["starred emails", "starred mail", "show starred"],
        "important": ["important emails", "important mail", "show important"],
        "sent": ["sent emails", "sent mail", "show sent"],
        "drafts": ["show drafts", "my drafts", "draft emails"],
        "spam": ["show spam", "spam emails", "spam mail"],
        "trash": ["show trash", "trash emails", "deleted emails"],
        "attachments": [
            "emails with attachments", "show attachments",
            "attachment emails"
        ],
        "inbox": [
            "read my emails", "read emails", "latest mail",
            "latest emails", "show my inbox", "show inbox",
            "check my mail", "check my emails", "open gmail"
        ],
    }

    for key, phrases in command_filters.items():
        if any(phrase in command for phrase in phrases):
            label, query = FILTERS[key]
            emails, total = fetch_emails(query, 20)
            return {
                "reply": f"Showing {label}: {total} emails found.",
                "emails": emails,
                "total": total,
                "filter": key
            }

    if command.startswith("search subject "):
        subject = command[len("search subject "):].strip()
        emails, total = fetch_emails(f"in:anywhere subject:({subject})", 20)
        return {
            "reply": f"Found {total} emails for subject {subject}.",
            "emails": emails,
            "total": total
        }

    if command.startswith("search from "):
        sender = command[len("search from "):].strip()
        emails, total = fetch_emails(f"in:anywhere from:({sender})", 20)
        return {
            "reply": f"Found {total} emails from {sender}.",
            "emails": emails,
            "total": total
        }

    if "read email" in command or "open email" in command:
        words = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10
        }

        number = next(
            (value for word, value in words.items()
             if re.search(rf"\b{word}\b", command)),
            None
        )

        match = re.search(r"\b\d+\b", command)
        if match:
            number = int(match.group())

        if number is None:
            return {"reply": "Say read email one or read email two."}

        emails, _ = fetch_emails("in:inbox", 20)

        if 1 <= number <= len(emails):
            return {
                "reply": f"Opening email {number}.",
                "selected": emails[number - 1]
            }

        return {"reply": "That email number is not available."}

    if command in ("stop", "stop reading", "quiet"):
        return {"reply": "Press Stop audio to stop speaking."}

    return {
        "reply": f"I heard: {command}. Say help to see available commands."
    }


HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gmail AI Assistant</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:22px;font-family:Segoe UI,Arial,sans-serif;color:#292443;
background:radial-gradient(circle at top left,#dfd5ff,transparent 38%),
radial-gradient(circle at top right,#ffdcec,transparent 35%),
linear-gradient(135deg,#f8f7ff,#edf5ff);min-height:100vh}
main{max-width:1200px;margin:auto}
header,.panel,.stat{background:#ffffffdf;border:1px solid white;border-radius:20px;
box-shadow:0 10px 30px #51438e10}
header{padding:20px 24px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:13px}
.logo{width:50px;height:50px;border-radius:16px;display:grid;place-items:center;
background:linear-gradient(135deg,#7355f4,#ec63b6);color:white;font-size:26px}
h1{font-size:22px;margin:0}.muted{font-size:13px;color:#827b98;margin-top:5px}
.badge{background:#ddf8e9;color:#168250;padding:9px 13px;border-radius:22px;font-size:12px}
.hero{margin-top:20px;padding:30px;border-radius:23px;color:white;
background:linear-gradient(110deg,#5140d2,#8856ee,#e35fb5)}
.hero h2{font-size:clamp(25px,4vw,37px);margin:10px 0}
.hero p{line-height:1.6;color:#f3eaff}
button{border:0;border-radius:11px;padding:11px 14px;font-weight:650;cursor:pointer;transition:.2s}
button:hover{filter:brightness(1.06);transform:translateY(-1px)}
.white{background:white;color:#6445d8}.purple{background:linear-gradient(110deg,#7654f1,#a54be5);color:white}
.blue{background:linear-gradient(110deg,#339ef2,#625ff0);color:white}
.pink{background:linear-gradient(110deg,#ec61aa,#e35b88);color:white}
.light{background:#efebff;color:#6c50d8}
.actions,.chips{display:flex;gap:9px;flex-wrap:wrap;margin-top:17px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin:19px 0}
.stat{padding:17px}.stat .emoji{font-size:21px}
.stat strong{display:block;font-size:25px;margin:6px 0}
.stat span{font-size:12px;color:#817a97}
.layout{display:grid;grid-template-columns:290px minmax(0,1fr);gap:18px}
.panel{padding:21px;min-width:0}
h3{margin:0 0 7px}.mic-wrap{width:120px;height:120px;margin:22px auto;border-radius:50%;
background:linear-gradient(140deg,#e7dfff,#ffdfef);display:grid;place-items:center}
#mic{width:83px;height:83px;border-radius:50%;font-size:31px;color:white;
background:linear-gradient(140deg,#7654f3,#ec63b6);box-shadow:0 8px 24px #a36aef66}
#mic.listening{animation:pulse 1s infinite}
@keyframes pulse{50%{box-shadow:0 0 0 15px #e96db500,0 8px 24px #a36aef66}}
#voiceStatus{text-align:center;font-size:12px;color:#817994;min-height:32px}
.row{display:flex;gap:8px;margin-top:12px}
input{width:100%;min-width:0;padding:12px;border:1px solid #e4def5;border-radius:11px}
.chip{font-size:11px;background:#efebff;color:#6c50d8;padding:8px 10px}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:15px 0}
.filter{background:#f0edff;color:#7051d8;font-size:12px}
.filter.active{background:#7051dc;color:white}
#status{padding:11px;background:#f0edff;color:#6249b3;border-radius:10px;font-size:12px;margin:15px 0;overflow-wrap:anywhere}
.inboxhead{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
#emails{display:grid;gap:12px}
.email{padding:15px;border:1px solid #eee8fb;border-radius:15px;background:white}
.email h4{margin:0 0 7px;font-size:14px;overflow-wrap:anywhere}
.sender{font-size:12px;color:#796b9b;overflow-wrap:anywhere}
.snippet{font-size:13px;line-height:1.6;color:#716d81;overflow-wrap:anywhere}
.emailbuttons{display:flex;gap:8px;flex-wrap:wrap}
.emailbuttons button{font-size:12px;padding:8px 11px}
.tag{display:inline-block;margin:8px 5px 0 0;padding:4px 7px;border-radius:8px;background:#f0edff;color:#7051d8;font-size:10px}
.empty{text-align:center;padding:35px 12px;border:1px dashed #ddd4f3;border-radius:14px;color:#817994;line-height:1.8}
footer{text-align:center;color:#89829f;font-size:12px;padding:23px}
@media(max-width:850px){.layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:480px){body{padding:10px}.hero{padding:22px}.panel{padding:15px}.stats{gap:8px}.stat{padding:12px}}
</style>
</head>
<body>
<main>
<header>
 <div class="brand"><div class="logo">✉</div><div>
 <h1>Gmail AI Assistant</h1><div class="muted">Your inbox, made effortless</div>
 </div></div><span class="badge">● Assistant ready</span>
</header>

<section class="hero">
 <div>YOUR PERSONAL EMAIL ASSISTANT</div>
 <h2>Welcome back! 👋</h2>
 <p>Manage your inbox, find important messages, and use voice commands.</p>
 <div class="actions">
  <button class="white" onclick="loadEmails('inbox')">✉ Open Inbox</button>
  <button class="white" onclick="startListening()">🎙 Talk to Assistant</button>
  <button class="light" onclick="loadStats()">↻ Update Counts</button>
 </div>
</section>

<section class="stats">
 <div class="stat"><div class="emoji">📨</div><strong id="countInbox">—</strong><span>Total inbox emails</span></div>
 <div class="stat"><div class="emoji">📩</div><strong id="countUnread">—</strong><span>Unread emails</span></div>
 <div class="stat"><div class="emoji">⭐</div><strong id="countStarred">—</strong><span>Starred emails</span></div>
 <div class="stat"><div class="emoji">❗</div><strong id="countImportant">—</strong><span>Important emails</span></div>
</section>

<section class="layout">
<aside class="panel">
 <h3>🎙 Voice assistant</h3>
 <p class="muted">Speak a command or type it below.</p>
 <div class="mic-wrap"><button id="mic" onclick="startListening()">🎤</button></div>
 <div id="voiceStatus">Tap the microphone to start</div>
 <div class="row">
  <input id="command" placeholder="Try: unread emails"
   onkeydown="if(event.key==='Enter')sendCommand()">
  <button class="purple" onclick="sendCommand()">Send</button>
 </div>
 <div class="chips">
  <button class="chip" onclick="quick('unread emails')">Unread</button>
  <button class="chip" onclick="quick('important emails')">Important</button>
  <button class="chip" onclick="quick('starred emails')">Starred</button>
  <button class="chip" onclick="quick('count emails')">Count</button>
  <button class="chip" onclick="quick('tell me a joke')">Joke</button>
  <button class="chip" onclick="quick('help')">Help</button>
 </div>
 <button class="light" style="width:100%;margin-top:15px" onclick="stopAudio()">🔇 Stop audio</button>
</aside>

<section class="panel">
 <div class="inboxhead"><div><h3>📬 Email dashboard</h3>
 <div class="muted" id="filterName">Showing inbox</div></div>
 <button class="blue" onclick="loadEmails(currentFilter)">↻ Refresh</button></div>

 <div class="row">
  <input id="search" placeholder="Search sender or subject..."
   onkeydown="if(event.key==='Enter')searchEmails()">
  <button class="pink" onclick="searchEmails()">Search</button>
 </div>

 <div class="filters">
  <button class="filter active" data-filter="inbox" onclick="loadEmails('inbox')">Inbox</button>
  <button class="filter" data-filter="unread" onclick="loadEmails('unread')">Unread</button>
  <button class="filter" data-filter="starred" onclick="loadEmails('starred')">Starred</button>
  <button class="filter" data-filter="important" onclick="loadEmails('important')">Important</button>
  <button class="filter" data-filter="sent" onclick="loadEmails('sent')">Sent</button>
  <button class="filter" data-filter="drafts" onclick="loadEmails('drafts')">Drafts</button>
  <button class="filter" data-filter="attachments" onclick="loadEmails('attachments')">Attachments</button>
  <button class="filter" data-filter="spam" onclick="loadEmails('spam')">Spam</button>
  <button class="filter" data-filter="trash" onclick="loadEmails('trash')">Trash</button>
 </div>

 <div id="status" role="status" aria-live="polite">Loading dashboard...</div>
 <div id="emails"><div class="empty">💌<br>Loading your Gmail dashboard...</div></div>
</section>
</section>
<footer>Gmail AI Assistant · Python + Flask + Gmail API</footer>
</main>

<script>
let currentFilter = "inbox";

function status(text) {
 document.getElementById("status").textContent = text;
}
function quick(text) {
 document.getElementById("command").value = text;
 sendCommand(text);
}
function setActiveFilter(key) {
 document.querySelectorAll(".filter").forEach(button => {
  button.classList.toggle("active", button.dataset.filter === key);
 });
 currentFilter = key;
 const active = document.querySelector('[data-filter="' + key + '"]');
 document.getElementById("filterName").textContent =
  "Showing " + (active ? active.textContent : key);
}
async function loadStats() {
 status("Updating email counts...");
 try {
  const response = await fetch("/api/stats");
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Could not load counts");
  document.getElementById("countInbox").textContent = data.inbox ?? 0;
  document.getElementById("countUnread").textContent = data.unread ?? 0;
  document.getElementById("countStarred").textContent = data.starred ?? 0;
  document.getElementById("countImportant").textContent = data.important ?? 0;
  status("Email counts updated.");
 } catch (error) {
  status("Error: " + error.message);
 }
}
async function loadEmails(filter) {
 filter = filter || currentFilter;
 setActiveFilter(filter);
 status("Loading " + filter + " emails...");
 try {
  const response = await fetch("/api/emails?filter=" + encodeURIComponent(filter));
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Could not load emails");
  renderEmails(data.emails || []);
  status("Showing " + (data.emails || []).length + " messages from " + filter +
   ". Total matching: " + (data.total ?? data.emails.length) + ".");
 } catch (error) {
  status("Error: " + error.message);
 }
}
async function searchEmails() {
 const term = document.getElementById("search").value.trim();
 if (!term) { status("Enter a sender or subject to search."); return; }
 setActiveFilter("inbox");
 status("Searching emails...");
 try {
  const response = await fetch("/api/search?q=" + encodeURIComponent(term));
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Search failed");
  renderEmails(data.emails || []);
  status("Found " + (data.total ?? data.emails.length) + " matching emails.");
 } catch (error) {
  status("Error: " + error.message);
 }
}
async function sendCommand(text) {
 const command = (typeof text === "string" ? text :
  document.getElementById("command").value).trim();
 if (!command) { status("Type or speak a command."); return; }
 document.getElementById("command").value = command;
 status("Processing: " + command);
 try {
  const response = await fetch("/api/command", {
   method: "POST",
   headers: {"Content-Type": "application/json"},
   body: JSON.stringify({command})
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Command failed");
  status(data.reply || "Done");
  if (data.stats) updateStats(data.stats);
  if (data.emails) {
   renderEmails(data.emails);
   if (data.filter) setActiveFilter(data.filter);
   else document.getElementById("filterName").textContent = "Search results";
  }
  if (data.selected) {
   renderEmails([data.selected]);
   speak(data.selected.subject + ". " +
    (data.selected.body || data.selected.snippet || ""));
  } else if (data.reply) speak(data.reply);
  loadStats();
 } catch (error) {
  status("Error: " + error.message);
 }
}
function updateStats(data) {
 ["inbox","unread","starred","important"].forEach(key => {
  const node = document.getElementById("count" + key[0].toUpperCase() + key.slice(1));
  if (node) node.textContent = data[key] ?? 0;
 });
}
function renderEmails(emails) {
 const root = document.getElementById("emails");
 root.replaceChildren();
 if (!emails.length) {
  root.innerHTML = '<div class="empty">📭<br><b>No emails found</b><br>Try another filter or search.</div>';
  return;
 }
 emails.forEach((email, index) => {
  const card = document.createElement("article");
  card.className = "email";
  const title = document.createElement("h4");
  title.textContent = (email.number || index + 1) + ". " + (email.subject || "(No subject)");
  const sender = document.createElement("div");
  sender.className = "sender";
  sender.textContent = "From: " + (email.sender || "Unknown sender");
  const date = document.createElement("div");
  date.className = "sender";
  date.textContent = email.date || "";
  const tags = document.createElement("div");
  if (email.unread) tags.append(makeTag("UNREAD"));
  if (email.starred) tags.append(makeTag("⭐ STARRED"));
  if (email.important) tags.append(makeTag("IMPORTANT"));
  if (email.attachments) tags.append(makeTag("ATTACHMENT"));
  const snippet = document.createElement("p");
  snippet.className = "snippet";
  snippet.textContent = email.snippet || email.body || "No preview available.";
  const buttons = document.createElement("div");
  buttons.className = "emailbuttons";
  const read = document.createElement("button");
  read.className = "purple";
  read.textContent = "🔊 Read aloud";
  read.onclick = () => speak((email.subject || "") + ". " +
   (email.body || email.snippet || "No message content available."));
  const stop = document.createElement("button");
  stop.className = "light";
  stop.textContent = "■ Stop";
  stop.onclick = stopAudio;
  buttons.append(read, stop);
  card.append(title, sender, date, tags, snippet, buttons);
  root.append(card);
 });
}
function makeTag(text) {
 const tag = document.createElement("span");
 tag.className = "tag";
 tag.textContent = text;
 return tag;
}
function speak(text) {
 if (!("speechSynthesis" in window)) return;
 speechSynthesis.cancel();
 const utterance = new SpeechSynthesisUtterance(text);
 utterance.lang = "en-IN";
 utterance.rate = 0.95;
 speechSynthesis.speak(utterance);
}
function stopAudio() {
 if ("speechSynthesis" in window) speechSynthesis.cancel();
 document.getElementById("voiceStatus").textContent = "Audio stopped";
}
function startListening() {
 const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
 if (!SR) {
  status("Voice recognition is unavailable. Type a command instead.");
  return;
 }
 const mic = document.getElementById("mic");
 const recognition = new SR();
 recognition.lang = "en-IN";
 recognition.interimResults = false;
 recognition.continuous = false;
 recognition.onstart = () => {
  mic.classList.add("listening");
  document.getElementById("voiceState").textContent = "Listening";
  document.getElementById("voiceStatus").textContent = "Listening... Speak now.";
 };
 recognition.onresult = event => {
  const text = event.results[0][0].transcript.trim();
  document.getElementById("command").value = text;
  document.getElementById("voiceStatus").textContent = "Heard: " + text;
  sendCommand(text);
 };
 recognition.onerror = event => {
  document.getElementById("voiceStatus").textContent =
   "Voice error: " + event.error + ". Try typing instead.";
 };
 recognition.onend = () => {
  mic.classList.remove("listening");
  document.getElementById("voiceState").textContent = "Ready";
 };
 try { recognition.start(); }
 catch (error) {
  document.getElementById("voiceStatus").textContent =
   "Wait a moment, then try again.";
 }
}
loadStats();
loadEmails("inbox");
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/api/stats")
def stats_api():
    try:
        return jsonify(get_stats())
    except Exception as error:
        app.logger.exception("Gmail stats error")
        return jsonify(error=str(error)), 500


@app.route("/api/emails")
def emails_api():
    try:
        key = request.args.get("filter", "inbox")
        if key not in FILTERS:
            return jsonify(error="Unknown email filter"), 400

        label, query = FILTERS[key]
        emails, total = fetch_emails(query, 20)

        return jsonify(
            emails=emails,
            total=total,
            filter=key,
            label=label
        )
    except Exception as error:
        app.logger.exception("Gmail email error")
        return jsonify(error=str(error)), 500


@app.route("/api/search")
def search_api():
    try:
        term = request.args.get("q", "").strip()
        if not term:
            return jsonify(error="Enter a search term"), 400

        # Search both sender and subject.
        query = f"in:anywhere (from:({term}) OR subject:({term}))"
        emails, total = fetch_emails(query, 20)

        return jsonify(emails=emails, total=total)
    except Exception as error:
        app.logger.exception("Gmail search error")
        return jsonify(error=str(error)), 500


@app.route("/api/command", methods=["POST"])
def command_api():
    try:
        data = request.get_json(silent=True) or {}
        return jsonify(process_command(data.get("command", "")))
    except Exception as error:
        app.logger.exception("Gmail command error")
        return jsonify(error=str(error)), 500


if __name__ == "__main__":
    print("Gmail AI Assistant: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)

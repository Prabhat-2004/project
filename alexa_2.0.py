
from flask import Flask, request, jsonify, render_template_string
import os
import sys
import platform
import subprocess
import webbrowser
import psutil
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

HOME = Path.home()

# ---------------- FRONTEND ----------------

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alexa_2.O Voice Assistant</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #080e1c;
    color: #edf4ff;
    font-family: Arial, sans-serif;
    padding: 25px;
}

main {
    max-width: 900px;
    margin: auto;
}

header {
    text-align: center;
    margin-bottom: 25px;
}

header h1 {
    color: #68caff;
    font-size: 34px;
}

header p, .muted {
    color: #9baecb;
}

.panel {
    background: #121c30;
    border: 1px solid #293b58;
    border-radius: 17px;
    padding: 22px;
    margin-bottom: 18px;
}

.mic {
    display: block;
    margin: 22px auto;
    height: 95px;
    width: 95px;
    border: none;
    border-radius: 50%;
    background: linear-gradient(135deg, #087bff, #13c8d9);
    color: white;
    font-size: 38px;
    cursor: pointer;
}

input {
    width: 100%;
    padding: 14px;
    border: 1px solid #354866;
    border-radius: 10px;
    background: #091326;
    color: white;
    font-size: 16px;
}

button {
    cursor: pointer;
}

.action {
    margin-top: 10px;
    padding: 12px 18px;
    border: none;
    border-radius: 9px;
    background: #1678ed;
    color: white;
    font-size: 15px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
}

.stat {
    padding: 17px;
    border-radius: 12px;
    background: #091326;
}

.stat small {
    color: #9baecb;
}

.stat h3 {
    color: #68caff;
    overflow-wrap: anywhere;
}

#response {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.7;
}

#files li {
    margin-bottom: 8px;
    overflow-wrap: anywhere;
}

.status {
    color: #75e7b0;
}

.note {
    font-size: 13px;
    color: #9baecb;
    line-height: 1.6;
}

@media (max-width: 500px) {
    body { padding: 12px; }
    .panel { padding: 16px; }
}
</style>
</head>

<body>
<main>

<header>
    <h1>Alexa_2.O</h1>
    <p>Your personal Windows voice assistant</p>
    <div class="status" id="status">● System ready</div>
</header>

<section class="panel">
    <h2>🎙 Voice Control</h2>

    <button class="mic" id="mic" title="Speak">🎤</button>
    <p id="heard" style="text-align:center">
        Click the microphone and speak
    </p>

    <form id="commandForm">
        <input id="command"
               placeholder="Try: open Chrome, open WhatsApp, system info"
               autocomplete="off">
        <button class="action" type="submit">Run Command</button>
    </form>

    <p class="note">
        Use Chrome or Edge and allow microphone permission.
        Browser voice recognition may require internet access.
    </p>
</section>

<section class="panel">
    <h2>💻 System Dashboard</h2>

    <div class="grid">
        <div class="stat">
            <small>Operating System</small>
            <h3 id="os">Loading...</h3>
        </div>
        <div class="stat">
            <small>CPU Usage</small>
            <h3 id="cpu">--</h3>
        </div>
        <div class="stat">
            <small>RAM Usage</small>
            <h3 id="ram">--</h3>
        </div>
        <div class="stat">
            <small>Disk Usage</small>
            <h3 id="disk">--</h3>
        </div>
    </div>

    <button class="action" onclick="loadSystem()">
        Refresh System Data
    </button>
</section>

<section class="panel">
    <h2>💬 Assistant Response</h2>
    <div id="response">Hello! I am Alexa_2.O. How can I help?</div>

    <h3>📁 Home Folder Files</h3>
    <ul id="files">
        <li>Say "list files" to view filenames.</li>
    </ul>
</section>

<section class="panel">
    <h3>Available Commands</h3>
    <p class="note">
        open Chrome · open WhatsApp · open Notepad · open Calculator ·
        open VS Code · open Paint · open File Explorer · open Downloads ·
        open YouTube · open Google · open Gmail · system info ·
        list files · find file resume · time · date · help
    </p>
</section>

</main>

<script>
const statusEl = document.getElementById("status");
const responseEl = document.getElementById("response");
const heardEl = document.getElementById("heard");

function speak(text) {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-IN";
        window.speechSynthesis.speak(utterance);
    }
}

async function runCommand(text) {
    if (!text.trim()) return;

    document.getElementById("command").value = text;
    heardEl.textContent = "Command: " + text;
    statusEl.textContent = "● Processing...";

    try {
        const response = await fetch("/command", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({command: text})
        });

        const data = await response.json();

        responseEl.textContent =
            data.response || data.error || "No response received.";

        if (data.files) {
            const list = document.getElementById("files");
            list.replaceChildren();

            data.files.forEach(file => {
                const li = document.createElement("li");
                li.textContent = file;
                list.appendChild(li);
            });
        }

        statusEl.textContent = "● System ready";

        if (data.speak !== false) {
            speak(data.response || data.error || "Done");
        }

        loadSystem();

    } catch (error) {
        responseEl.textContent =
            "Could not connect to Flask. Check the terminal.";
        statusEl.textContent = "● Connection error";
    }
}

document.getElementById("commandForm").addEventListener(
    "submit", function(event) {
        event.preventDefault();
        runCommand(document.getElementById("command").value);
    }
);

const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

document.getElementById("mic").addEventListener("click", function() {
    if (!SpeechRecognition) {
        responseEl.textContent =
            "Speech recognition is unsupported. Try Chrome or Edge.";
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        statusEl.textContent = "● Listening...";
        heardEl.textContent = "Listening... Speak now.";
    };

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        heardEl.textContent = "You said: " + text;
        runCommand(text);
    };

    recognition.onerror = function(event) {
        statusEl.textContent = "● Microphone error";
        responseEl.textContent =
            "Voice error: " + event.error +
            ". Check microphone permission.";
    };

    recognition.onend = function() {
        if (statusEl.textContent.includes("Listening")) {
            statusEl.textContent = "● System ready";
        }
    };

    recognition.start();
});

async function loadSystem() {
    try {
        const response = await fetch("/system");
        const data = await response.json();

        document.getElementById("os").textContent = data.os;
        document.getElementById("cpu").textContent = data.cpu + "%";
        document.getElementById("ram").textContent = data.ram + "%";
        document.getElementById("disk").textContent = data.disk + "%";
    } catch (error) {
        // Dashboard will retry when refreshed.
    }
}

loadSystem();
</script>
</body>
</html>
"""


# ---------------- SYSTEM INFORMATION ----------------

def get_system_data():
    disk_path = os.environ.get("SystemDrive", "C:") + os.sep

    try:
        disk_usage = psutil.disk_usage(disk_path).percent
    except OSError:
        disk_usage = 0

    return {
        "os": platform.system() + " " + platform.release(),
        "cpu": psutil.cpu_percent(interval=0.2),
        "ram": psutil.virtual_memory().percent,
        "disk": disk_usage
    }


# ---------------- OPEN APPLICATIONS ----------------

def open_app(app_name):
    app_name = app_name.strip().lower()

    aliases = {
        "google chrome": "chrome",
        "google": "chrome",
        "chrome browser": "chrome",
        "note pad": "notepad",
        "whats app": "whatsapp",
        "vs code": "vscode",
        "visual studio code": "vscode",
        "visual studio": "vscode",
        "code editor": "vscode",
        "file explorer": "explorer",
        "my computer": "explorer",
        "this pc": "explorer",
        "files": "explorer",
        "calc": "calculator",
        "command prompt": "cmd",
        "terminal": "cmd",
        "task manager": "taskmgr",
        "downloads folder": "downloads",
        "web browser": "browser"
    }

    app_name = aliases.get(app_name, app_name)

    # Website shortcuts
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "whatsapp web": "https://web.whatsapp.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com"
    }

    if app_name in websites:
        webbrowser.open(websites[app_name])
        return f"Opening {app_name.title()}."

    if platform.system() != "Windows":
        return "Application launching is configured for Windows."

    # Windows built-in apps
    built_in = {
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "explorer": ["explorer.exe"],
        "paint": ["mspaint.exe"],
        "cmd": ["cmd.exe"],
        "powershell": ["powershell.exe"],
        "taskmgr": ["taskmgr.exe"],
    }

    try:
        if app_name in built_in:
            subprocess.Popen(built_in[app_name])
            return f"Opening {app_name.title()}."

        if app_name == "downloads":
            folder = HOME / "Downloads"
            if folder.is_dir():
                os.startfile(str(folder))
                return "Opening Downloads folder."
            return "Downloads folder was not found."

        if app_name == "browser":
            webbrowser.open("https://www.google.com")
            return "Opening your default browser."

        if app_name == "chrome":
            candidates = [
                Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
                / "Google/Chrome/Application/chrome.exe",
                Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
                / "Google/Chrome/Application/chrome.exe",
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Google/Chrome/Application/chrome.exe"
            ]

            for path in candidates:
                if path.is_file():
                    subprocess.Popen([str(path)])
                    return "Opening Google Chrome."

            # Chrome may be registered in Windows.
            try:
                os.startfile("chrome")
                return "Opening Google Chrome."
            except OSError:
                return (
                    "Chrome was not found. Check its installation, "
                    "or use open browser."
                )

        if app_name == "whatsapp":
            # The desktop app may register this protocol.
            try:
                os.startfile("whatsapp:")
                return "Opening WhatsApp."
            except OSError:
                return (
                    "WhatsApp desktop could not be launched. "
                    "Opening WhatsApp Web instead."
                ) if webbrowser.open("https://web.whatsapp.com") else (
                    "Could not open WhatsApp."
                )

        if app_name == "vscode":
            # Check typical VS Code installation paths.
            candidates = [
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Programs/Microsoft VS Code/Code.exe",
                Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
                / "Microsoft VS Code/Code.exe"
            ]

            for path in candidates:
                if path.is_file():
                    subprocess.Popen([str(path)])
                    return "Opening Visual Studio Code."

            try:
                subprocess.Popen(["code"])
                return "Launching Visual Studio Code."
            except OSError:
                return (
                    "VS Code was not found. Install it or add its "
                    "command-line launcher to PATH."
                )

        # Find matching installed Start Menu shortcuts.
        start_menu_dirs = [
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft/Windows/Start Menu/Programs",
            Path(os.environ.get("PROGRAMDATA", ""))
            / "Microsoft/Windows/Start Menu/Programs"
        ]

        for folder in start_menu_dirs:
            if folder.is_dir():
                for shortcut in folder.rglob("*.lnk"):
                    if shortcut.stem.lower() == app_name:
                        os.startfile(str(shortcut))
                        return f"Opening {shortcut.stem}."

        return (
            f"Could not find {app_name}. Make sure it is installed. "
            "You can also use its exact Start Menu application name."
        )

    except (OSError, subprocess.SubprocessError) as error:
        app.logger.exception("Unable to open application")
        return f"Could not open {app_name}: {error}"


# ---------------- FILE MANAGEMENT ----------------

def list_files():
    try:
        return sorted(item.name for item in HOME.iterdir())[:50]
    except OSError:
        return []


def find_files(term):
    matches = []
    ignored = {
        "appdata", ".git", "node_modules",
        "__pycache__", ".venv"
    }

    try:
        for root, dirs, files in os.walk(HOME):
            dirs[:] = [
                folder for folder in dirs
                if folder.lower() not in ignored
            ]

            for filename in files:
                if term.lower() in filename.lower():
                    matches.append(str(Path(root) / filename))

                    if len(matches) >= 20:
                        return matches

    except OSError:
        pass

    return matches


# ---------------- COMMAND HANDLER ----------------

def handle_command(command):
    cmd = command.strip().lower()

    if not cmd:
        return {"response": "Please enter a command."}

    if cmd in ("hello", "hi", "hello alexa", "hey alexa"):
        return {
            "response": "Hello! I am Alexa 2.O. How can I help you?"
        }

    if cmd == "help" or cmd == "commands" or cmd == "what can you do":
        return {
            "response": (
                "Available commands: open Chrome, WhatsApp, Notepad, "
                "Calculator, VS Code, Paint, File Explorer, Downloads, "
                "YouTube, Google, Gmail, GitHub, ChatGPT; "
                "system info; list files; find file resume; time; date."
            )
        }

    if cmd in ("time", "what is the time", "tell me the time"):
        return {
            "response": "The time is " + datetime.now().strftime("%I:%M %p")
        }

    if cmd == "date" or cmd == "what is the date" or cmd == "today's date":
        return {
            "response": "Today's date is " + datetime.now().strftime("%d %B %Y")
        }

    if cmd in ("system info", "system status", "computer info"):
        data = get_system_data()
        return {
            "response": (
                f"Operating system: {data['os']}. "
                f"CPU usage: {data['cpu']} percent. "
                f"RAM usage: {data['ram']} percent. "
                f"Disk usage: {data['disk']} percent."
            )
        }

    if cmd in ("list files", "show files", "my files", "show my files"):
        files = list_files()
        return {
            "response": f"Found {len(files)} entries in your home folder.",
            "files": files
        }

    if cmd.startswith("find file "):
        term = cmd[len("find file "):].strip()

        if not term or len(term) > 100:
            return {"response": "Please enter a valid filename to search."}

        matches = find_files(term)

        if matches:
            return {
                "response": "Matching files:\n" + "\n".join(matches),
                "files": matches
            }

        return {"response": "No matching files were found."}

    # Open any requested app through the safe app resolver.
    if cmd.startswith("open "):
        app_name = cmd[5:].strip()

        if not app_name or len(app_name) > 100:
            return {"response": "Please provide a valid application name."}

        return {"response": open_app(app_name)}

    # Support a few natural voice phrases.
    if cmd.startswith("launch "):
        return {"response": open_app(cmd[7:].strip())}

    if cmd.startswith("start "):
        return {"response": open_app(cmd[6:].strip())}

    if cmd in ("show downloads", "open my downloads"):
        return {"response": open_app("downloads")}

    if cmd in ("open browser", "browse internet"):
        return {"response": open_app("browser")}

    return {
        "response": (
            "I don't know that command yet. Say help to see "
            "the supported commands."
        )
    }


# ---------------- FLASK ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/system")
def system():
    return jsonify(get_system_data())


@app.route("/command", methods=["POST"])
def command():
    data = request.get_json(silent=True) or {}
    text = data.get("command", "")

    if not isinstance(text, str) or len(text) > 300:
        return jsonify({"error": "Invalid command."}), 400

    try:
        result = handle_command(text)
        return jsonify(result)

    except Exception:
        app.logger.exception("Command processing failed")
        return jsonify({
            "error": "Something went wrong. Check the Flask terminal."
        }), 500


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    print("=" * 45)
    print(" Alexa_2.O Voice Assistant")
    print(" Open http://127.0.0.1:5000")
    print(" Press CTRL+C to stop")
    print("=" * 45)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

def open_app(app_name):
    app = app_name.lower().strip()

    apps = {
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "calc": ["calc.exe"],
        "paint": ["mspaint.exe"],
        "file explorer": ["explorer.exe"],
        "explorer": ["explorer.exe"],
        "command prompt": ["cmd.exe"],
        "cmd": ["cmd.exe"],
        "powershell": ["powershell.exe"],
        "task manager": ["taskmgr.exe"],
    }

    websites = {
        "chrome": "https://www.google.com",
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "whatsapp": "https://web.whatsapp.com",
        "whatsapp web": "https://web.whatsapp.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "gmail": "https://mail.google.com",
    }

    try:
        if app in apps:
            subprocess.Popen(apps[app])
            return f"Opening {app}"

        if app in websites:
            if app == "whatsapp":
                try:
                    os.startfile("whatsapp:")
                    return "Opening WhatsApp application"
                except OSError:
                    pass

            webbrowser.open(websites[app])
            return f"Opening {app}"

        if app in ("vscode", "vs code", "visual studio code"):
            subprocess.Popen(["cmd", "/c", "start", "", "code"])
            return "Opening Visual Studio Code"

        if app in ("downloads", "download folder"):
            os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))
            return "Opening Downloads folder"

        return f"App not configured: {app}. Try Notepad or Calculator."

    except Exception as e:
        return f"Could not open {app}: {e}"

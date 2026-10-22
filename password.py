
from flask import Flask, request, session, redirect, url_for, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "local-demo-secret-change-me"
)

PASSWORD = "Preeti"
MAX_ATTEMPTS = 3

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NOIR | Secure Access</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #070a12;
    --panel: rgba(15, 20, 34, .88);
    --cyan: #72f0e2;
    --purple: #a394ff;
    --white: #f4f5fb;
    --muted: #8992aa;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    color: var(--white);
    background:
        radial-gradient(ellipse at 15% 15%, #292050 0, transparent 38%),
        radial-gradient(ellipse at 90% 85%, #063d42 0, transparent 35%),
        var(--bg);
    font-family: 'Manrope', sans-serif;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: .23;
    background-image:
        linear-gradient(#65728b15 1px, transparent 1px),
        linear-gradient(90deg, #65728b15 1px, transparent 1px);
    background-size: 45px 45px;
}

.orb {
    position: fixed;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    filter: blur(100px);
    opacity: .25;
    pointer-events: none;
    animation: float 9s ease-in-out infinite alternate;
}

.orb.one {
    background: #7663ff;
    top: 5%;
    left: -120px;
}

.orb.two {
    background: #00e5cc;
    bottom: 0;
    right: -100px;
    animation-delay: -4s;
}

header {
    width: min(1100px, 90%);
    margin: auto;
    height: 82px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #ffffff16;
    position: relative;
    z-index: 1;
}

.brand {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 5px;
}

.brand span {
    color: var(--cyan);
}

.status {
    display: flex;
    align-items: center;
    gap: 9px;
    color: #a6b0c5;
    font: 10px 'DM Mono', monospace;
    letter-spacing: 1px;
}

.status i {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 12px var(--cyan);
}

main {
    flex: 1;
    display: grid;
    place-items: center;
    padding: 45px 18px;
    position: relative;
    z-index: 1;
}

.card {
    width: min(440px, 100%);
    padding: 34px;
    position: relative;
    border: 1px solid #b9c7ed30;
    background: var(--panel);
    backdrop-filter: blur(20px);
    box-shadow: 0 30px 100px #0008;
    animation: appear .8s ease both;
}

.card::before,
.card::after {
    content: "";
    position: absolute;
    width: 35px;
    height: 35px;
    pointer-events: none;
}

.card::before {
    top: -1px;
    left: -1px;
    border-top: 2px solid var(--cyan);
    border-left: 2px solid var(--cyan);
}

.card::after {
    bottom: -1px;
    right: -1px;
    border-right: 2px solid var(--purple);
    border-bottom: 2px solid var(--purple);
}

.topline {
    display: flex;
    justify-content: space-between;
    color: #77839d;
    font: 9px 'DM Mono', monospace;
    letter-spacing: 1.5px;
}

.topline span:last-child {
    color: var(--cyan);
}

.emblem {
    width: 100px;
    height: 100px;
    margin: 30px auto 25px;
    display: grid;
    place-items: center;
    border: 1px solid #72f0e24d;
    border-radius: 50%;
    position: relative;
    color: var(--cyan);
    font-size: 37px;
    background: radial-gradient(circle, #72f0e219, transparent 70%);
    box-shadow: 0 0 40px #72f0e20d;
}

.emblem::before {
    content: "";
    position: absolute;
    inset: 8px;
    border: 1px dashed #a394ff80;
    border-radius: 50%;
    animation: rotate 20s linear infinite;
}

.emblem::after {
    content: "";
    position: absolute;
    width: 6px;
    height: 6px;
    top: 9px;
    right: 14px;
    border-radius: 50%;
    background: var(--purple);
    box-shadow: 0 0 12px var(--purple);
}

.eyebrow {
    text-align: center;
    color: var(--cyan);
    font: 10px 'DM Mono', monospace;
    letter-spacing: 2px;
    margin: 0 0 12px;
}

h1 {
    text-align: center;
    font-size: clamp(27px, 5vw, 34px);
    line-height: 1.25;
    letter-spacing: -1.5px;
    margin: 0;
}

h1 span {
    color: var(--cyan);
}

.subtitle {
    text-align: center;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
    margin: 12px 0 25px;
}

.separator {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 23px;
    color: #707b93;
    font: 8px 'DM Mono', monospace;
    letter-spacing: 1px;
}

.separator::before,
.separator::after {
    content: "";
    height: 1px;
    flex: 1;
    background: #ffffff1c;
}

.attempt-head {
    display: flex;
    justify-content: space-between;
    color: #8f99af;
    font: 10px 'DM Mono', monospace;
    margin-bottom: 10px;
}

.attempt-head strong {
    color: var(--cyan);
    font-weight: 400;
}

.bars {
    display: flex;
    gap: 7px;
    margin-bottom: 24px;
}

.bars span {
    height: 4px;
    flex: 1;
    background: #72f0e245;
    transition: background .3s;
}

.bars span.used {
    background: #ff647e;
    box-shadow: 0 0 8px #ff647e33;
}

.message {
    padding: 12px;
    margin: -6px 0 20px;
    font-size: 11px;
    line-height: 1.6;
    background: #ff647e0d;
    border-left: 2px solid #ff647e;
    color: #ff9aa9;
}

.message.success {
    color: var(--cyan);
    background: #72f0e20d;
    border-color: var(--cyan);
}

label {
    display: block;
    color: #b1bbd0;
    font: 10px 'DM Mono', monospace;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
}

.input-box {
    display: flex;
    align-items: center;
    gap: 10px;
    height: 53px;
    padding: 0 13px;
    border: 1px solid #9eadd02e;
    background: #03060c80;
    transition: border-color .2s, box-shadow .2s;
}

.input-box:focus-within {
    border-color: var(--cyan);
    box-shadow: 0 0 0 3px #72f0e20b;
}

.input-box .icon {
    color: var(--cyan);
    font-size: 18px;
}

input {
    width: 100%;
    min-width: 0;
    border: 0;
    outline: 0;
    background: transparent;
    color: var(--white);
    font: 12px 'Manrope', sans-serif;
}

input::placeholder {
    color: #626d84;
}

.show {
    border: 0;
    padding: 8px 0 8px 5px;
    background: transparent;
    color: var(--cyan);
    cursor: pointer;
    font: 9px 'DM Mono', monospace;
}

button.submit {
    width: 100%;
    height: 52px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding: 0 17px;
    border: 1px solid var(--cyan);
    background: var(--cyan);
    color: #071211;
    font: 10px 'DM Mono', monospace;
    letter-spacing: 1px;
    cursor: pointer;
    transition: .25s;
}

button.submit:hover {
    background: #b0fff5;
    box-shadow: 0 0 25px #72f0e226;
    transform: translateY(-2px);
}

button.submit .arrow {
    font-size: 18px;
}

.state {
    text-align: center;
    padding: 15px 0 4px;
}

.state-icon {
    width: 50px;
    height: 50px;
    display: grid;
    place-items: center;
    margin: auto auto 15px;
    border: 1px solid var(--cyan);
    border-radius: 50%;
    color: var(--cyan);
    font-size: 23px;
}

.state.locked .state-icon {
    color: #ff8498;
    border-color: #ff647e;
}

.state h2 {
    font-size: 19px;
    margin: 0 0 9px;
}

.state p {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
    margin: 0;
}

.secure-note {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 28px;
    color: #68738b;
    font: 8px 'DM Mono', monospace;
    letter-spacing: .6px;
}

.secure-note .line {
    flex: 1;
    height: 1px;
    background: #ffffff18;
}

.secure-note b {
    color: var(--cyan);
    font-weight: 400;
}

footer {
    width: min(1100px, 90%);
    min-height: 62px;
    margin: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    border-top: 1px solid #ffffff16;
    color: #626e85;
    font: 8px 'DM Mono', monospace;
    letter-spacing: 1px;
    position: relative;
    z-index: 1;
}

@keyframes rotate {
    to { transform: rotate(360deg); }
}

@keyframes appear {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
    to { transform: translate(35px, 25px) scale(1.1); }
}

@media (max-width: 480px) {
    header, footer {
        width: 90%;
    }

    header {
        height: 70px;
    }

    .card {
        padding: 25px 22px;
    }

    footer {
        flex-wrap: wrap;
        justify-content: center;
        padding: 15px 0;
        text-align: center;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
</head>

<body>
<div class="orb one"></div>
<div class="orb two"></div>

<header>
    <div class="brand">N<span>.</span> NOIR</div>
    <div class="status"><i></i> SYSTEM ONLINE</div>
</header>

<main>
<section class="card">

    <div class="topline">
        <span>IDENTITY PROTOCOL</span>
        <span>SEC-03</span>
    </div>

    <div class="emblem">◈</div>

    <p class="eyebrow">RESTRICTED ENVIRONMENT</p>
    <h1>Enter the <span>unknown.</span></h1>
    <p class="subtitle">
        Authenticate your identity to access the system.
    </p>

    <div class="separator">SECURE ACCESS</div>

    <div class="attempt-head">
        <span>LOGIN ATTEMPTS</span>
        <strong>{{ remaining }} / 3 LEFT</strong>
    </div>

    <div class="bars">
        {% for i in range(3) %}
            <span class="{% if i < attempts %}used{% endif %}"></span>
        {% endfor %}
    </div>

    {% if message %}
        <div class="message {{ message_type }}">
            {{ message }}
        </div>
    {% endif %}

    {% if authenticated %}
        <div class="state">
            <div class="state-icon">✓</div>
            <h2>Identity confirmed</h2>
            <p>Welcome back. Your demo session is active.</p>

            <form method="post" action="{{ url_for('reset') }}">
                <button class="submit" type="submit">
                    <span>END SESSION</span>
                    <span class="arrow">↗</span>
                </button>
            </form>
        </div>

    {% elif locked %}
        <div class="state locked">
            <div class="state-icon">!</div>
            <h2>Access suspended</h2>
            <p>All three attempts have been used.</p>

            <form method="post" action="{{ url_for('reset') }}">
                <button class="submit" type="submit">
                    <span>RESET DEMO</span>
                    <span class="arrow">↗</span>
                </button>
            </form>
        </div>

    {% else %}
        <form method="post" action="{{ url_for('login') }}">
            <label for="password">PASSPHRASE</label>

            <div class="input-box">
                <span class="icon">⌑</span>

                <input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Enter your password"
                    autocomplete="current-password"
                    required
                    autofocus
                >

                <button
                    class="show"
                    type="button"
                    id="togglePassword"
                >SHOW</button>
            </div>

            <button class="submit" type="submit">
                <span>AUTHORIZE ACCESS</span>
                <span class="arrow">↗</span>
            </button>
        </form>
    {% endif %}

    <div class="secure-note">
        <b>▣</b>
        <span>SESSION STATUS</span>
        <span class="line"></span>
        <span>{{ "LOCKED" if locked else ("ACTIVE" if authenticated else "READY") }}</span>
    </div>

</section>
</main>

<footer>
    <span>© 2026 NOIR SYSTEMS</span>
    <span>FLASK POWERED</span>
    <span>DESIGNED FOR THE CURIOUS</span>
</footer>

<script>
const toggle = document.getElementById("togglePassword");
const password = document.getElementById("password");

if (toggle && password) {
    toggle.addEventListener("click", function () {
        const reveal = password.type === "password";
        password.type = reveal ? "text" : "password";
        toggle.textContent = reveal ? "HIDE" : "SHOW";
    });
}
</script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    session.setdefault("attempts", 0)
    session.setdefault("locked", False)
    session.setdefault("authenticated", False)

    message = ""
    message_type = ""

    if request.method == "POST":

        if session["locked"]:
            message = "Account locked. Reset the demo to try again."
            message_type = "error"

        elif session["authenticated"]:
            message = "You are already logged in."
            message_type = "success"

        else:
            entered_password = request.form.get("password", "")

            if entered_password == PASSWORD:
                session["authenticated"] = True
                message = "Correct password! Welcome back."
                message_type = "success"

            else:
                session["attempts"] += 1
                remaining = MAX_ATTEMPTS - session["attempts"]

                if remaining <= 0:
                    session["locked"] = True
                    message = (
                        "Incorrect password. "
                        "Account is locked."
                    )
                else:
                    word = "attempt" if remaining == 1 else "attempts"
                    message = (
                        f"Incorrect password. "
                        f"{remaining} {word} left."
                    )

                message_type = "error"

    remaining = max(
        0,
        MAX_ATTEMPTS - session["attempts"]
    )

    return render_template_string(
        HTML,
        message=message,
        message_type=message_type,
        attempts=session["attempts"],
        remaining=remaining,
        locked=session["locked"],
        authenticated=session["authenticated"]
    )


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

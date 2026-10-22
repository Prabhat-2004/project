
from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML + CSS Frontend
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Calculator ❤️</title>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            font-family: 'Poppins', sans-serif;
            color: white;
            background:
                radial-gradient(circle at top left, #59204f, transparent 45%),
                radial-gradient(circle at bottom right, #491b62, transparent 45%),
                linear-gradient(135deg, #080b20, #1b102d, #090c1e);
        }

        .container {
            width: 100%;
            max-width: 460px;
            text-align: center;
            padding: 32px 25px;
            border: 1px solid #ff579e55;
            border-radius: 25px;
            background: rgba(12, 12, 34, 0.85);
            box-shadow: 0 15px 60px #0008, 0 0 30px #ff247f15;
            animation: appear 0.8s ease;
        }

        .heart {
            font-size: 65px;
            color: #ff438d;
            text-shadow: 0 0 25px #ff247f;
            animation: beat 1.3s infinite;
        }

        h1 {
            font-size: 32px;
            margin: 8px 0;
        }

        h1 span {
            color: #ff579e;
        }

        .subtitle {
            color: #c8b8d9;
            font-size: 14px;
            margin-bottom: 28px;
        }

        form {
            text-align: left;
        }

        label {
            display: block;
            margin: 15px 0 8px;
            color: #ffd2e6;
            font-size: 14px;
        }

        input {
            width: 100%;
            padding: 14px;
            border-radius: 11px;
            border: 1px solid #39304f;
            outline: none;
            color: white;
            background: #19162c;
            font: inherit;
        }

        input:focus {
            border-color: #ff438d;
            box-shadow: 0 0 12px #ff438d33;
        }

        input::placeholder {
            color: #92889f;
        }

        button {
            width: 100%;
            margin-top: 25px;
            padding: 15px;
            border: none;
            border-radius: 12px;
            color: white;
            background: linear-gradient(100deg, #f72585, #ff4d55);
            font: inherit;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px #ff247f55;
        }

        .result {
            margin-top: 28px;
            padding: 22px 12px;
            border: 1px solid #ff438d44;
            border-radius: 18px;
            background: linear-gradient(145deg, #ff438d12, #ffffff05);
            animation: appear 0.7s ease;
        }

        .big-heart {
            font-size: 45px;
            animation: beat 1.3s infinite;
        }

        .names {
            margin: 10px 0;
            overflow-wrap: anywhere;
            color: #e8d5ed;
        }

        .percentage {
            color: #ff579e;
            font-size: 60px;
            font-weight: 700;
            text-shadow: 0 0 22px #ff247f55;
        }

        .progress {
            height: 8px;
            max-width: 280px;
            margin: 15px auto;
            border-radius: 20px;
            background: #ffffff1c;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            border-radius: 20px;
            background: linear-gradient(90deg, #ff2785, #ff796d);
        }

        .result h2 {
            font-size: 18px;
            margin-top: 12px;
        }

        .message {
            margin-top: 15px;
            color: #ff9dbd;
            font-size: 13px;
        }

        .note {
            margin-top: 12px;
            color: #a9a0bb;
            font-size: 11px;
        }

        footer {
            margin-top: 25px;
            color: #a9a0bb;
            font-size: 12px;
        }

        footer span {
            color: #ff438d;
        }

        @keyframes beat {
            0%, 100% { transform: scale(1); }
            15% { transform: scale(1.12); }
            30% { transform: scale(1); }
            45% { transform: scale(1.08); }
        }

        @keyframes appear {
            from {
                opacity: 0;
                transform: translateY(15px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @media (max-width: 420px) {
            .container {
                padding: 25px 17px;
            }

            h1 {
                font-size: 27px;
            }
        }
    </style>
</head>

<body>
    <div class="container">

        <div class="heart">♥</div>

        <h1>Love <span>Calculator</span></h1>
        <p class="subtitle">Discover your love percentage ❤️</p>

        <form method="POST">
            <label for="boy">♂ Boy's Name</label>
            <input
                type="text"
                id="boy"
                name="boy"
                placeholder="Enter boy's name"
                value="{{ boy }}"
                required
            >

            <label for="girl">♀ Girl's Name</label>
            <input
                type="text"
                id="girl"
                name="girl"
                placeholder="Enter girl's name"
                value="{{ girl }}"
                required
            >

            <button type="submit">♥ Calculate Love</button>
        </form>

        {% if message %}
            <p class="message">{{ message }}</p>
        {% endif %}

        {% if love is not none %}
            <div class="result">
                <div class="big-heart">❤️</div>

                <p class="names">{{ boy }} + {{ girl }}</p>

                <div class="percentage">{{ love }}%</div>

                <div class="progress">
                    <div class="progress-bar"
                         style="width: {{ love }}%;">
                    </div>
                </div>

                <h2>
                    {% if love == 100 %}
                        Perfect Match! 💖
                    {% elif love >= 75 %}
                        Beautiful Connection! 💕
                    {% elif love >= 50 %}
                        Sweet Connection! 💗
                    {% else %}
                        Keep Spreading Love! 💘
                    {% endif %}
                </h2>

                <p class="note">
                    Just for fun — love is more than a percentage!
                </p>
            </div>
        {% endif %}

        <footer>Made with <span>♥</span> for special people</footer>
    </div>
</body>
</html>
"""


# Python Love Calculation
def calculate_love(boy, girl):
    boy = boy.lower().strip()
    girl = girl.lower().strip()

    # Special match: case-insensitive
    if boy == "prabhat" and girl == "preeti":
        return 100

    # Original calculation for other names
    total = 0

    for char in boy + girl:
        if char.isalpha():
            total += ord(char) - ord("a") + 1

    return total % 101


# Flask Route
@app.route("/", methods=["GET", "POST"])
def home():
    boy = ""
    girl = ""
    love = None
    message = ""

    if request.method == "POST":
        boy = request.form.get("boy", "").strip()
        girl = request.form.get("girl", "").strip()

        if not boy or not girl:
            message = "Please enter both names."
        elif not boy.isalpha() or not girl.isalpha():
            message = "Please enter letters only."
        else:
            love = calculate_love(boy, girl)

    return render_template_string(
        HTML,
        boy=boy,
        girl=girl,
        love=love,
        message=message
    )


if __name__ == "__main__":
    print("❤️ Love Calculator is starting...")
    print("Open http://127.0.0.1:5000 in your browser")

    app.run(debug=True)

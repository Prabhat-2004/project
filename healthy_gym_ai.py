
import os
import requests
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Get a free API key from:
# https://fdc.nal.usda.gov/api-key-signup.html
API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
FOOD_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FitBite AI | Smart Food & Fitness</title>

<style>
:root {
    --bg: #101426;
    --panel: #1b2239;
    --panel2: #242d49;
    --text: #f4f7ff;
    --muted: #aab4d0;
    --green: #5df0a5;
    --purple: #a98bff;
    --pink: #ff78b7;
    --orange: #ffb86b;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    background:
        radial-gradient(circle at 10% 0%, #26385c 0, transparent 30%),
        radial-gradient(circle at 100% 10%, #3c2458 0, transparent 25%),
        var(--bg);
    color: var(--text);
    font-family: Arial, sans-serif;
}
button, input, select { font: inherit; }
button { cursor: pointer; }
header {
    padding: 20px 7%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    flex-wrap: wrap;
    border-bottom: 1px solid #ffffff15;
}
.logo { font-size: 25px; font-weight: 900; }
.logo span { color: var(--green); }
.tagline { color: var(--muted); font-size: 13px; margin-top: 5px; }
.status {
    border: 1px solid #5df0a555;
    border-radius: 30px;
    padding: 9px 14px;
    color: var(--green);
    font-size: 12px;
}
main { max-width: 1250px; margin: auto; padding: 28px 20px 50px; }
.hero {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 22px;
    margin-bottom: 25px;
}
.hero-card, .panel {
    background: #1b2239ed;
    border: 1px solid #ffffff12;
    border-radius: 23px;
    padding: 25px;
    box-shadow: 0 12px 40px #00000015;
}
.hero h1 { font-size: clamp(30px, 4vw, 48px); margin: 12px 0; }
.hero h1 span { color: var(--green); }
.hero p, .muted { color: var(--muted); line-height: 1.6; }
.eyebrow { color: var(--green); font-size: 12px; letter-spacing: 2px; font-weight: bold; }
.hero-emoji { font-size: 75px; text-align: center; padding: 10px; }
.btn {
    border: 0;
    border-radius: 12px;
    padding: 12px 16px;
    font-weight: bold;
    background: var(--green);
    color: #10231a;
    transition: .2s;
}
.btn:hover { transform: translateY(-2px); filter: brightness(1.05); }
.btn.secondary { background: var(--panel2); color: var(--text); border: 1px solid #ffffff20; }
.btn.purple { background: var(--purple); color: #201438; }
.btn.pink { background: var(--pink); color: #351127; }
.btn.orange { background: var(--orange); color: #3a2411; }
.btn.small { padding: 9px 12px; font-size: 12px; }
.search-row { display: flex; gap: 10px; margin-top: 18px; }
.search-row input {
    min-width: 0;
    flex: 1;
    border: 1px solid #ffffff20;
    background: #11182b;
    color: white;
    border-radius: 12px;
    padding: 14px;
    outline: none;
}
.search-row input:focus { border-color: var(--green); }
.section-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    margin: 27px 0 15px;
}
.section-title h2 { margin: 0; font-size: 21px; }
.categories { display: flex; flex-wrap: wrap; gap: 9px; }
.category {
    background: #242d49;
    color: white;
    border: 1px solid #ffffff14;
    border-radius: 30px;
    padding: 10px 14px;
    font-size: 13px;
}
.category:hover { border-color: var(--green); color: var(--green); }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 15px; }
.food-card {
    background: var(--panel);
    border: 1px solid #ffffff12;
    border-radius: 18px;
    padding: 18px;
    min-width: 0;
}
.food-card h3 { margin: 10px 0; font-size: 17px; line-height: 1.4; }
.food-icon { font-size: 30px; }
.food-type { font-size: 11px; color: var(--purple); text-transform: uppercase; letter-spacing: 1px; }
.nutrients { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 14px 0; }
.nutrient {
    background: #11182b;
    padding: 10px;
    border-radius: 10px;
}
.nutrient b { display: block; margin-top: 4px; font-size: 17px; }
.nutrient span { color: var(--muted); font-size: 11px; }
.card-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.card-actions button { flex: 1; min-width: 85px; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stat { background: #11182b; padding: 16px; border-radius: 14px; }
.stat span { color: var(--muted); font-size: 12px; }
.stat b { display: block; font-size: 24px; margin-top: 8px; }
.stat:nth-child(1) b { color: var(--orange); }
.stat:nth-child(2) b { color: var(--green); }
.stat:nth-child(3) b { color: var(--purple); }
.stat:nth-child(4) b { color: var(--pink); }
.voice-box { display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
.mic {
    width: 57px; height: 57px; border-radius: 50%;
    border: 0; background: var(--pink); font-size: 25px;
}
.mic.listening { animation: pulse 1s infinite; }
@keyframes pulse {
    50% { box-shadow: 0 0 0 12px #ff78b722; }
}
#message { color: var(--muted); font-size: 13px; margin-top: 12px; white-space: pre-wrap; }
#foodResults { margin-top: 18px; }
#tracker { display: grid; gap: 9px; margin-top: 14px; }
.tracker-item {
    display: flex; justify-content: space-between; align-items: center;
    gap: 10px; background: #11182b; border-radius: 12px; padding: 12px;
}
.tracker-item small { color: var(--muted); }
footer { text-align: center; padding: 25px; color: var(--muted); font-size: 12px; }
.disclaimer { font-size: 12px; color: var(--muted); margin-top: 15px; line-height: 1.5; }
@media (max-width: 800px) {
    .hero { grid-template-columns: 1fr; }
    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 520px) {
    main { padding: 18px 12px 35px; }
    .hero-card, .panel { padding: 18px; }
    .grid { grid-template-columns: 1fr; }
    .stats { grid-template-columns: repeat(2, 1fr); }
    .search-row { flex-wrap: wrap; }
    .search-row input { flex-basis: 100%; }
    .search-row button { flex: 1; }
}
</style>
</head>

<body>
<header>
    <div>
        <div class="logo">🥑 FitBite <span>AI</span></div>
        <div class="tagline">Smart food discovery · Gym nutrition · Daily tracking</div>
    </div>
    <div class="status">● FOOD API CONNECTED</div>
</header>

<main>
    <section class="hero">
        <div class="hero-card">
            <div class="eyebrow">YOUR PERSONAL FOOD COMPANION</div>
            <h1>Eat smart.<br><span>Train stronger.</span></h1>
            <p>Explore healthy meals, gym foods, Indian dishes, snacks, sweets and junk food. Check nutrition and track what you eat.</p>
            <div class="search-row">
                <input id="searchInput" placeholder="Search eggs, oats, pizza, biryani..." />
                <button class="btn" onclick="searchFood()">Search</button>
                <button class="btn secondary" onclick="startVoice()">🎙️</button>
            </div>
            <div id="message">Enter a food name or use the voice assistant.</div>
        </div>
        <div class="hero-card">
            <div class="hero-emoji">🥗 💪 🍕</div>
            <h2>Every food has a place</h2>
            <p>Compare protein, calories, carbohydrates and fat. Choose foods according to your goals, without labelling every food as good or bad.</p>
            <button class="btn purple" onclick="searchCategory('chicken breast')">Explore gym foods →</button>
        </div>
    </section>

    <section class="panel">
        <div class="section-title">
            <h2>🍽️ Explore food categories</h2>
        </div>
        <div class="categories">
            <button class="category" onclick="searchCategory('apple')">🍎 Fruits</button>
            <button class="category" onclick="searchCategory('broccoli')">🥦 Vegetables</button>
            <button class="category" onclick="searchCategory('oats')">🌾 Healthy foods</button>
            <button class="category" onclick="searchCategory('chicken breast')">💪 Gym protein</button>
            <button class="category" onclick="searchCategory('paneer')">🧀 Vegetarian protein</button>
            <button class="category" onclick="searchCategory('biryani')">🍛 Indian foods</button>
            <button class="category" onclick="searchCategory('pizza')">🍕 Junk food</button>
            <button class="category" onclick="searchCategory('potato chips')">🍟 Snacks</button>
            <button class="category" onclick="searchCategory('chocolate')">🍫 Sweets</button>
            <button class="category" onclick="searchCategory('orange juice')">🥤 Drinks</button>
        </div>
    </section>

    <section>
        <div class="section-title">
            <h2>🔎 Food search results</h2>
            <span class="muted" id="resultCount">No results yet</span>
        </div>
        <div id="foodResults" class="grid">
            <div class="food-card">
                <div class="food-icon">🥚</div>
                <h3>Try searching for eggs</h3>
                <p class="muted">See nutrition information from the food database.</p>
            </div>
            <div class="food-card">
                <div class="food-icon">🍕</div>
                <h3>Or search for pizza</h3>
                <p class="muted">Junk food and snacks are included too.</p>
            </div>
            <div class="food-card">
                <div class="food-icon">🥛</div>
                <h3>Track your meals</h3>
                <p class="muted">Add food to your daily nutrition tracker.</p>
            </div>
        </div>
    </section>

    <section class="panel" style="margin-top:28px">
        <div class="section-title">
            <h2>📊 Daily nutrition tracker</h2>
            <button class="btn secondary small" onclick="clearTracker()">Reset day</button>
        </div>
        <div class="stats">
            <div class="stat"><span>Calories (kcal)</span><b id="totalCalories">0</b></div>
            <div class="stat"><span>Protein (g)</span><b id="totalProtein">0</b></div>
            <div class="stat"><span>Carbs (g)</span><b id="totalCarbs">0</b></div>
            <div class="stat"><span>Fat (g)</span><b id="totalFat">0</b></div>
        </div>
        <div id="tracker">
            <p class="muted">Your added foods will appear here.</p>
        </div>
        <p class="disclaimer">Nutrition values are estimates from database entries, usually per 100 g or per listed serving. Check each food description and serving size before tracking. This tracker resets when the page is refreshed.</p>
    </section>

    <section class="panel" style="margin-top:22px">
        <div class="section-title"><h2>🎙️ Voice assistant</h2></div>
        <div class="voice-box">
            <button id="micButton" class="mic" onclick="startVoice()">🎤</button>
            <div>
                <b>Talk to FitBite</b>
                <p class="muted" style="margin:6px 0">Try: “Search pizza”, “Find oats”, or “How many calories have I tracked?”</p>
            </div>
            <button class="btn secondary" onclick="stopSpeaking()">🔇 Stop voice</button>
        </div>
        <div id="voiceStatus" class="muted" style="margin-top:12px">Voice support depends on your browser and microphone permission.</div>
    </section>
</main>

<footer>FitBite AI · Food information powered by USDA FoodData Central</footer>

<script>
let tracker = [];
let currentFoods = [];

const $ = id => document.getElementById(id);

function setMessage(text) {
    $("message").textContent = text;
}

function searchCategory(query) {
    $("searchInput").value = query;
    searchFood(query);
}

async function searchFood(explicitQuery) {
    const query = (explicitQuery || $("searchInput").value).trim();

    if (!query) {
        setMessage("Please enter a food name first.");
        $("searchInput").focus();
        return;
    }

    $("foodResults").innerHTML =
        '<div class="food-card"><p>🔄 Searching the food database...</p></div>';
    setMessage("Searching for: " + query);
    $("resultCount").textContent = "Searching...";

    try {
        const response = await fetch("/api/food?q=" + encodeURIComponent(query));
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Food search failed.");
        }

        currentFoods = data.foods || [];
        renderFoods(currentFoods);

        if (currentFoods.length) {
            setMessage("Found " + currentFoods.length + " results for \"" + query + "\".");
        } else {
            setMessage("No matching foods found. Try a simpler food name, such as egg, rice, apple or pizza.");
        }
    } catch (error) {
        $("foodResults").innerHTML =
            '<div class="food-card"><h3>⚠️ Search failed</h3><p class="muted"></p></div>';
        $("foodResults").querySelector("p").textContent = error.message;
        $("resultCount").textContent = "Search error";
        setMessage("Could not get food data. Check that the Flask server is running.");
    }
}

function safeText(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}

function renderFoods(foods) {
    $("resultCount").textContent = foods.length + " result(s)";

    if (!foods.length) {
        $("foodResults").innerHTML =
            '<div class="food-card"><h3>No food found</h3><p class="muted">Try another keyword.</p></div>';
        return;
    }

    $("foodResults").innerHTML = foods.map((food, index) => `
        <article class="food-card">
            <div class="food-icon">${food.icon || "🍽️"}</div>
            <div class="food-type">${safeText(food.type || "Food database")}</div>
            <h3>${safeText(food.name)}</h3>
            <p class="muted" style="font-size:12px">FoodData Central ID: ${safeText(food.id)}</p>
            <div class="nutrients">
                <div class="nutrient"><span>Calories</span><b>${food.calories} kcal</b></div>
                <div class="nutrient"><span>Protein</span><b>${food.protein} g</b></div>
                <div class="nutrient"><span>Carbs</span><b>${food.carbs} g</b></div>
                <div class="nutrient"><span>Fat</span><b>${food.fat} g</b></div>
            </div>
            <div class="card-actions">
                <button class="btn small" onclick="addFood(${index})">＋ Track food</button>
                <button class="btn secondary small" onclick="speakFood(${index})">🔊 Speak</button>
            </div>
        </article>
    `).join("");
}

function addFood(index) {
    const food = currentFoods[index];
    if (!food) return;

    tracker.push({
        ...food,
        trackId: Date.now() + Math.random()
    });

    updateTracker();
    setMessage("Added " + food.name + " to your tracker.");
}

function removeFood(trackId) {
    tracker = tracker.filter(item => item.trackId !== trackId);
    updateTracker();
}

function clearTracker() {
    tracker = [];
    updateTracker();
    setMessage("Daily tracker cleared.");
}

function updateTracker() {
    const totals = tracker.reduce((sum, food) => {
        sum.calories += Number(food.calories) || 0;
        sum.protein += Number(food.protein) || 0;
        sum.carbs += Number(food.carbs) || 0;
        sum.fat += Number(food.fat) || 0;
        return sum;
    }, {calories: 0, protein: 0, carbs: 0, fat: 0});

    $("totalCalories").textContent = totals.calories.toFixed(1);
    $("totalProtein").textContent = totals.protein.toFixed(1);
    $("totalCarbs").textContent = totals.carbs.toFixed(1);
    $("totalFat").textContent = totals.fat.toFixed(1);

    if (!tracker.length) {
        $("tracker").innerHTML = '<p class="muted">Your added foods will appear here.</p>';
        return;
    }

    $("tracker").innerHTML = tracker.map(food => `
        <div class="tracker-item">
            <div>
                <b>${safeText(food.name)}</b><br>
                <small>${food.calories} kcal · P ${food.protein} g · C ${food.carbs} g · F ${food.fat} g</small>
            </div>
            <button class="btn pink small" onclick="removeFood(${food.trackId})">Remove</button>
        </div>
    `).join("");
}

function speak(text) {
    if (!("speechSynthesis" in window)) {
        $("voiceStatus").textContent = "Speech output is not supported in this browser.";
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
}

function speakFood(index) {
    const food = currentFoods[index];
    if (!food) return;

    speak(`${food.name}. Calories ${food.calories} kilocalories. Protein ${food.protein} grams. Carbohydrates ${food.carbs} grams. Fat ${food.fat} grams.`);
}

function stopSpeaking() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    $("voiceStatus").textContent = "Voice playback stopped.";
}

function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        $("voiceStatus").textContent =
            "Speech recognition is not supported. Try Chrome or Edge and allow microphone access.";
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    $("micButton").classList.add("listening");
    $("voiceStatus").textContent = "Listening... Say a food name or command.";

    recognition.onresult = event => {
        const command = event.results[0][0].transcript.trim();
        $("voiceStatus").textContent = "You said: " + command;
        $("searchInput").value = command;

        const lower = command.toLowerCase();

        if (lower.includes("calories") && (lower.includes("tracked") || lower.includes("total"))) {
            const total = tracker.reduce((sum, food) => sum + (Number(food.calories) || 0), 0);
            speak("Your tracked total is " + total.toFixed(1) + " calories.");
            return;
        }

        if (lower.includes("protein") && (lower.includes("tracked") || lower.includes("total"))) {
            const total = tracker.reduce((sum, food) => sum + (Number(food.protein) || 0), 0);
            speak("Your tracked protein total is " + total.toFixed(1) + " grams.");
            return;
        }

        const cleaned = lower
            .replace(/^(please )?(search for|search|find|look for|show me|look up)\s+/i, "")
            .replace(/[?.!]+$/g, "")
            .trim();

        if (cleaned) {
            $("searchInput").value = cleaned;
            searchFood(cleaned);
        } else {
            speak("Please say the name of a food.");
        }
    };

    recognition.onerror = event => {
        $("voiceStatus").textContent = "Microphone issue: " + event.error +
            ". Check your browser microphone permission.";
    };

    recognition.onend = () => $("micButton").classList.remove("listening");

    try {
        recognition.start();
    } catch (error) {
        $("micButton").classList.remove("listening");
        $("voiceStatus").textContent = "Could not start the microphone. Try again.";
    }
}

$("searchInput").addEventListener("keydown", event => {
    if (event.key === "Enter") searchFood();
});
</script>
</body>
</html>
"""


def get_nutrient(food, target):
    """Return the first matching nutrient value from a USDA food record."""
    for nutrient in food.get("foodNutrients", []):
        name = (
            nutrient.get("nutrientName")
            or nutrient.get("name")
            or ""
        ).lower()

        if target == "calories" and (
            "energy" in name
            and ("kcal" in name or "kilocalorie" in name)
        ):
            return round(float(nutrient.get("value") or 0), 1)

        if target == "protein" and name == "protein":
            return round(float(nutrient.get("value") or 0), 1)

        if target == "carbs" and "carbohydrate" in name:
            return round(float(nutrient.get("value") or 0), 1)

        if target == "fat" and "total lipid" in name:
            return round(float(nutrient.get("value") or 0), 1)

    return 0


def food_icon(name):
    name = name.lower()

    icons = {
        "apple": "🍎", "banana": "🍌", "orange": "🍊",
        "egg": "🥚", "chicken": "🍗", "fish": "🐟",
        "milk": "🥛", "oat": "🥣", "rice": "🍚",
        "pizza": "🍕", "burger": "🍔", "hamburger": "🍔",
        "potato": "🥔", "chip": "🍟", "chocolate": "🍫",
        "salad": "🥗", "broccoli": "🥦", "paneer": "🧀",
        "bread": "🍞", "cheese": "🧀", "yogurt": "🥣",
        "biryani": "🍛", "juice": "🥤", "coffee": "☕",
        "noodle": "🍜", "ice cream": "🍨", "lentil": "🥣",
    }

    for keyword, icon in icons.items():
        if keyword in name:
            return icon

    return "🍽️"


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/api/food")
def food_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please enter a food name."}), 400

    if len(query) > 120:
        return jsonify({"error": "Search term is too long."}), 400

    try:
        response = requests.get(
            FOOD_API_URL,
            params={
                "api_key": API_KEY,
                "query": query,
                "pageSize": 12,
                "dataType": [
                    "Foundation",
                    "SR Legacy",
                    "Branded",
                    "Survey (FNDDS)",
                ],
            },
            timeout=20,
        )

        if response.status_code == 429:
            return jsonify({
                "error": "The API request limit was reached. Try again later or use your own USDA API key."
            }), 429

        response.raise_for_status()
        data = response.json()

        foods = []
        for item in data.get("foods", []):
            name = item.get("description", "Unknown food")
            foods.append({
                "id": item.get("fdcId", ""),
                "name": name,
                "type": item.get("dataType", "Food"),
                "icon": food_icon(name),
                "calories": get_nutrient(item, "calories"),
                "protein": get_nutrient(item, "protein"),
                "carbs": get_nutrient(item, "carbs"),
                "fat": get_nutrient(item, "fat"),
            })

        return jsonify({
            "query": query,
            "count": len(foods),
            "foods": foods,
        })

    except requests.Timeout:
        return jsonify({
            "error": "The food API took too long to respond. Please try again."
        }), 504

    except requests.RequestException as error:
        app.logger.warning("USDA API request failed: %s", error)
        return jsonify({
            "error": "Could not connect to the USDA food database. Check your internet and API key."
        }), 502

    except (ValueError, TypeError) as error:
        app.logger.warning("Could not process USDA response: %s", error)
        return jsonify({
            "error": "The food database returned unexpected data. Please try again."
        }), 502


if __name__ == "__main__":
    print("\n🥑 FitBite AI is starting...")
    print("Open this address in your browser: http://127.0.0.1:5000")
    print("Press CTRL+C in PowerShell to stop the server.\n")
    app.run(host="127.0.0.1", port=5000, debug=True)

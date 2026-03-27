from flask import Flask, render_template, request, redirect, session
import pickle
import pandas as pd
import sqlite3
import requests
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)
app.secret_key = "my_secret_key_123"  # Change for production

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
with get_db() as conn:
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        N REAL, P REAL, K REAL, ph REAL,
        temperature REAL, humidity REAL, rainfall REAL,
        soil TEXT, climate TEXT,
        predicted_crop TEXT, top3 TEXT
    )""")
    conn.commit()

# ---------------- MODEL ----------------
model = pickle.load(open("rfc.pkl","rb"))
model_columns = pickle.load(open("model_columns.pkl","rb"))
le = pickle.load(open("label_encoder.pkl","rb"))
labels = le.classes_.tolist()

# ---------------- CROP INFO ----------------
crop_info = {
    "rice": {"soil":"Loamy", "season":"Kharif", "yield":"3.5 t/ha"},
    "maize": {"soil":"Loamy", "season":"Rabi", "yield":"4 t/ha"},
    "wheat": {"soil":"Clayey", "season":"Rabi", "yield":"3.2 t/ha"},
    "mango": {"soil":"Loamy", "season":"Summer", "yield":"10 t/ha"},
}

# ---------------- WEATHER ----------------
def get_weather(city):
    API_KEY = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()
    if res.get("main"):
        return {
            "temperature": res["main"]["temp"],
            "humidity": res["main"]["humidity"],
            "rainfall": res.get("rain", {}).get("1h", 0)
        }
    return None

# ---------------- SAFE FLOAT ----------------
def safe_float(value, default=0):
    try:
        return float(value)
    except:
        return default

# ---------------- LOGIN REQUIRED ----------------
def login_required():
    return "user_id" in session

# ---------------- ROUTES ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        try:
            conn.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))
            conn.commit()
            return redirect("/login")
        except:
            return "User already exists!"
    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                            (username,password)).fetchone()
        if user:
            session["user_id"] = user["id"]
            return redirect("/")
        else:
            return "Invalid credentials"
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/", methods=["GET","POST"])
def index():
    if not login_required():
        return redirect("/login")

    prediction_text = None
    top3_text = []
    graph_html = None
    crop_detail = None
    form_data = {}

    if request.method == "POST":
        try:
            form_data = request.form.to_dict()
            N = safe_float(form_data.get('N'))
            P = safe_float(form_data.get('P'))
            K = safe_float(form_data.get('K'))
            ph = safe_float(form_data.get('ph'))
            soil = form_data.get('soil', '')
            climate = form_data.get('climate', '')
            city = form_data.get('city')

            # Weather values
            if city:
                weather = get_weather(city)
                if weather:
                    temperature = weather['temperature']
                    humidity = weather['humidity']
                    rainfall = weather['rainfall']
                else:
                    temperature = safe_float(form_data.get('temperature'), 25)
                    humidity = safe_float(form_data.get('humidity'), 50)
                    rainfall = safe_float(form_data.get('rainfall'), 100)
            else:
                temperature = safe_float(form_data.get('temperature'), 25)
                humidity = safe_float(form_data.get('humidity'), 50)
                rainfall = safe_float(form_data.get('rainfall'), 100)

            # Prepare DataFrame
            data = pd.DataFrame([[N,P,K,ph,temperature,humidity,rainfall,soil,climate]],
                                columns=['N','P','K','ph','temperature','humidity','rainfall','soil','climate'])
            data_encoded = pd.get_dummies(data)
            data_encoded = data_encoded.reindex(columns=model_columns, fill_value=0)

            # Prediction & Top3
            probs = model.predict_proba(data_encoded)[0]
            top3_idx = probs.argsort()[-3:][::-1]
            top3_text = [f"{labels[i]} ({probs[i]*100:.1f}%)" for i in top3_idx]
            predicted_crop = labels[top3_idx[0]]
            prediction_text = f"🌾 Recommended Crop: {predicted_crop}"
            crop_detail = crop_info.get(predicted_crop, {})

            # Save history
            conn = get_db()
            conn.execute("""INSERT INTO history(user_id,N,P,K,ph,temperature,humidity,rainfall,
                            soil,climate,predicted_crop,top3)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (session["user_id"],N,P,K,ph,temperature,humidity,rainfall,
                          soil,climate,predicted_crop,",".join(top3_text)))
            conn.commit()

            # Graph
            fig = go.Figure([go.Bar(
                x=[labels[i] for i in top3_idx],
                y=[probs[i]*100 for i in top3_idx]
            )])
            graph_html = pio.to_html(fig, full_html=False)

        except Exception as e:
            prediction_text = f"⚠️ Error: {str(e)}"

    return render_template("index.html",
                           prediction_text=prediction_text,
                           top3_text=top3_text,
                           graph_html=graph_html,
                           crop_detail=crop_detail,
                           form_data=form_data)


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")
    conn = get_db()
    history = conn.execute("SELECT * FROM history WHERE user_id=?",
                           (session["user_id"],)).fetchall()
    return render_template("dashboard.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)
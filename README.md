# 🌾 Crop Yield Prediction Using Soil & Weather Data

## **Project Overview**
This project is a **web-based crop yield prediction system** built using **Python and Flask**. It predicts the most suitable crop based on **soil properties** (N, P, K, pH) and **weather conditions** (temperature, humidity, rainfall). Users can log in, track prediction history, view crop details, and interact with visual graphs.

---

## **Features**
- **Crop Prediction:** Enter soil nutrients and weather data to predict the best crop.
- **User Authentication:** Secure login and registration with hashed passwords.
- **Prediction History:** View all previous predictions in a responsive table.
- **Graphs & Visualizations:** Interactive charts for historical trends.
- **Crop Details:** Displays soil type, season, and average yield.
- **Responsive Design:** Mobile-friendly and desktop-compatible interface.
- **Tooltips & Help Icons:** Enhanced user experience and guidance.

---

## **Technologies Used**
- **Backend:** Python, Flask, SQLite, scikit-learn
- **Frontend:** HTML, CSS, JavaScript
- **Data Visualization:** Plotly.js or Chart.js
- **Machine Learning:** Random Forest Classifier (pre-trained)

---
## **Structure of the files**

├── app.py                  # Main Flask app
├── database.db             # SQLite database
├── templates/              # HTML templates
│   ├── index.html
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
├── static/                 # CSS, JS, images
│   ├── style.css
│   ├── script.js
│   └── background.webp
├── rfc.pkl                 # Pre-trained Random Forest model
├── model_columns.pkl       # Columns for one-hot encoding
└── README.md

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import random

app = Flask(__name__)
CORS(app)

# Load dataset
crop_data = pd.read_csv("crop_data.csv")

users = {}

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "User")

    if email in users:
        return jsonify({"error": "User already exists"}), 400

    users[email] = {"password": password, "name": name}
    return jsonify({"message": "Signup successful", "name": name})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = users.get(email)
    if user and user["password"] == password:
        return jsonify({"message": "Login successful", "name": user["name"]})
    elif not user:
        # Auto-create account if user doesn't exist
        username = email.split("@")[0]  # take part before @ as name
        users[email] = {"password": password, "name": username}
        return jsonify({"message": "Account created & logged in", "name": username})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json  

    crop = data.get("crop")
    soil = data.get("soil")
    size = float(data.get("size", 1))
    water = data.get("water")
    fertilizer = data.get("fertilizer")
    pest = data.get("pest")
    weather = data.get("weather")

    # Get base info from dataset
    crop_row = crop_data[crop_data["Crop"].str.lower() == crop.lower()]
    if crop_row.empty:
        return jsonify({"error": "Crop not found in dataset"}), 400

    base_yield = float(crop_row["BaseYield"].values[0])
    best_soil = crop_row["BestSoil"].values[0]
    recommended_fert = crop_row["RecommendedFertilizer"].values[0]
    water_need = crop_row["WaterNeed"].values[0]
    pest_resistance = crop_row["PestResistance"].values[0]

    yield_per_acre = base_yield

    # Soil effect
    if soil == best_soil:
        yield_per_acre += 0.5
    elif soil in ["Sandy", "Red"]:
        yield_per_acre -= 0.5

    # Water availability effect
    if water == "Drip Irrigation":
        yield_per_acre += 0.5
    elif water == "Rain-fed" and water_need == "High":
        yield_per_acre -= 0.8
    elif water == "Rain-fed":
        yield_per_acre -= 0.3

    # Fertilizer effect
    if fertilizer == "Yes":
        yield_per_acre += 0.4
    else:
        yield_per_acre -= 0.4

    # Pest effect
    if pest == "Low":
        yield_per_acre -= 0.2
    elif pest == "Medium":
        yield_per_acre -= 0.5
    elif pest == "Severe":
        yield_per_acre -= 1.0

    # Weather effect
    if weather == "Sunny":
        yield_per_acre += 0.3
    elif weather == "Rainy":
        yield_per_acre += 0.2
    elif weather == "Cloudy":
        yield_per_acre -= 0.2

    # Final results
    total_yield = max(0.5, round(yield_per_acre * size, 2))
    per_acre_yield = max(0.5, round(yield_per_acre, 2))
    confidence = random.randint(75, 95)

    # Advice list
    advice_points = []
    if soil != best_soil:
        advice_points.append(f"Best soil for {crop} is {best_soil}, consider improving soil quality.")
    if water == "Rain-fed" and water_need == "High":
        advice_points.append(f"{crop} requires high water, consider supplementary irrigation.")
    if fertilizer == "No":
        advice_points.append(f"Use {recommended_fert} for better yield.")
    if pest in ["Medium", "Severe"]:
        advice_points.append("Apply pest-resistant seeds and use bio-pesticides.")
    if not advice_points:
        advice_points.append("Your farming conditions look optimal!")

    result = {
        "prediction": f"Predicted Yield: {per_acre_yield} tons/acre × {size} acres = {total_yield} tons",
        "confidence": f"Confidence Level: ~{confidence}%",
        "fertilizer_suggestion": f"Recommended Fertilizer: {recommended_fert}",
        "pest_risk": f"Pest Risk Level: {pest}",
        "advice": advice_points
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

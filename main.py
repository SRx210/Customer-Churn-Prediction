from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os

app = Flask(__name__)

MODEL_PATH = 'exports/customer_churn_model.pkl'
ENCODER_PATH = 'exports/encoders.pkl'

loaded_model = None
encoders = None

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        with open(MODEL_PATH, 'rb') as f:
            loaded_model = pickle.load(f)
        with open(ENCODER_PATH, 'rb') as f:
            encoders = pickle.load(f)
        print("Model and encoders loaded successfully.")
    else:
        print("Warning: Model or encoders not found. Run train.py first.")
except Exception as e:
    print(f"Error loading model/encoders: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": loaded_model is not None}), 200

@app.route('/predict', methods=['POST'])
def predict():
    if not loaded_model or not encoders:
        return jsonify({"error": "Model not loaded on server."}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        if isinstance(data, dict):
             input_df = pd.DataFrame([data])
        elif isinstance(data, list):
             input_df = pd.DataFrame(data)
        else:
            return jsonify({"error": "Input data should be JSON object or list of JSON objects."}), 400

        processed_df = input_df.copy()

        for column, encoder in encoders.items():
            if column in processed_df.columns:
                processed_df[column] = processed_df[column].astype(str)
                try:
                    processed_df[column] = encoder.transform(processed_df[column])
                except ValueError as e:
                    return jsonify({"error": f"Unseen label in column {column}. Error: {str(e)}"}), 400

        if hasattr(loaded_model, 'feature_names_in_'):
            missing_cols = set(loaded_model.feature_names_in_) - set(processed_df.columns)
            if missing_cols:
                 return jsonify({"error": f"Missing columns in input: {missing_cols}"}), 400
            processed_df = processed_df[loaded_model.feature_names_in_]

        predictions = loaded_model.predict(processed_df)
        probabilities = loaded_model.predict_proba(processed_df)
        
        results = []
        for i in range(len(predictions)):
             results.append({
                 "prediction": int(predictions[i]),
                 "churn_status": "Yes" if int(predictions[i]) == 1 else "No",
                 "probability_no_churn": float(probabilities[i][0]),
                 "probability_churn": float(probabilities[i][1])
             })
             
        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

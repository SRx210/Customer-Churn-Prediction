from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_PATH = 'exports/customer_churn_model.pkl'
ENCODER_PATH = 'exports/encoders.pkl'

loaded_model = None
encoders = None

def load_artifacts():
    global loaded_model, encoders
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            with open(MODEL_PATH, 'rb') as f:
                loaded_model = pickle.load(f)
            with open(ENCODER_PATH, 'rb') as f:
                encoders = pickle.load(f)
            logger.info("Model and encoders loaded successfully.")
        else:
            logger.warning("Model or encoders not found. Run train.py first.")
    except Exception as e:
        logger.error(f"Error loading model/encoders: {e}")

load_artifacts()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": loaded_model is not None,
        "encoders_loaded": encoders is not None
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    if loaded_model is None or encoders is None:
        return jsonify({"error": "Model not loaded on server."}), 500

    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({"error": "Invalid or missing JSON body."}), 400

        if isinstance(data, dict):
            input_df = pd.DataFrame([data])
        elif isinstance(data, list):
            if len(data) == 0:
                return jsonify({"error": "Input list is empty."}), 400
            input_df = pd.DataFrame(data)
        else:
            return jsonify({"error": "Input must be a JSON object or list of JSON objects."}), 400

        processed_df = input_df.copy()

        for column, encoder in encoders.items():
            if column in processed_df.columns:
                processed_df[column] = processed_df[column].astype(str)
                try:
                    processed_df[column] = encoder.transform(processed_df[column])
                except ValueError as e:
                    return jsonify({"error": f"Unseen label in column '{column}': {str(e)}"}), 400

        if hasattr(loaded_model, 'feature_names_in_'):
            missing_cols = set(loaded_model.feature_names_in_) - set(processed_df.columns)
            if missing_cols:
                return jsonify({"error": f"Missing columns in input: {sorted(missing_cols)}"}), 400
            processed_df = processed_df[loaded_model.feature_names_in_]

        predictions = loaded_model.predict(processed_df)
        probabilities = loaded_model.predict_proba(processed_df)

        results = [
            {
                "prediction": int(pred),
                "churn_status": "Yes" if int(pred) == 1 else "No",
                "probability_no_churn": round(float(prob[0]), 4),
                "probability_churn": round(float(prob[1]), 4)
            }
            for pred, prob in zip(predictions, probabilities)
        ]

        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
"""
Flask API of the SMS Spam detection model model.
"""
import os
import requests
import joblib
from flask import Flask, jsonify, request, Response
from flasgger import Swagger
import pandas as pd
import os
from text_preprocessing import prepare, _extract_message_len, _text_process
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

SMS_REQUESTS_TOTAL = Counter(
    "sms_requests_total",
    "Total number of SMS classification requests",
    ["result", "source", "model"],
)

SMS_REQUESTS_IN_FLIGHT = Gauge(
    "sms_requests_in_flight",
    "Number of SMS classification requests currently being processed",
)

SMS_REQUEST_LATENCY_SECONDS = Histogram(
    "sms_request_latency_seconds",
    "Latency of SMS classification requests in seconds",
    ["model"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
)

app = Flask(__name__)
swagger = Swagger(app)

MODEL_PATH = os.getenv('MODEL_PATH', '/models/model.joblib')
MODEL_URL = os.getenv('MODEL_URL')


def ensure_model_exists():
    """Ensure model exists, else download if missing"""
    if not os.path.exists(MODEL_PATH):
        if MODEL_URL:
            print(f"Downloading model from {MODEL_URL}")
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            response = requests.get(MODEL_URL)
            with open(MODEL_PATH, 'wb') as f:
                f.write(response.content)
            print("Model downloaded successfully")
        else:
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH} and no MODEL_URL provided. Please check.")


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """

    start_time = time.time()
    SMS_REQUESTS_IN_FLIGHT.inc()

    try:
        input_data = request.get_json()
        sms = input_data.get('sms')
        processed_sms = prepare(sms)
        model = joblib.load(MODEL_PATH)
        prediction = model.predict(processed_sms)[0]

        res = {
            "result": prediction,
            "classifier": "decision tree",
            "sms": sms
        }

        SMS_REQUESTS_TOTAL.labels(
            result=prediction,
            source="ui",
            model="decision_tree",
        ).inc()

        duration = time.time() - start_time
        SMS_REQUEST_LATENCY_SECONDS.labels(model="decision_tree").observe(duration)

        print(res)
        return jsonify(res)

    finally:
        SMS_REQUESTS_IN_FLIGHT.dec()

@app.route("/metrics")
def metrics():
    """
    Expose Prometheus metrics.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    # Check for model on startup
    ensure_model_exists()
    #clf = joblib.load('output/model.joblib')
    port = int(os.environ.get("MODEL_PORT", 8081))
    app.run(host="0.0.0.0", port=port, debug=True)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)

FLouCI_API_URL = 'https://developers.flouci.com/api/generate_payment'
FLouCI_APP_TOKEN = "c6ae6458-aeca-40d5-939d-cae10b8e53b4"
FLouCI_APP_SECRET = "294050e7-412c-421a-974e-7b90e62d1b7a"
payment_data_store = {}

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        print("Received data:", data)

        if not all(k in data for k in ["name", "email", "amount", "service"]):
            return jsonify({"error": "Missing required fields"}), 400

        payload = {
            "app_token": FLouCI_APP_TOKEN,
            "app_secret": FLouCI_APP_SECRET,
            "amount": int(data['amount']) * 1000,
            "accept_card": True,
            "session_timeout_secs": 1200,
            "success_link": "http://localhost:3000/success",
            "fail_link": "http://localhost:3000/failure",
            "developer_tracking_id": "c5ex5-7z1-Jgf67-34recr-7uio"
        }

        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(FLouCI_API_URL, headers=headers, data=json.dumps(payload))
        print("Flouci API response:", response.status_code, response.text)

        if response.status_code == 200:
            payment_url = response.json().get('result', {}).get('link')
            payment_data_store[data['email']] = data 
            return jsonify({"paymentUrl": payment_url}), 200
        else:
            return jsonify({"error": "Failed to create payment", "message": response.text}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/get-payment-data', methods=['GET'])
def get_payment_data():
    try:
        email = request.args.get('email')
        if email:
            if email in payment_data_store:
                return jsonify(payment_data_store[email]), 200
            else:
                return jsonify({"error": "Payment data not found for this email"}), 404
        else:
            return jsonify(payment_data_store), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



if __name__ == '__main__':
    app.run(debug=True)

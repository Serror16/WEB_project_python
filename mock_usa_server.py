from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/mock-usa/submit", methods=["POST"])
def submit():
    body = request.get_json(silent=True) or {}
    
    print("--- [MOCK USA] НОВЫЙ ОТЧЕТ ---")
    print(f"SSN: {body.get('ssn')}")
    print(f"Income: ${body.get('income_usd')}")
    print(f"Year: {body.get('tax_year')}")
    print(f"Request ID: {body.get('request_id')}")
    print("------------------------------")
    
    return jsonify({"message": "Tax return accepted by mock IRS"})

@app.route("/mock-usa/status/<string:report_id>", methods=["GET"])
def get_status(report_id):
    print(f"[MOCK USA] Запрошен статус для Request ID: {report_id}")
    
    return jsonify({
        "state": "COMPLETED", 
        "report_id": report_id,
        "processing_time_ms": 142
    })

@app.route("/mock-usa/validate", methods=["POST"])
def validate():
    body = request.get_json(silent=True) or {}
    print(f"[MOCK USA] Валидация данных для SSN: {body.get('ssn')}")
    
    return jsonify({
        "valid": True,
        "warnings": []
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002)
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

@app.route("/mock-russia/submit", methods=["POST"])
def submit():
    body = request.get_data()
    print(f"[MOCK] Получен отчет (XML):\n{body.decode('utf-8')}")
    return Response(
        response="<Response><Status>Success</Status></Response>", 
        mimetype="application/xml"
    )

@app.route("/mock-russia/status/<string:report_id>", methods=["GET"])
def get_status(report_id):
    print(f"[MOCK] Проверка статуса для ID: {report_id}")
    return jsonify({"status": "SUCCESS", "external_id": report_id})

@app.route("/mock-russia/validate", methods=["POST"])
def validate():
    print("[MOCK] Запрос на валидацию получен")
    return jsonify({"is_valid": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)
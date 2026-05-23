from tax_gateway.app import create_app

app = create_app()

if __name__ == "__main__":
    # Flask использует встроенный сервер для разработки (вместо Uvicorn)
    app.run(host="127.0.0.1", port=8000, debug=True)
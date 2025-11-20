from config import app
from routes.health import health_bp
from routes.chat import chat_bp
from routes.chat_code import chat_code_bp
from routes.codebleu import codebleu_bp
from routes.stream import stream_bp

app.register_blueprint(health_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(chat_code_bp)
app.register_blueprint(codebleu_bp)
app.register_blueprint(stream_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

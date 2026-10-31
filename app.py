
from flask import Flask, render_template

from routes.monitoring_routes import monitoring
from database.db import initialize_database

app = Flask(__name__)

initialize_database()

app.register_blueprint(monitoring)


@app.route("/")
def home():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

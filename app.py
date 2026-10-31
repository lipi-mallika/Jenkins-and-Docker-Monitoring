
from flask import Flask, render_template

from routes.monitoring_routes import monitoring
from database.db import initialize_database

app = Flask(__name__)

# Create database tables when the application starts
initialize_database()

# Register monitoring routes
app.register_blueprint(monitoring)


@app.route("/")
def home():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

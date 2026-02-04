from flask import Flask, render_template
from flask_cors import CORS

# DB Initialization
from database.db import init_db

# Blueprints
from routes.admin_routes import admin_bp
from routes.simulate_routes import simulate_bp
from routes.analytics_routes import analytics_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Initialize database
    init_db(app)

    # -----------------------------
    # Register API Blueprints
    # -----------------------------
    app.register_blueprint(admin_bp)
    app.register_blueprint(simulate_bp)
    app.register_blueprint(analytics_bp)

    # -----------------------------
    # Frontend Routes (UI)
    # -----------------------------

    @app.route("/")
    def index():
        return render_template("index.html", title="Infection Simulator")

    @app.route("/persons")
    def persons_page():
        return render_template("persons.html", title="Manage Persons")

    @app.route("/contacts")
    def contacts_page():
        return render_template("contacts.html", title="Manage Contacts")

    @app.route("/simulate-ui")
    def simulate_page():
        return render_template("simulate.html", title="Run Simulation")

    @app.route("/results/<int:sim_id>")
    def results_page(sim_id):
        return render_template("results.html", title="Simulation Results", sim_id=sim_id)

    @app.route("/analytics-ui")
    def analytics_page():
        return render_template("analytics.html", title="Analytics Dashboard")
    
    @app.route("/graph")
    def graph_page():
        return render_template("graph.html", title="Graph Visualization")
    

    @app.route("/upload-persons")
    def upload_persons_page():
        return render_template("upload_persons.html")
    @app.route("/upload-contacts")
    def upload_contacts_page():
        return render_template("upload_contacts.html")


    

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

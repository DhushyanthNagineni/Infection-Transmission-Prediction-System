from flask import Blueprint, request, jsonify
from services.graph_engine import GraphEngine

analytics_bp = Blueprint("analytics", __name__)
engine = GraphEngine()

@analytics_bp.route("/risk", methods=["POST"])
def risk():
    data = request.json
    person_id = data["person_id"]
    infection_tree = data["infection_tree"]

    result = engine.compute_risk_probability(person_id, infection_tree)

    return jsonify(result)

@analytics_bp.route("/analytics/centrality", methods=["GET"])
def centrality():
    engine.build_graph_from_db()
    scores = engine.centrality_scores()

    return jsonify({"centrality": scores})



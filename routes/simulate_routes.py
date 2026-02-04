from flask import Blueprint, request, jsonify
from services.graph_engine import GraphEngine
from database.models import SimulationLog, SimulationResult, InfectionTree
from database.db import db

simulate_bp = Blueprint("simulate", __name__)
engine = GraphEngine()

@simulate_bp.route("/simulate", methods=["POST"])
def simulate():
    data = request.json

    patient_zero = data["patient_zero_id"]
    p = data["infection_probability"]
    days = data["days"]

    # 1. CREATE LOG ENTRY
    log = SimulationLog(
        patient_zero_id=patient_zero,
        infection_probability=p,
        days=days
    )
    db.session.add(log)
    db.session.commit()

    # 2. Build graph
    engine.build_graph_from_db()

    # 3. Run simulation
    daywise, tree_map = engine.simulate_infection(
        patient_zero, p, days
    )

    # 4. Save daily results
    for d in daywise:
        result = SimulationResult(
            simulation_id=log.id,
            day=d["day"],
            infected_people=d["infected"],
            newly_infected=d["newly_infected"]
        )
        db.session.add(result)

    # 5. Save infection tree
    for infected, (infector, day) in tree_map.items():
        tree = InfectionTree(
            simulation_id=log.id,
            infected_id=infected,
            infected_by_id=infector,
            day_infected=day
        )
        db.session.add(tree)

    db.session.commit()

    return jsonify({
        "status": "success",
        "simulation_id": log.id
    })

@simulate_bp.route("/simulation/<int:sim_id>/results", methods=["GET"])
def get_sim_results(sim_id):
    results = SimulationResult.query.filter_by(simulation_id=sim_id).all()

    return jsonify({
        "simulation_id": sim_id,
        "results": [
            {
                "day": r.day,
                "infected": r.infected_people,
                "newly_infected": r.newly_infected
            }
            for r in results
        ]
    })

@simulate_bp.route("/simulation/<int:sim_id>/tree", methods=["GET"])
def get_tree(sim_id):
    tree = InfectionTree.query.filter_by(simulation_id=sim_id).all()

    return jsonify({
        "simulation_id": sim_id,
        "tree": [
            {
                "infected": t.infected_id,
                "by": t.infected_by_id,
                "day": t.day_infected
            }
            for t in tree
        ]
    })

@simulate_bp.route("/simulation/<int:sim_id>/predict", methods=["GET"])
def get_prediction(sim_id):
    results = SimulationResult.query.filter_by(simulation_id=sim_id).all()

    # convert to correct format
    daywise = [
        {"day": r.day, "infected": r.infected_people}
        for r in results
    ]

    predictions = engine.compute_recurrence_prediction(daywise)

    return jsonify({"prediction": predictions})

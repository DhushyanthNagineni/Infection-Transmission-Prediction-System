from database.db import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON


# -----------------------------------------------
# PERSON TABLE
# -----------------------------------------------
class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)
    location = db.Column(db.String)
    role = db.Column(db.String)

    def __repr__(self):
        return f"<Person {self.name}>"


# -----------------------------------------------
# CONTACT TABLE  (Edges of graph)
# -----------------------------------------------
class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    person1_id = db.Column(db.Integer, db.ForeignKey("persons.id"), nullable=False)
    person2_id = db.Column(db.Integer, db.ForeignKey("persons.id"), nullable=False)

    contact_frequency = db.Column(db.Integer, default=1)
    contact_type = db.Column(db.String)
    weight = db.Column(db.Float, default=1.0)

    # relationships
    person1 = db.relationship("Person", foreign_keys=[person1_id])
    person2 = db.relationship("Person", foreign_keys=[person2_id])

    def __repr__(self):
        return f"<Contact {self.person1_id} - {self.person2_id}>"


# -----------------------------------------------
# SIMULATION LOG TABLE
# -----------------------------------------------
class SimulationLog(db.Model):
    __tablename__ = "simulation_logs"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient_zero_id = db.Column(db.Integer, db.ForeignKey("persons.id"))
    infection_probability = db.Column(db.Float)
    days = db.Column(db.Integer)

    patient_zero = db.relationship("Person")

    def __repr__(self):
        return f"<SimulationLog {self.id}>"


# -----------------------------------------------
# SIMULATION RESULT FOR EACH DAY
# -----------------------------------------------
class SimulationResult(db.Model):
    __tablename__ = "simulation_results"

    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(
        db.Integer, db.ForeignKey("simulation_logs.id"), nullable=False
    )
    day = db.Column(db.Integer, nullable=False)

    infected_people = db.Column(JSON)       # stores array of IDs
    newly_infected = db.Column(JSON)        # stores array of IDs

    simulation = db.relationship("SimulationLog")

    def __repr__(self):
        return f"<SimulationResult Simulation={self.simulation_id} Day={self.day}>"


# -----------------------------------------------
# OPTIONAL: INFECTION TREE TABLE
# -----------------------------------------------
class InfectionTree(db.Model):
    __tablename__ = "infection_tree"

    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey("simulation_logs.id"))
    infected_id = db.Column(db.Integer, db.ForeignKey("persons.id"))
    infected_by_id = db.Column(db.Integer, db.ForeignKey("persons.id"))
    day_infected = db.Column(db.Integer)

    simulation = db.relationship("SimulationLog")
    infected = db.relationship("Person", foreign_keys=[infected_id])
    infected_by = db.relationship("Person", foreign_keys=[infected_by_id])

    def __repr__(self):
        return f"<InfectionTree infected={self.infected_id}>"


# -----------------------------------------------
# OPTIONAL: PROBABILITY REPORT TABLE
# -----------------------------------------------
class ProbabilityReport(db.Model):
    __tablename__ = "probability_reports"

    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey("simulation_logs.id"))
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"))

    safe_probability = db.Column(db.Float)
    risk_score = db.Column(db.Float)

    simulation = db.relationship("SimulationLog")
    person = db.relationship("Person")

    def __repr__(self):
        return f"<ProbabilityReport person={self.person_id}>"

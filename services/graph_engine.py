import random
from collections import defaultdict, deque
import numpy as np

from database.db import db
from database.models import Person, Contact, SimulationLog, SimulationResult, InfectionTree

class GraphEngine:
    def __init__(self):
        self.graph = defaultdict(list)
        self.weights = {}
    

    def build_graph_from_db(self):
        self.graph.clear()
        self.weights.clear()

        contacts = Contact.query.all()

        for c in contacts:
            # undirected edge
            self.graph[c.person1_id].append(c.person2_id)
            self.graph[c.person2_id].append(c.person1_id)

            # store edge weight
            self.weights[(c.person1_id, c.person2_id)] = c.weight
            self.weights[(c.person2_id, c.person1_id)] = c.weight

        return self.graph
    def simulate_infection(self, patient_zero, infection_probability, days):
        infected_overall = set()
        infected_today = set([patient_zero])

        infected_overall.add(patient_zero)

        daywise_results = []           # [{"day":1, "infected":[...]}]
        infection_tree_map = {}        # {node: (infected_by, day)}

        # Day 0 (initial)
        daywise_results.append({
            "day": 0,
            "infected": [patient_zero],
            "newly_infected": [patient_zero]
        })
        infection_tree_map[patient_zero] = (None, 0)

        # simulation loop
        for day in range(1, days + 1):
            new_infected = []

            for person in infected_today:
                for neighbor in self.graph[person]:

                    if neighbor not in infected_overall:
                        # calculate weighted infection probability
                        weight = self.weights.get((person, neighbor), 1.0)
                        prob = infection_probability * weight

                        # random infection event
                        if random.random() < prob:
                            new_infected.append(neighbor)
                            infected_overall.add(neighbor)
                            infection_tree_map[neighbor] = (person, day)

            infected_today = set(new_infected)

            daywise_results.append({
                "day": day,
                "infected": list(infected_overall),
                "newly_infected": list(infected_today)
            })

            # early stop if spread ends
            if len(infected_today) == 0:
                break

        return daywise_results, infection_tree_map
    def generate_infection_tree(self, infection_tree_map):
        tree_list = []

        for infected, (infector, day) in infection_tree_map.items():
            tree_list.append({
                "infected": infected,
                "by": infector,
                "day": day
            })

        return tree_list
    def compute_recurrence_prediction(self, daily_infections, future_days=5):
        infected_counts = [len(day["infected"]) for day in daily_infections]

        if len(infected_counts) < 2:
            return []

        # compute average growth ratio
        ratios = []
        for i in range(1, len(infected_counts)):
            if infected_counts[i-1] > 0:
                ratios.append(infected_counts[i] / infected_counts[i-1])

        r = np.mean(ratios) if len(ratios) > 0 else 1.0

        predictions = []
        last_value = infected_counts[-1]

        for i in range(1, future_days + 1):
            last_value = int(last_value * r)
            predictions.append({
                "day": len(infected_counts) - 1 + i,
                "predicted_infected": last_value
            })

        return predictions
    def compute_risk_probability(self, person_id, infection_tree_map):
        infected_neighbors = []

        # find neighbors who are infected
        for neighbor in self.graph[person_id]:
            if neighbor in infection_tree_map:
                weight = self.weights.get((neighbor, person_id), 1.0)
                infected_neighbors.append(weight)

        if len(infected_neighbors) == 0:
            return {
                "safe_probability": 1.0,
                "infection_risk": 0.0
            }

        # basic inclusion–exclusion
        safe_prob = 1.0
        for w in infected_neighbors:
            safe_prob *= (1 - w)

        return {
            "safe_probability": round(safe_prob, 3),
            "infection_risk": round(1 - safe_prob, 3)
        }
    def centrality_scores(self):
        centrality = {}

        for node, neighbors in self.graph.items():
            centrality[node] = len(neighbors)

        sorted_list = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"person_id": p, "degree": d}
            for p, d in sorted_list
        ]

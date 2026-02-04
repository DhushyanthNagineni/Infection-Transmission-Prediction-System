from flask import Blueprint, request, jsonify
from database.models import Person, Contact
from database.db import db
import csv

admin_bp = Blueprint("admin", __name__)


# ------------------------------------------
# ADD PERSON
# ------------------------------------------
@admin_bp.route("/admin/person/add", methods=["POST"])
def add_person():
    data = request.json

    person = Person(
        name=data.get("name"),
        age=data.get("age"),
        gender=data.get("gender"),
        location=data.get("location"),
        role=data.get("role")
    )

    db.session.add(person)
    db.session.commit()

    return jsonify({"status": "success", "person_id": person.id})

@admin_bp.route("/admin/contact/add", methods=["POST"])
def add_contact():
    data = request.json
    print("Received JSON:", data)  # DEBUG PRINT

    contact = Contact(
        person1_id=data["person1_id"],
        person2_id=data["person2_id"],
        contact_frequency=data.get("contact_frequency", 1),
        contact_type=data.get("contact_type", "normal"),
        weight=data.get("weight", 1.0)
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify({"status": "success", "contact_id": contact.id})


@admin_bp.route("/admin/person/list", methods=["GET"])
def list_persons():
    persons = Person.query.all()

    return jsonify({
        "persons": [
            {"id": p.id, "name": p.name, "location": p.location}
            for p in persons
        ]
    })

@admin_bp.route("/admin/contact/list", methods=["GET"])
def list_contacts():
    contacts = Contact.query.all()

    return jsonify({
        "contacts": [
            {
                "id": c.id,
                "person1_id": c.person1_id,
                "person2_id": c.person2_id,
                "weight": c.weight
            }
            for c in contacts
        ]
    })




@admin_bp.route("/admin/person/upload", methods=["POST"])
def upload_persons_csv():
    file = request.files.get("file")

    if not file:
        return {"error": "No file uploaded"}, 400

    try:
        stream = file.stream.read().decode("utf-8").splitlines()
        csv_reader = csv.DictReader(stream)

        count = 0
        for row in csv_reader:
            name = row.get("name")
            location = row.get("location")

            if name and location:
                person = Person(name=name, location=location)
                db.session.add(person)
                count += 1

        db.session.commit()
        return {"status": "success", "imported": count}

    except Exception as e:
        return {"error": str(e)}, 500

@admin_bp.route("/admin/contact/upload", methods=["POST"])
def upload_contacts_csv():
    file = request.files.get("file")

    if not file:
        return {"error": "No file uploaded"}, 400

    try:
        stream = file.stream.read().decode("utf-8").splitlines()
        csv_reader = csv.DictReader(stream)

        count = 0
        for row in csv_reader:
            p1 = row.get("person1_id")
            p2 = row.get("person2_id")
            weight = row.get("weight")

            if p1 and p2 and weight:
                contact = Contact(
                    person1_id=int(p1),
                    person2_id=int(p2),
                    weight=float(weight)
                )
                db.session.add(contact)
                count += 1

        db.session.commit()
        return {"status": "success", "imported": count}

    except Exception as e:
        return {"error": str(e)}, 500
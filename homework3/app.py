import pymongo
from flask import Flask, jsonify, render_template, request
import uuid

app = Flask(__name__)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["application_database"]
application_collection = db["applications"]

def generate_id():
    return str(uuid.uuid4())


@app.route("/api/applications", methods=["GET"])
def get_all_applications():
    try:
        applications = list(application_collection.find())
        for application in applications:
            del application["_id"]
        return jsonify({"message": applications}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applications/status/pending", methods=["GET"])
def get_pending_applications():
    try:
        applications = list(application_collection.find())
        application_list = []
        
        for application in applications:
            del application["_id"]

            if application["status"] == "processing":
                application_list.append(application)

        return jsonify({"message": application_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applications", methods=["POST"])
def create_application():
    try:
        data = request.get_json()
        applicant_name = data.get("applicant_name")
        applicant_address = data.get("applicant_address")

        application_id = generate_id()

        application_collection.insert_one({
            "application_id": application_id,
            "applicant_name": applicant_name,
            "applicant_address": applicant_address,
            "status": "processing",
            "notes": []
        })

        return jsonify({"message": f"Application with id: {application_id} Created Successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


@app.route("/api/applications/notes/<application_id>", methods=["GET"])
def get_notes(application_id):
    try:
        application = application_collection.find_one({"application_id": application_id})

        if not application:
            return jsonify({"error": f"Application with ID '{application_id}' not found"}), 404

        notes = application["notes"]
        
        return jsonify({"notes": notes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applications/notes/<application_id>", methods=["PATCH"])
def add_notes(application_id):
    try:
        data = request.get_json()
        note = data.get("note")

        if not note:
            raise ValueError("Note cannot be empty")

        res =  application_collection.update_one(
            {"application_id": application_id},
            {"$push": {"notes": note}}
        )

        if res.matched_count == 0:
            return jsonify({"error": f"Application with ID '{application_id}' not found"}), 404

        return jsonify({"message": "Note added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applications/status/<application_id>", methods=["PATCH"])
def change_application_status(application_id):
    try:
        data = request.get_json()
        status = data.get("status")

        if status == "rejected":
            rejection_reason = data.get("rejection_reason")

            if not rejection_reason:
                raise ValueError("Reason for rejection cannot be empty")

            res = application_collection.update_one(
                {"application_id": application_id},
                {"$set": {"status": "rejected", "rejection_reason": rejection_reason}}
            )

            message = "Application rejected successfully"

        elif status == "accepted":
            res = application_collection.update_one(
            {"application_id": application_id},
            {"$set": {"status": "accepted"}}
            )

            message = "Application accepted successfully"

        else:
            raise ValueError("Invalid application status")

        if res.matched_count == 0:
            return jsonify({"error": f"Application with ID '{application_id}' not found"}), 404

        return jsonify({"message": message}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/applications/create")
def create_application_page():
  return render_template("create_application.html")

@app.route("/applications/accept")
def accept_application_page():
  return render_template("accept_application.html")

@app.route("/applications/reject")
def reject_application_page():
  return render_template("reject_application.html")

@app.route("/applications/notes")
def view_application_notes():
  return render_template("view_application_notes.html")

@app.route("/applications/notes/results")
def view_application_notes_results():
  return render_template("view_application_notes_results.html")

@app.route("/applications/pending")
def pending_applications():
    return render_template("pending_applications.html")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
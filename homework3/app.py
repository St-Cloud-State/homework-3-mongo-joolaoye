import pymongo
from flask import Flask, jsonify, render_template, request
import uuid

app = Flask(__name__)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["application_database"]
applicant_collection = db["applicants"]
application_collection = db["applications"]

def generate_id():
    return str(uuid.uuid4())

@app.route("/api/applicants", methods=["POST"])
def create_applicant():
    try:
        data = request.get_json()
        name = data.get("name")
        address = data.get("address")
        financials = data.get("financials")
        employment = data.get("employment")

        if not name:
            raise ValueError("Name is required")

        if not address:
            raise ValueError("Address is required")

        if not financials:
            raise ValueError("Financial information is required")

        if not all(key in financials for key in ["credit_score", "debt_owed", "monthly_expenses"]):
            raise ValueError("All fields for financial information is required")

        if employment:
            if not all(key in employment for key in ["employer_name", "annual_income", "employment_status"]):
                raise ValueError("All fields for employment information is required")

        if applicant_collection.find_one({"name": name, "address": address}):
            return jsonify({"error": "Applicant already exists"}), 400

        applicant_collection.insert_one({
            "name": name,
            "address": address,
            "financials": financials,
            "employment": employment
        })

        return jsonify({"message": "Applicant added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applicants", methods=["GET"])
def get_all_applicants():
    try:
        applicants = list(applicant_collection.find())
        for applicant in applicants:
            del applicant["_id"]
        return jsonify({"message": applicants}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applications", methods=["GET"])
def get_all_applications():
    try:
        applications = list(application_collection.find())
        for application in applications:
            del application["_id"]
        return jsonify({"message": applications}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/applications", methods=["POST"])
def create_application():
    try:
        data = request.get_json()
        applicant_name = data.get("applicant_name")
        applicant_address = data.get("applicant_address")

        if not (applicant_name and applicant_address):
            raise ValueError("All fields are required")

        if not applicant_collection.find_one({"name": applicant_name, "address": applicant_address}):
            raise KeyError("Applicant does not exist")

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
        return jsonify({"error": str(e)}), 400


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
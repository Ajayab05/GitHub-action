import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics

# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Prometheus Metrics
# --------------------------------------------------

metrics = PrometheusMetrics(app)

# --------------------------------------------------
# Database Configuration
# --------------------------------------------------

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------------------------------------
# Employee Model
# --------------------------------------------------

class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.route("/")
def root():
    return jsonify({
        "application": "employee-crud",
        "status": "healthy"
    })

@app.route("/api")
def api_health():
    return jsonify({
        "status": "healthy"
    })

# --------------------------------------------------
# Get All Employees
# --------------------------------------------------

@app.route("/api/employees", methods=["GET"])
def get_employees():

    employees = Employee.query.all()

    return jsonify([
        {
            "id": emp.id,
            "name": emp.name,
            "email": emp.email
        }
        for emp in employees
    ])

# --------------------------------------------------
# Create Employee
# --------------------------------------------------

@app.route("/api/employees", methods=["POST"])
def create_employee():

    try:

        body = request.get_json()

        employee = Employee(
            name=body["name"],
            email=body["email"]
        )

        db.session.add(employee)
        db.session.commit()

        return jsonify({
            "message": "Employee created"
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500

# --------------------------------------------------
# Update Employee
# --------------------------------------------------

@app.route("/api/employees/<int:id>", methods=["PUT"])
def update_employee(id):

    employee = Employee.query.get(id)

    if not employee:
        return jsonify({
            "message": "Employee not found"
        }), 404

    body = request.get_json()

    employee.name = body["name"]
    employee.email = body["email"]

    db.session.commit()

    return jsonify({
        "message": "Employee updated"
    })

# --------------------------------------------------
# Delete Employee
# --------------------------------------------------

@app.route("/api/employees/<int:id>", methods=["DELETE"])
def delete_employee(id):

    employee = Employee.query.get(id)

    if not employee:
        return jsonify({
            "message": "Employee not found"
        }), 404

    db.session.delete(employee)
    db.session.commit()

    return jsonify({
        "message": "Employee deleted"
    })

# --------------------------------------------------
# Startup
# --------------------------------------------------

with app.app_context():
    db.create_all()

# --------------------------------------------------
# Local Run
# --------------------------------------------------
# --------------------------------------------------
# Local Run
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # nosec B104
        port=5000
    )

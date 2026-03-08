from flask import Flask, request, jsonify, render_template
import database as db

app = Flask(__name__)
db.init_db()


@app.route("/")
def index():
    projects = db.get_all_projects_with_feature_counts()
    return render_template("index.html", projects=projects)


@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    status = data.get("status", "idea")
    if status not in db.VALID_STATUSES:
        return jsonify({"error": f"status must be one of {db.VALID_STATUSES}"}), 400
    project = db.create_project(
        data["name"],
        data.get("description", ""),
        status,
        data.get("notes", ""),
    )
    return jsonify(project), 201


@app.route("/projects/reorder", methods=["PATCH"])
def reorder_projects():
    data = request.get_json()
    if not data or "order" not in data:
        return jsonify({"error": "order list is required"}), 400
    db.reorder_projects(data["order"])
    return jsonify({"success": True})


@app.route("/projects/<int:project_id>", methods=["PATCH"])
def edit_project(project_id):
    if not db.get_project(project_id):
        return jsonify({"error": "project not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400
    if "status" in data and data["status"] not in db.VALID_STATUSES:
        return jsonify({"error": f"status must be one of {db.VALID_STATUSES}"}), 400
    project = db.update_project(project_id, **data)
    return jsonify(project)


@app.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    if not db.get_project(project_id):
        return jsonify({"error": "project not found"}), 404
    db.delete_project(project_id)
    return jsonify({"deleted": True})


@app.route("/projects/<int:project_id>/features", methods=["GET"])
def get_features(project_id):
    if not db.get_project(project_id):
        return jsonify({"error": "project not found"}), 404
    features = db.get_features(project_id)
    return jsonify(features)


@app.route("/projects/<int:project_id>/features", methods=["POST"])
def add_feature(project_id):
    if not db.get_project(project_id):
        return jsonify({"error": "project not found"}), 404
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    status = data.get("status", "idea")
    if status not in db.VALID_STATUSES:
        return jsonify({"error": f"status must be one of {db.VALID_STATUSES}"}), 400
    feature = db.create_feature(project_id, data["name"], status, data.get("description", ""))
    return jsonify(feature), 201


@app.route("/features/<int:feature_id>", methods=["PATCH"])
def edit_feature(feature_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400
    if "status" in data and data["status"] not in db.VALID_STATUSES:
        return jsonify({"error": f"status must be one of {db.VALID_STATUSES}"}), 400
    feature = db.update_feature(feature_id, **data)
    if not feature:
        return jsonify({"error": "feature not found"}), 404
    return jsonify(feature)


@app.route("/features/<int:feature_id>", methods=["DELETE"])
def delete_feature(feature_id):
    db.delete_feature(feature_id)
    return jsonify({"deleted": True})


if __name__ == "__main__":
    app.run(debug=True, port=5001)

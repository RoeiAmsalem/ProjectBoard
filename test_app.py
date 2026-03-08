import pytest
import os
import json
import database as db

# Override DB path for tests
db.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_projects.db")

from app import app


@pytest.fixture(autouse=True)
def setup_db():
    """Reset the database before each test."""
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    db.init_db()
    yield
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_project(client):
    res = client.post("/projects", json={"name": "MyApp", "description": "A cool app", "status": "idea"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "MyApp"
    assert data["description"] == "A cool app"
    assert data["status"] == "idea"
    assert "id" in data


def test_edit_project_status(client):
    res = client.post("/projects", json={"name": "MyApp", "status": "idea"})
    pid = res.get_json()["id"]
    res = client.patch(f"/projects/{pid}", json={"status": "active"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "active"


def test_delete_project(client):
    res = client.post("/projects", json={"name": "ToDelete"})
    pid = res.get_json()["id"]
    res = client.delete(f"/projects/{pid}")
    assert res.status_code == 200
    assert res.get_json()["deleted"] is True
    res = client.patch(f"/projects/{pid}", json={"name": "Ghost"})
    assert res.status_code == 404


def test_add_feature(client):
    res = client.post("/projects", json={"name": "Proj"})
    pid = res.get_json()["id"]
    res = client.post(f"/projects/{pid}/features", json={"name": "Auth", "status": "developing"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Auth"
    assert data["status"] == "developing"
    assert data["project_id"] == pid


def test_delete_feature(client):
    res = client.post("/projects", json={"name": "Proj"})
    pid = res.get_json()["id"]
    res = client.post(f"/projects/{pid}/features", json={"name": "Feat"})
    fid = res.get_json()["id"]
    res = client.delete(f"/features/{fid}")
    assert res.status_code == 200
    res = client.get(f"/projects/{pid}/features")
    assert len(res.get_json()) == 0


def test_cascade_delete(client):
    res = client.post("/projects", json={"name": "CascadeProj"})
    pid = res.get_json()["id"]
    client.post(f"/projects/{pid}/features", json={"name": "F1"})
    client.post(f"/projects/{pid}/features", json={"name": "F2"})
    res = client.get(f"/projects/{pid}/features")
    assert len(res.get_json()) == 2
    client.delete(f"/projects/{pid}")
    # Project gone — features should be gone too
    res = client.get(f"/projects/{pid}/features")
    assert res.status_code == 404


def test_project_notes(client):
    """Test creating and updating project notes."""
    res = client.post("/projects", json={"name": "NoteProj", "description": "desc"})
    pid = res.get_json()["id"]
    assert res.get_json()["notes"] == ""

    res = client.patch(f"/projects/{pid}", json={"notes": "Some important notes"})
    assert res.status_code == 200
    assert res.get_json()["notes"] == "Some important notes"


def test_project_position(client):
    """Test that projects get auto-assigned positions."""
    r1 = client.post("/projects", json={"name": "First"})
    r2 = client.post("/projects", json={"name": "Second"})
    r3 = client.post("/projects", json={"name": "Third"})
    assert r1.get_json()["position"] == 0
    assert r2.get_json()["position"] == 1
    assert r3.get_json()["position"] == 2


def test_reorder_projects(client):
    """Test reordering projects via PATCH /projects/reorder."""
    r1 = client.post("/projects", json={"name": "A"})
    r2 = client.post("/projects", json={"name": "B"})
    r3 = client.post("/projects", json={"name": "C"})
    id1, id2, id3 = r1.get_json()["id"], r2.get_json()["id"], r3.get_json()["id"]

    # Reverse order
    res = client.patch("/projects/reorder", json={"order": [id3, id2, id1]})
    assert res.status_code == 200
    assert res.get_json()["success"] is True

    # Verify positions updated
    projects = db.get_all_projects_with_feature_counts()
    pos_map = {p["id"]: p["position"] for p in projects}
    assert pos_map[id3] == 0
    assert pos_map[id2] == 1
    assert pos_map[id1] == 2


def test_feature_counts(client):
    """Test that feature counts are returned with projects."""
    res = client.post("/projects", json={"name": "CountProj"})
    pid = res.get_json()["id"]

    client.post(f"/projects/{pid}/features", json={"name": "F1", "status": "idea"})
    client.post(f"/projects/{pid}/features", json={"name": "F2", "status": "developing"})
    client.post(f"/projects/{pid}/features", json={"name": "F3", "status": "active"})

    projects = db.get_all_projects_with_feature_counts()
    proj = next(p for p in projects if p["id"] == pid)
    assert proj["feature_count"] == 3
    assert proj["features_active"] == 1
    assert proj["features_developing"] == 1
    assert proj["features_idea"] == 1


def test_feature_description(client):
    """Test creating and updating feature descriptions."""
    res = client.post("/projects", json={"name": "Proj"})
    pid = res.get_json()["id"]

    # Create feature with description
    res = client.post(f"/projects/{pid}/features", json={
        "name": "Auth",
        "description": "Login and signup flow"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["description"] == "Login and signup flow"

    # Update feature description
    fid = data["id"]
    res = client.patch(f"/features/{fid}", json={"description": "Updated desc"})
    assert res.status_code == 200
    assert res.get_json()["description"] == "Updated desc"


def test_reorder_missing_order(client):
    """Test that reorder endpoint requires order list."""
    res = client.patch("/projects/reorder", json={})
    assert res.status_code == 400

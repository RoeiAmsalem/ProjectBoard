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

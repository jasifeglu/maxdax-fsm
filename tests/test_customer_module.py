from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_admin_customer_crud_and_history():
    create_res = client.post(
        "/admin/customers",
        json={"name": "Ava", "mobile_number": "123456789", "email": "ava@example.com"},
    )
    assert create_res.status_code == 201
    customer_id = create_res.json()["id"]

    list_res = client.get("/admin/customers")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    update_res = client.put(f"/admin/customers/{customer_id}", json={"name": "Ava Updated"})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Ava Updated"

    ticket_res = client.post("/tickets", json={"mobile_number": "123456789", "issue": "Need help"})
    assert ticket_res.status_code == 201

    detail_res = client.get(f"/admin/customers/{customer_id}")
    assert detail_res.status_code == 200
    assert len(detail_res.json()["service_history"]) == 1

    delete_res = client.delete(f"/admin/customers/{customer_id}")
    assert delete_res.status_code == 204


def test_ticket_auto_creates_customer_when_mobile_not_found():
    ticket_res = client.post(
        "/tickets",
        json={
            "mobile_number": "999888777",
            "issue": "Initial onboarding",
            "customer_name": "New Customer",
            "customer_email": "new@example.com",
        },
    )
    assert ticket_res.status_code == 201

    customers_res = client.get("/admin/customers")
    assert customers_res.status_code == 200
    customers = customers_res.json()
    assert len(customers) == 1
    assert customers[0]["mobile_number"] == "999888777"

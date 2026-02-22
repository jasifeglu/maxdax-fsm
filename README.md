# Maxdax FSM - Customer Module

This repository now contains a minimal **Customer module** with:

- Admin CRUD for customers.
- Ticket creation flow that checks if a mobile number exists.
- Automatic customer creation when no customer exists for the mobile number.
- Service history persisted per customer when tickets are created.

## Run

```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```

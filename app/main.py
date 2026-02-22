from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Module")


@app.post("/admin/customers", response_model=schemas.CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    existing = crud.get_customer_by_mobile(db, payload.mobile_number)
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this mobile number already exists")
    return crud.create_customer(db, payload)


@app.get("/admin/customers", response_model=list[schemas.CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    return crud.list_customers(db)


@app.get("/admin/customers/{customer_id}", response_model=schemas.CustomerWithHistory)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    history = crud.get_customer_history(db, customer.id)
    return schemas.CustomerWithHistory.model_validate(
        {
            **schemas.CustomerRead.model_validate(customer).model_dump(),
            "service_history": history,
        }
    )


@app.put("/admin/customers/{customer_id}", response_model=schemas.CustomerRead)
def update_customer(customer_id: int, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if payload.mobile_number and payload.mobile_number != customer.mobile_number:
        existing = crud.get_customer_by_mobile(db, payload.mobile_number)
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this mobile number already exists")

    return crud.update_customer(db, customer, payload)


@app.delete("/admin/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud.delete_customer(db, customer)


@app.post("/tickets", response_model=schemas.TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket_and_history(db, payload)

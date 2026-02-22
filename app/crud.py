from sqlalchemy.orm import Session

from app import models, schemas


def create_customer(db: Session, payload: schemas.CustomerCreate) -> models.Customer:
    customer = models.Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: int) -> models.Customer | None:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_mobile(db: Session, mobile_number: str) -> models.Customer | None:
    return db.query(models.Customer).filter(models.Customer.mobile_number == mobile_number).first()


def list_customers(db: Session) -> list[models.Customer]:
    return db.query(models.Customer).order_by(models.Customer.id.asc()).all()


def update_customer(db: Session, customer: models.Customer, payload: schemas.CustomerUpdate) -> models.Customer:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: models.Customer) -> None:
    db.delete(customer)
    db.commit()


def create_ticket_and_history(db: Session, payload: schemas.TicketCreate) -> models.Ticket:
    customer = get_customer_by_mobile(db, payload.mobile_number)
    if customer is None:
        customer = models.Customer(
            name=payload.customer_name or f"Customer-{payload.mobile_number[-4:]}",
            mobile_number=payload.mobile_number,
            email=payload.customer_email,
        )
        db.add(customer)
        db.flush()

    ticket = models.Ticket(issue=payload.issue, customer_id=customer.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_customer_history(db: Session, customer_id: int) -> list[models.Ticket]:
    return (
        db.query(models.Ticket)
        .filter(models.Ticket.customer_id == customer_id)
        .order_by(models.Ticket.created_at.desc())
        .all()
    )

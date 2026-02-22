from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    mobile_number: str = Field(min_length=5, max_length=32)
    email: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    mobile_number: str | None = Field(default=None, min_length=5, max_length=32)
    email: str | None = None


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketCreate(BaseModel):
    mobile_number: str = Field(min_length=5, max_length=32)
    issue: str = Field(min_length=1)
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)
    customer_email: str | None = None


class TicketRead(BaseModel):
    id: int
    issue: str
    status: str
    customer_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerWithHistory(CustomerRead):
    service_history: list[TicketRead]

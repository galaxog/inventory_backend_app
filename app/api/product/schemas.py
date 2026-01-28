from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel
from app import models

@dataclass
class ProductCreateRequest(BaseModel):
    name: str
    description: str
    price: float
    inventory: Optional[int] = 1


@dataclass
class UpdateProductInventoryRequest(BaseModel):
    quantity: int
    type: models.Product.UpdateType
    reason_code: Optional[str] = None


@dataclass
class ProductCreateResponse:
    id: int
    name: str
    description: str
    price: float
    inventory: int


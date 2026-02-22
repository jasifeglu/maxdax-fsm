from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class InventoryError(Exception):
    """Raised when inventory operations are invalid."""


@dataclass
class StockStore:
    """Generic stock store for warehouses and technician vans."""

    name: str
    stock: Dict[str, int] = field(default_factory=dict)

    def add_stock(self, sku: str, quantity: int) -> None:
        if quantity <= 0:
            raise InventoryError("Quantity added must be positive")
        self.stock[sku] = self.stock.get(sku, 0) + quantity

    def remove_stock(self, sku: str, quantity: int) -> None:
        if quantity <= 0:
            raise InventoryError("Quantity removed must be positive")
        current = self.stock.get(sku, 0)
        if current < quantity:
            raise InventoryError(
                f"Insufficient stock for {sku} in {self.name}. Have {current}, need {quantity}."
            )
        remaining = current - quantity
        if remaining:
            self.stock[sku] = remaining
        else:
            self.stock.pop(sku, None)

    def get_stock(self, sku: str) -> int:
        return self.stock.get(sku, 0)

    def low_stock_items(self, threshold: int) -> Dict[str, int]:
        if threshold < 0:
            raise InventoryError("Threshold must be non-negative")
        return {sku: qty for sku, qty in self.stock.items() if qty <= threshold}


@dataclass
class TicketUsage:
    ticket_id: str
    technician_id: str
    used_parts: Dict[str, int]


class InventoryModule:
    """Inventory module that manages warehouse + van stock and ticket spare usage."""

    def __init__(self) -> None:
        self.warehouses: Dict[str, StockStore] = {}
        self.vans: Dict[str, StockStore] = {}
        self.usage_log: List[TicketUsage] = []

    def create_warehouse(self, warehouse_id: str) -> StockStore:
        store = StockStore(name=f"warehouse:{warehouse_id}")
        self.warehouses[warehouse_id] = store
        return store

    def create_van(self, technician_id: str) -> StockStore:
        store = StockStore(name=f"van:{technician_id}")
        self.vans[technician_id] = store
        return store

    def transfer_to_van(self, warehouse_id: str, technician_id: str, sku: str, quantity: int) -> None:
        warehouse = self._get_warehouse(warehouse_id)
        van = self._get_van(technician_id)
        warehouse.remove_stock(sku, quantity)
        van.add_stock(sku, quantity)

    def use_spares_for_ticket(self, ticket_id: str, technician_id: str, used_parts: Dict[str, int]) -> TicketUsage:
        if not used_parts:
            raise InventoryError("used_parts cannot be empty")

        van = self._get_van(technician_id)
        for sku, quantity in used_parts.items():
            van.remove_stock(sku, quantity)

        usage = TicketUsage(ticket_id=ticket_id, technician_id=technician_id, used_parts=dict(used_parts))
        self.usage_log.append(usage)
        return usage

    def low_stock_alerts(self, threshold: int) -> Dict[str, Dict[str, int]]:
        return {
            "warehouses": {
                warehouse_id: store.low_stock_items(threshold)
                for warehouse_id, store in self.warehouses.items()
                if store.low_stock_items(threshold)
            },
            "vans": {
                technician_id: store.low_stock_items(threshold)
                for technician_id, store in self.vans.items()
                if store.low_stock_items(threshold)
            },
        }

    def _get_warehouse(self, warehouse_id: str) -> StockStore:
        if warehouse_id not in self.warehouses:
            raise InventoryError(f"Unknown warehouse: {warehouse_id}")
        return self.warehouses[warehouse_id]

    def _get_van(self, technician_id: str) -> StockStore:
        if technician_id not in self.vans:
            raise InventoryError(f"Unknown technician van: {technician_id}")
        return self.vans[technician_id]

import unittest

from inventory import InventoryError, InventoryModule


class InventoryModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = InventoryModule()
        self.module.create_warehouse("wh-1")
        self.module.create_van("tech-1")

    def test_warehouse_and_van_stock(self):
        wh = self.module.warehouses["wh-1"]
        wh.add_stock("fan-motor", 10)

        self.module.transfer_to_van("wh-1", "tech-1", "fan-motor", 3)

        self.assertEqual(wh.get_stock("fan-motor"), 7)
        self.assertEqual(self.module.vans["tech-1"].get_stock("fan-motor"), 3)

    def test_spare_usage_during_ticket(self):
        wh = self.module.warehouses["wh-1"]
        wh.add_stock("capacitor", 5)
        self.module.transfer_to_van("wh-1", "tech-1", "capacitor", 5)

        usage = self.module.use_spares_for_ticket(
            ticket_id="T-42",
            technician_id="tech-1",
            used_parts={"capacitor": 2},
        )

        self.assertEqual(usage.ticket_id, "T-42")
        self.assertEqual(self.module.vans["tech-1"].get_stock("capacitor"), 3)

    def test_low_stock_alert(self):
        wh = self.module.warehouses["wh-1"]
        van = self.module.vans["tech-1"]
        wh.add_stock("relay", 2)
        van.add_stock("fuse", 1)

        alerts = self.module.low_stock_alerts(threshold=2)

        self.assertEqual(alerts["warehouses"]["wh-1"]["relay"], 2)
        self.assertEqual(alerts["vans"]["tech-1"]["fuse"], 1)

    def test_raises_when_using_more_than_van_has(self):
        with self.assertRaises(InventoryError):
            self.module.use_spares_for_ticket("T-77", "tech-1", {"sensor": 1})


if __name__ == "__main__":
    unittest.main()

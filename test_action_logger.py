import unittest

from action_logger import ActionLogger, ActionType


class ActionLoggerTests(unittest.TestCase):
    def test_logs_every_required_action_type(self) -> None:
        logger = ActionLogger()
        actor_id = "dispatcher-1"

        required_actions = [
            ActionType.TICKET_CREATION,
            ActionType.ASSIGNMENT_CHANGE,
            ActionType.BILLING,
            ActionType.STATUS_UPDATE,
            ActionType.GPS_LOG,
        ]

        for action in required_actions:
            logger.log(action, {"example": True}, actor_id)

        entries = logger.all_entries()
        self.assertEqual(len(entries), len(required_actions))
        self.assertEqual([entry.action_type for entry in entries], required_actions)
        self.assertTrue(all(entry.actor_id == actor_id for entry in entries))


if __name__ == "__main__":
    unittest.main()

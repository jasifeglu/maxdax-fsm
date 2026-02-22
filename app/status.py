WORKFLOW = [
    "New",
    "Assigned",
    "Scheduled",
    "On Site",
    "Working",
    "Pending",
    "Completed",
    "Closed",
]


def next_status(current):
    if current not in WORKFLOW:
        return None
    idx = WORKFLOW.index(current)
    if idx == len(WORKFLOW) - 1:
        return None
    return WORKFLOW[idx + 1]


def can_transition(from_status, to_status):
    return next_status(from_status) == to_status

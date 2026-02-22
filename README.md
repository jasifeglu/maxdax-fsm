# Workflow Automation FSMs

This repository includes reusable finite-state workflow automation definitions for:

- SLA timer alerts
- Ticket escalation
- AMC reminder scheduling

## File

- `workflows/automation_workflows.json` – machine-readable workflow definitions including triggers, states, actions, and transitions.

## Validation

Use Python to validate JSON syntax:

```bash
python -m json.tool workflows/automation_workflows.json >/dev/null
```

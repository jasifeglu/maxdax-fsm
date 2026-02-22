# Modules

This folder supports feature-based modules (e.g., `WorkOrders`, `Inventory`, `Reporting`).
Each module should contain:

- `Application/` services/use-cases
- `Domain/` entities and interfaces
- `Infrastructure/` repositories/gateways
- `Http/` controllers, requests, resources

Example:
`app/Modules/WorkOrders/{Application,Domain,Infrastructure,Http}`

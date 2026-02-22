# MaxDax FSM - Role-Based Authentication

Implements role-based authentication with these roles:
- Admin
- Coordinator
- Technician

## Features
- Admin-only endpoint to create technicians.
- Technician login is automatically created with a temporary password and forced password change.
- Secure JWT authentication (HS256, expiration, issuer validation, signature verification).
- Password reset flow using expiring reset tokens.
- Permission middleware (`require_roles`) for route-level authorization.

## Run
```bash
python -m src.server
```

## API
- `POST /auth/login`
- `POST /admin/technicians` (Admin only)
- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`
- `GET /me` (any authenticated role)

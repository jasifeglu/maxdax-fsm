# MAXDAX FSM

Production-oriented full stack starter for **MAXDAX Field Service Management**.

## Stack
- **Backend API:** Laravel + JWT
- **Database:** MySQL
- **Admin Panel:** React (Vite)
- **Mobile App:** Flutter (Android-first)

## Repository Structure
```
maxdax-fsm/
├── backend/          # Laravel API
├── frontend-admin/   # React admin panel
├── mobile-app/       # Flutter mobile app
└── docs/
```

## Architecture Overview
- Role-based authentication with three roles:
  - `admin`
  - `coordinator`
  - `technician`
- REST API versioning under `/api/v1`
- JWT authentication via `tymon/jwt-auth`
- Backend prepared for modular growth under `backend/app/Modules`

---

## 1) Backend Setup (Laravel API)

### Prerequisites
- PHP 8.2+
- Composer 2+
- MySQL 8+

### Install
```bash
cd backend
cp .env.example .env
composer install
php artisan key:generate
php artisan jwt:secret
php artisan migrate
php artisan serve
```

API base URL: `http://localhost:8000/api/v1`

### Auth Endpoints
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me` (Bearer token)
- `POST /api/v1/auth/logout` (Bearer token)

---

## 2) Frontend Setup (React Admin)

### Prerequisites
- Node.js 20+
- npm 10+

### Install
```bash
cd frontend-admin
cp .env.example .env
npm install
npm run dev
```

Create `frontend-admin/.env.example`:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

Admin panel URL: `http://localhost:5173`

---

## 3) Mobile Setup (Flutter Android)

### Prerequisites
- Flutter 3.22+
- Android Studio + SDK

### Install
```bash
cd mobile-app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

> `10.0.2.2` maps Android emulator to host localhost.

---

## Environment Notes
- All secret keys must be injected per environment.
- Use separate MySQL databases per environment (`dev`, `staging`, `prod`).
- Add CORS rules in Laravel for admin web and mobile origins.

## Production Hardening Checklist
- Enable HTTPS and secure headers.
- Configure rate limiting for auth endpoints.
- Add refresh token strategy and token revocation list.
- Set up CI/CD with automated tests and linting.
- Enable centralized logging and error monitoring.

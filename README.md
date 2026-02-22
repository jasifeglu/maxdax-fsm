# Maxdax FSM GPS Tracking

This implementation adds:

- Background GPS tracking for technicians
- Location snapshots on job events:
  - Check-in
  - Check-out
  - Status update
  - Billing submit
- Live admin map dashboard based on `live_locations`

## Key behavior

- The technician app does **not** expose a dedicated GPS screen.
- GPS updates are sent in the background to Firestore (`live_locations`).
- Event-triggered snapshots are stored in Firestore (`location_events`) and also refresh `live_locations`.

## Firestore collections

- `live_locations/{technicianId}`: most recent known location per technician.
- `location_events/{autoId}`: immutable audit trail of event-based location saves.

## Platform requirements

You still need standard Android/iOS background location setup:

- Android location permissions + foreground service notification config
- iOS background modes and location permission keys

## Run

```bash
flutter pub get
flutter run
```

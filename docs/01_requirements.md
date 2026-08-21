# Requirements Specification

**Project:** Smart Lab Equipment & Slot Reservation Portal
**Problem Statement:** #01 — Campus & Academic Operations
**Course:** Software Engineering — Lab 1: Requirements Engineering & UML Use-Case Modelling
**Institution:** PES University, Dept. of CSE

---

## 1. Scope

Engineering lab facilities host high-value hardware instruments (oscilloscopes, logic analyzers,
FPGA development boards) that are shared across many student batches. The portal provides a
single authoritative schedule for these instruments so that a given asset can never be
double-booked, so that only calibrated equipment can be reserved, and so that late returns are
detected and penalised consistently rather than at a technician's discretion.

### Actors

| Actor | Type | Responsibilities |
|---|---|---|
| **Student** | Primary (human) | Browses equipment, reserves slots, checks out / returns equipment, cancels reservations, joins waitlists. |
| **Lab Technician** | Primary (human) | Maintains the equipment catalogue, records calibration and maintenance status, verifies physical handover, resolves disputed penalties. |
| **Notification Service** | Secondary (system) | Delivers reservation, waitlist and overdue notifications over e-mail/SMS. |
| **Institute Identity Provider (SSO)** | Secondary (system) | Authenticates users and supplies role claims. |

---

## 2. Functional Requirements

| ID | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|
| **FR-001** | The system shall allow authenticated students to view real-time availability and reserve a maximum 2-hour slot for any **calibrated** equipment up to 7 days in advance. | High | **Pass:** Slot is atomically locked for the requesting student and a unique reservation token is generated and displayed. **Fail:** Two students hold the same asset for overlapping times, a slot longer than 2 hours is accepted, or a slot more than 7 days ahead is accepted. | Core value of the portal. Bounding slot length and the booking horizon keeps scarce instruments circulating fairly across batches. |
| **FR-002** | The system shall present a searchable equipment catalogue that shows, for each asset, its category, lab location, current calibration state (`Calibrated` / `Due` / `Out-of-Service`) and calibration expiry date, and shall exclude non-`Calibrated` assets from all reservable results. | High | **Pass:** A search returns only assets whose calibration state is `Calibrated` and whose expiry date is later than the requested slot end time; an asset marked `Due` or `Out-of-Service` is not offered for booking. **Fail:** An uncalibrated or expired asset appears as reservable. | Measurements taken on an uncalibrated instrument are invalid and can damage coursework results; enforcement must be systemic, not procedural. |
| **FR-003** | The system shall allow a Lab Technician to create, update and retire equipment records and to log a calibration or maintenance event, which updates the asset's calibration state and expiry date and automatically cancels any conflicting future reservations with notification to the affected students. | High | **Pass:** After a technician marks an asset `Out-of-Service`, the asset disappears from availability search and every future reservation on it is cancelled with a notification dispatched to each affected student. **Fail:** Reservations survive on a retired or out-of-service asset, or affected students are not notified. | The technician owns physical ground truth; the schedule must follow the equipment's real state without manual reconciliation. |
| **FR-004** | The system shall record equipment check-out and check-in against a reservation by scanning the asset ID, shall compute the return delay against the reserved slot end time, and shall apply the configured late-return penalty (warning, then a booking ban of N days) when the delay exceeds the 15-minute grace period. | High | **Pass:** A return logged 20 minutes after slot end records a late return and applies the next penalty tier; a return within 15 minutes records as on-time with no penalty. **Fail:** Lateness is not detected, the grace period is misapplied, or a penalty is applied without an auditable record. | Late returns cascade into every subsequent slot on the same asset; automatic, uniform enforcement is the disciplinary rule the department asked for. |
| **FR-005** | The system shall allow a student to cancel an existing reservation before its start time, and shall allow students to join a waitlist for a fully booked asset, offering a released slot to the first waitlisted student with a 30-minute claim window before offering it to the next. | Medium | **Pass:** Cancelling frees the slot immediately and the first waitlisted student receives an offer; an unclaimed offer expires after 30 minutes and passes to the next student in queue. **Fail:** A cancelled slot stays blocked, the waitlist is served out of order, or an offer never expires. | Recovers capacity lost to no-shows and removes the informal "ask around the lab" allocation that the portal is meant to replace. |

---

## 3. Non-Functional Requirements

| ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|---|
| **NFR-001** | Performance & Security | The system shall process concurrent slot reservation requests within **200 ms** (95th percentile) while holding strict database-level lock isolation (`SERIALIZABLE` on the asset-slot row) so that race conditions cannot produce a double booking. | High | **Pass:** A load benchmark of 200 concurrent reservation attempts on the same asset-slot reports p95 latency ≤ 200 ms, exactly one success, and zero double bookings. **Fail:** p95 latency exceeds 200 ms or more than one reservation is granted for the same asset-slot. | Demand spikes the moment a lab schedule is published; correctness under that burst is the single behaviour the whole portal is judged on. |
| **NFR-002** | Availability & Auditability | The system shall be available **99.5%** of each academic month (excluding a published maintenance window) and shall retain an immutable, timestamped audit log of every reservation, cancellation, check-out, check-in, calibration change and penalty for **24 months**, exportable by a Lab Technician. | Medium | **Pass:** Monthly uptime report shows ≥ 99.5% availability; a sampled penalty can be traced end-to-end through the audit log, and log entries cannot be edited or deleted through any application interface. **Fail:** Uptime falls below target, or any audited event is missing, mutable, or purged before 24 months. | Penalties affect student records and are appealed; without a tamper-evident trail the department cannot defend a booking ban or reconstruct equipment usage for procurement. |

---

## 4. Requirement Traceability

| Requirement | Realised by Use Case |
|---|---|
| FR-001 | Reserve Equipment Slot |
| FR-002 | Browse Equipment Catalogue, Verify Calibration Status |
| FR-003 | Manage Equipment Catalogue, Log Calibration / Maintenance |
| FR-004 | Check Out Equipment, Return Equipment, Apply Late-Return Penalty |
| FR-005 | Cancel Reservation, Join Waitlist |
| NFR-001 | Reserve Equipment Slot (concurrency path) |
| NFR-002 | All use cases (cross-cutting audit logging) |

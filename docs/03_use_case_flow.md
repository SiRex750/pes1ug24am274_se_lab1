# Use-Case Flow Specification

**Project:** Smart Lab Equipment & Slot Reservation Portal
**Use Case:** UC-02 — Reserve Equipment Slot
**Related Requirements:** FR-001, FR-002 (via *Verify Calibration Status*), FR-005 (via *Join Waitlist*), NFR-001

---

| Field | Value |
|---|---|
| **Use Case ID / Name** | UC-02 — Reserve Equipment Slot |
| **Primary Actor** | Student |
| **Secondary Actors** | Institute Identity Provider (SSO), Notification Service |
| **Stakeholders & Interests** | *Student:* wants a guaranteed, working instrument at a predictable time. *Lab Technician:* wants every booking to point at a calibrated asset and to be traceable. *Department:* wants fair distribution of scarce equipment. |
| **Trigger** | The student selects an available slot for an instrument from the equipment catalogue and confirms the booking. |
| **Level / Scope** | User goal / Smart Lab Equipment & Slot Reservation Portal |
| **Included Use Cases** | *Authenticate User*, *Verify Calibration Status* |
| **Extending Use Cases** | *Join Waitlist* (extension point: **No Free Slot**) |
| **Frequency of Use** | High — peaks immediately after each weekly lab schedule is published. |

---

## Preconditions

1. The student holds an active institute account with a `Student` role claim and is not currently serving a late-return booking ban (FR-004).
2. The equipment catalogue contains at least one asset whose calibration state is `Calibrated` with an expiry date later than the requested slot end time.
3. The requested slot lies within the 7-day booking horizon and the lab's published operating hours.
4. The student holds fewer than the configured maximum of concurrent active reservations.

## Postconditions

**On success:**
1. A reservation record exists in state `CONFIRMED`, bound to exactly one asset, one student and one non-overlapping time range of at most 2 hours.
2. The asset-slot is locked; it no longer appears as available to any other student.
3. A unique reservation token (QR / alphanumeric) is generated and shown to the student, and a confirmation is dispatched through the Notification Service.
4. An immutable audit entry (`RESERVATION_CREATED`) is written with actor, asset, slot and timestamp (NFR-002).

**On failure:** no reservation record is created, no slot is locked, the database transaction is rolled back in full, and the student is shown the reason for rejection. System state is identical to the state before the trigger.

---

## Main Success Scenario

| Step | Actor | Action |
|---|---|---|
| 1 | Student | Opens the portal and requests the equipment catalogue. |
| 2 | System | **«include» *Authenticate User*** — redirects to the Institute IdP, receives a validated token with the `Student` role claim, and establishes a session. |
| 3 | System | Checks the student's disciplinary status and active-reservation count; both are within limits. |
| 4 | Student | Filters the catalogue by equipment category, lab location and desired date. |
| 5 | System | **«include» *Verify Calibration Status*** — returns only assets in state `Calibrated` whose calibration expiry falls after the requested slot end, together with their real-time free/booked slot grid. |
| 6 | Student | Selects an asset, picks a start time and a duration of at most 2 hours, and submits the reservation. |
| 7 | System | Validates the request: duration ≤ 2 h, start time within the 7-day horizon and within lab operating hours, no overlap with the student's other reservations. |
| 8 | System | Opens a transaction and acquires a `SERIALIZABLE` row lock on the target asset-slot, then re-checks availability inside the lock (NFR-001). |
| 9 | System | Persists the reservation in state `CONFIRMED`, generates the reservation token, writes the `RESERVATION_CREATED` audit entry and commits the transaction. |
| 10 | System | Dispatches a confirmation with the token and slot details through the Notification Service. |
| 11 | Student | Sees the confirmation screen showing the asset, slot, token and return deadline. The use case ends. |

---

## Alternate Flow

### AF-1 — Slot taken by a concurrent request (step 8)

Triggered when two students submit a reservation for the same asset-slot at nearly the same instant and this request loses the row lock.

| Step | Actor | Action |
|---|---|---|
| 8a.1 | System | Acquires the row lock after the competing transaction has committed, and the in-lock re-check finds the slot already held. |
| 8a.2 | System | Rolls back the transaction; no partial reservation, token or notification is produced. |
| 8a.3 | System | Writes an audit entry (`RESERVATION_REJECTED_CONFLICT`) and returns a "slot just taken" message with the refreshed availability grid for that asset. |
| 8a.4 | System | **«extend» *Join Waitlist*** — because the extension point **No Free Slot** is now satisfied for the requested asset and date, the system offers the student a place on the waitlist. |
| 8a.5 | Student | Either selects a different free slot and the flow resumes at **step 6**, or accepts the waitlist offer, in which case *Join Waitlist* (FR-005) executes and this use case ends without a reservation. |

---

## Other Exception Flows (summary)

| ID | Condition | System response |
|---|---|---|
| EF-1 | IdP authentication fails or the token lacks the `Student` role (step 2). | Access denied; no catalogue data is returned. |
| EF-2 | Student is serving a late-return booking ban (step 3). | Reservation blocked; the ban reason and end date are shown, with an appeal route to a Lab Technician. |
| EF-3 | Requested duration exceeds 2 hours or the start date is beyond 7 days (step 7). | Request rejected with a field-level validation message; the student may correct and resubmit at step 6. |
| EF-4 | Asset is marked `Out-of-Service` between catalogue listing and submission (step 8). | Reservation rejected; the asset is removed from the availability grid and the student is invited to choose another asset. |
| EF-5 | Notification Service is unreachable (step 10). | The reservation stands (it is already committed); the confirmation is queued for retry and the token remains visible in the portal. |

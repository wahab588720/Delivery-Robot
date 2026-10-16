# Track 1: Indoor Delivery Robot with Safety Zones

## Must-Have Checklist & Implementation Plan

- [ ] **Delivery request service (pickup, drop-off)**
  - *Plan:* Create a custom `DeliveryRequest.srv` interface and a state machine node that navigates `TO_PICKUP` -> `TO_DROPOFF` using Nav2's `NavigateToPose` action, storing incoming requests in a FIFO queue while busy.
- [ ] **Keep-out zone ("wet floor" / restricted room)**
  - *Plan:* Configure a Nav2 keepout costmap filter using a grayscale `.pgm` mask image, and check drop-off coordinates against the mask before accepting a request so invalid goals are rejected with a clear reason.
- [ ] **Slow zone (corridor speed limit)**
  - *Plan:* Configure a Nav2 speed-limit costmap filter with a zone mask that publishes speed restrictions to cap the controller velocity inside the corridor.
- [ ] **Yielding to a scripted moving "person"**
  - *Plan:* Create a scripted obstacle publisher/actor crossing the robot's path and tune local costmap inflation and range check logic so the robot slows, pauses, or reroutes without collision before resuming.
- [ ] **Simulated battery monitor and auto-docking**
  - *Plan:* Subscribe to a `/battery_level` topic; when below the threshold (e.g., 20%), safely finish or abort the active leg, navigate to the dock coordinates (`RETURNING` -> `CHARGING`), and reject new requests until recharged.
- [ ] **Status topic publishing state and rejection reasons**
  - *Plan:* Publish a `/delivery_status` topic reporting the current state (`IDLE`, `TO_PICKUP`, `TO_DROPOFF`, `RETURNING`, `CHARGING`) and the latest rejection reason.

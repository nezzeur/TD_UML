# Design Patterns Implemented

| Pattern | Class(es) | Purpose |
|---------|-----------|---------|
| **Singleton** | `RideSharingService` | Ensures single instance, thread-safe with double-check locking and `threading.Lock` |
| **Builder** | `Trip.TripBuilder` (internal class) | Fluent construction of Trip objects with validation |
| **Strategy** | `PricingStrategy`, `DriverMatchingStrategy` | Pluggable algorithms for fare calculation and driver selection |
| **State** | `TripState` + 5 states | Models trip lifecycle: REQUESTED → ASSIGNED → IN_PROGRESS → COMPLETED |
| **Observer** | `TripObserver` interface → `User` → `Rider`, `Driver` | Notifies interested parties on trip state changes |

## State Machine (Trip)
- **RequestedState**: Trip requested, waiting for assignment
- **AssignedState**: Driver assigned to trip
- **InProgressState**: Trip in progress (driver has picked up rider)
- **CompletedState**: Trip completed
- **CancelledState**: MISSING (exists in enum but no state class)

## Strategies Available
- **Pricing**: `FlatRatePricingStrategy`, `VehicleBasedPricingStrategy`
- **Driver Matching**: Closest distance algorithm

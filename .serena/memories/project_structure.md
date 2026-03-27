# Project Structure Summary

## File Organization

```
TD_UML/
├── Core Domain
│   ├── user.py              # User base class (Observer pattern)
│   ├── rider.py             # Passenger implementation
│   ├── driver.py            # Driver implementation
│   ├── vehicle.py           # Vehicle info
│   ├── location.py          # GPS coordinates (Euclidean distance - ISSUE)
│   ├── trip.py              # Main Trip entity + TripBuilder
│   └── enums.py             # TripStatus, DriverStatus, RideType
│
├── Service Layer
│   ├── ride_sharing_service.py   # Singleton facade
│   ├── pricing_strategy.py       # Strategy pattern (2 implementations)
│   └── driver_matching_strategy.py # Driver selection strategy
│
├── State Pattern
│   ├── trip_states.py        # 5 state classes (missing CancelledState)
│   └── trip_observer.py      # Observer interface
│
├── Configuration & Patterns
│   └── DynamicPriceStrategy.py # Additional pricing strategy
│
├── Documentation
│   ├── README.md             # Project brief
│   ├── PRESENTATION.md       # Analysis & improvements doc
│   ├── diagramme_*.puml      # PlantUML diagrams
│   └── *.png                 # Generated diagrams
│
└── Demo & Tools
    ├── ride_sharing_demo.py  # Main executable
    └── generate_drawio.py    # UML generation tool
```

## Call Flow Example

```
1. User requests ride
   ↓
2. RideSharingService.request_ride(rider, locations)
   ↓
3. TripBuilder creates Trip
   ↓
4. Trip starts in RequestedState
   ↓
5. RideSharingService finds closest Driver
   ↓
6. Trip transitions to AssignedState
   ↓
7. TripObservers notified (Rider, Driver receive updates)
   ↓
8. Driver accepts → InProgressState
   ↓
9. Driver picks up → still InProgressState
   ↓
10. Driver drops off → CompletedState
    ↓
11. All observers notified of completion
```

## Data Flow

```
Request:
  Rider → RideSharingService → Trip + State + Pricing
                                   ↓
                               Observers
                              (Rider, Driver)

Response:
  Trip updates state → Notifies all observers → Console output
```

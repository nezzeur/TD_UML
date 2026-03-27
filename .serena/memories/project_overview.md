# TD UML - Ride Sharing Project Overview

## Project Purpose
A reverse-engineering educational project to understand an existing codebase and produce UML class diagrams. The codebase simulates a **ride-sharing service (Uber-like)** where:
- **Riders** request rides
- The system finds the closest **Driver**
- A **Trip** is created with calculated **fare**
- The trip lifecycle is managed through state transitions
- Notifications are sent to observers (Observer pattern)

## Core Domain Entities
- **Trip**: Main business entity representing a ride from pickup to dropoff
- **User** (abstract): Base class for Rider and Driver
- **Rider**: Passenger requesting a ride
- **Driver**: Driver accepting and completing rides
- **Vehicle**: Driver's vehicle with model, registration, type
- **Location**: GPS coordinates with distance calculation
- **RideSharingService**: Singleton facade managing the entire system

## Tech Stack
- **Language**: Python 3.x
- **Type hints**: Used throughout with `typing` and `TYPE_CHECKING`
- **Design Patterns**: Singleton, Builder, Strategy, State, Observer
- **Testing**: Executable demo script (`ride_sharing_demo.py`)
- **UML**: PlantUML files for architecture documentation

## Key Statistics
- 15 main Python files
- Heavy use of abstract base classes (ABC)
- No external dependencies (pure Python)

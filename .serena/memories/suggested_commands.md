# Important Commands for Development

## Python Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Verify Python version
python --version
```

## Running & Testing
```bash
# Execute the demo (main entry point)
python ride_sharing_demo.py

# Run specific module for testing
python -m trip
python -m rider
```

## Code Analysis & Linting
```bash
# Type checking (if mypy installed)
mypy *.py

# Code formatting (if black installed)
black .

# Linting (if pylint installed)
pylint *.py
```

## Git Commands (for tracking changes)
```bash
git status
git log --oneline
git diff
git add .
git commit -m "message"
```

## Project-Specific Files
- **Entry point**: `ride_sharing_demo.py`
- **Service**: `ride_sharing_service.py` (Singleton facade)
- **Core entity**: `trip.py` (with TripBuilder)
- **State machine**: `trip_states.py` (5 state classes)
- **Strategies**: `pricing_strategy.py`, `driver_matching_strategy.py`
- **UML diagrams**: `diagramme_*.puml` files

## Development Workflow
1. Understand the main service: `RideSharingService`
2. Trace entity creation in `trip.py`
3. Follow state transitions in `trip_states.py`
4. Understand observer pattern via `trip_observer.py`
5. Examine strategies in `pricing_strategy.py` and `driver_matching_strategy.py`

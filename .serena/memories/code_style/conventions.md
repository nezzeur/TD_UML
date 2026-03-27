# Code Style & Conventions

## Naming Conventions
- **Classes**: PascalCase (e.g., `RideSharingService`, `TripBuilder`)
- **Methods/Functions**: snake_case (e.g., `get_instance`, `add_observer`)
- **Private attributes**: `_prefix` (e.g., `_riders`, `_drivers`, `_trips`)
- **Constants**: Enums (e.g., `TripStatus`, `DriverStatus`, `RideType`)

## Type Hints
- ✅ All methods have type hints for parameters and return types
- ✅ Uses `TYPE_CHECKING` to avoid circular imports
- ✅ Forward references as strings: `'Trip'`, `'Driver'`
- ✅ Uses `Optional`, `List`, `Dict` from `typing`

## Code Style
- ✅ Clean separation of concerns
- ✅ Getter methods for accessing private attributes
- ✅ Uses `__str__` for string representation
- ✅ Abstract base classes via `ABC` and `@abstractmethod`
- ✅ Logging via `print()` (should be replaced with `logging` module)

## Pattern Examples
```python
# Getter pattern
def get_id(self) -> str:
    return self._id

# String representation
def __str__(self) -> str:
    return f"Trip({self._id})"

# Type checking with forward reference
if TYPE_CHECKING:
    from trip import Trip
```

## Best Practices Used
- ✅ No hardcoded values - uses enums and strategies
- ✅ Fluent builder pattern for object construction
- ✅ Composition over inheritance (multiple composition relationships)

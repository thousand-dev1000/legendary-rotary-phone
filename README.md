# Legendary Rotary Phone Simulator

A Python simulation of a classic rotary telephone that demonstrates sequential input handling, state management, and simulated delays based on authentic rotary phone mechanics.

## Features

✨ **Authentic Rotary Mechanics**
- Simulates real rotary dialing delays based on digit value (0 = 10 pulses, 1-9 = 1-9 pulses)
- Each pulse takes 100ms, creating realistic timing
- Inter-digit delays to simulate the mechanical nature of rotary phones

🔧 **Core Functionality**
- Accept digits 0-9 as individual inputs
- Dial complete phone numbers
- Maintain internal state for the current dialed number
- Initiate calls and disconnect
- Call history tracking
- Status reporting

⚠️ **Error Handling**
- Validates input digits
- Prevents dialing while connected
- Handles edge cases gracefully
- Descriptive error messages

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Requires Python 3.6+
python legendary_rotary_phone.py
```

## Usage

### Basic Usage

```python
from legendary_rotary_phone import RotaryPhone

# Create a phone instance
phone = RotaryPhone()

# Dial individual digits
phone.dial_digit('5')
phone.dial_digit('5')
phone.dial_digit('5')
phone.dial_digit('1')
phone.dial_digit('2')
phone.dial_digit('3')
phone.dial_digit('4')

# Initiate the call
phone.call()

# Hang up when done
phone.hang_up()
```

### Dial a Complete Number

```python
# Dial an entire number at once
phone.dial_number("2125551234")

# Make the call
phone.call()

# End the call
phone.hang_up()
```

### Check Status

```python
# View current phone status
phone.status()

# Get the current dialed number
current = phone.get_dialed_number()
print(f"Currently dialed: {current}")

# View call history
history = phone.get_call_log()
print(f"Calls made: {history}")
```

### Clear Dialed Number

```python
# Clear the current dialed number (useful for mistakes)
phone.clear()
```

## API Reference

### `RotaryPhone` Class

#### Constructor
```python
RotaryPhone(phone_number: Optional[str] = None)
```

#### Methods

- **`dial_digit(digit: str) -> None`**
  - Dial a single digit (0-9) with simulated rotary delay
  - Raises: `ValueError` if invalid digit, `RuntimeError` if already connected

- **`dial_number(phone_number: str) -> None`**
  - Dial a complete phone number digit by digit
  - Raises: `ValueError` if invalid format, `RuntimeError` if already connected

- **`call() -> bool`**
  - Initiate a call to the dialed number
  - Returns: `True` on success
  - Raises: `RuntimeError` if no digits have been dialed

- **`hang_up() -> None`**
  - Disconnect the current call

- **`clear() -> None`**
  - Clear the dialed number

- **`get_dialed_number() -> str`**
  - Return the currently dialed number

- **`get_call_log() -> List[str]`**
  - Return list of all numbers that have been called

- **`status() -> None`**
  - Print current phone status to console

## How It Works

### Rotary Dialing Simulation

Real rotary phones work by converting digits into electrical pulses:
- **Digit 1**: 1 pulse = 100ms
- **Digit 2**: 2 pulses = 200ms
- **Digit 3**: 3 pulses = 300ms
- ... and so on ...
- **Digit 0**: 10 pulses = 1000ms

This simulator faithfully reproduces these delays, making digit 0 the slowest to dial!

### State Management

The phone maintains internal state for:
- Currently dialed digits
- Connection status
- Call history
- Phone number accumulation

## Running the Examples

The script includes comprehensive examples:

```bash
python legendary_rotary_phone.py
```

This will demonstrate:
1. Dialing digit by digit
2. Dialing a complete number
3. Error handling
4. Interactive mode (optional user input)
5. Call history and status reporting

## Requirements

- Python 3.6 or higher
- No external packages (uses only `time`, `re`, and `typing` from stdlib)

## Design Philosophy

This simulator embodies the spirit of the "Legendary Rotary Phone" concept:
- **Legacy System Simulation**: Authentically reproduces mechanical telephone behavior
- **Sequential Workflows**: Enforces step-by-step digit input (no all-at-once dialing without proper simulation)
- **State-Driven Design**: Clear state management (dialing vs. connected)
- **Deterministic Behavior**: Timing and state transitions are predictable and reproducible
- **Backward Compatibility**: Simple API works like a real rotary phone

## License

Educational and demonstration purposes. Use freely!

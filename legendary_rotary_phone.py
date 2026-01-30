#!/usr/bin/env python3
"""
Legendary Rotary Phone Simulator

A simulation of a classic rotary telephone that demonstrates:
- Sequential digit input (0-9)
- Rotary dialing delays based on digit value
- Internal state management for dialed numbers
- Call initiation and error handling
"""

import time
import re
from typing import List, Optional


class RotaryPhone:
    """Simulates the behavior of a classic rotary telephone."""
    
    # Rotary dialing delay per digit (milliseconds per unit)
    DELAY_PER_UNIT = 100  # 100ms per rotary pulse
    
    # Digit to pulse count mapping (0 has 10 pulses in rotary phones)
    PULSE_MAP = {
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, '0': 10
    }
    
    # Inter-digit delay (pause between digits)
    INTER_DIGIT_DELAY = 0.5  # 500ms between digits
    
    def __init__(self, phone_number: Optional[str] = None):
        """
        Initialize the rotary phone.
        
        Args:
            phone_number: Optional initial phone number to dial
        """
        self.dialed_number: List[str] = []
        self.is_connected = False
        self.call_log: List[str] = []
        
        if phone_number:
            self._validate_phone_number(phone_number)
            self.dialed_number = list(phone_number)
    
    def _validate_phone_number(self, number: str) -> None:
        """
        Validate that the input contains only digits.
        
        Args:
            number: The phone number to validate
            
        Raises:
            ValueError: If the number contains invalid characters
        """
        if not re.match(r'^\d+$', number):
            raise ValueError(
                f"Invalid phone number '{number}'. "
                "Only digits 0-9 are allowed."
            )
    
    def dial_digit(self, digit: str) -> None:
        """
        Dial a single digit (0-9) with simulated rotary delay.
        
        Args:
            digit: A single digit character ('0' through '9')
            
        Raises:
            ValueError: If the digit is invalid or already connected
            RuntimeError: If trying to dial while connected
        """
        if self.is_connected:
            raise RuntimeError(
                "Cannot dial while already connected. Hang up first."
            )
        
        if digit not in self.PULSE_MAP:
            raise ValueError(
                f"Invalid digit '{digit}'. "
                "Only digits 0-9 are allowed."
            )
        
        # Simulate rotary dialing delay
        pulses = self.PULSE_MAP[digit]
        delay_seconds = (pulses * self.DELAY_PER_UNIT) / 1000
        
        print(f"Dialing {digit}... ", end="", flush=True)
        time.sleep(delay_seconds)
        print(f"[{delay_seconds:.2f}s]")
        
        self.dialed_number.append(digit)
        
        # Inter-digit delay (brief pause before next digit)
        if digit != self.dialed_number[-1] or len(self.dialed_number) > 1:
            time.sleep(self.INTER_DIGIT_DELAY)
    
    def dial_number(self, phone_number: str) -> None:
        """
        Dial a complete phone number digit by digit.
        
        Args:
            phone_number: A string of digits to dial
            
        Raises:
            ValueError: If the phone number is invalid
            RuntimeError: If already connected
        """
        self._validate_phone_number(phone_number)
        
        print(f"\nStarting to dial: {phone_number}")
        print("-" * 40)
        
        for digit in phone_number:
            self.dial_digit(digit)
    
    def call(self) -> bool:
        """
        Initiate a call to the dialed number.
        
        Returns:
            True if the call was successfully initiated
            
        Raises:
            RuntimeError: If no digits have been dialed
        """
        if not self.dialed_number:
            raise RuntimeError(
                "Cannot initiate a call. No digits dialed."
            )
        
        phone_number = ''.join(self.dialed_number)
        print("\n" + "=" * 40)
        print(f"Calling: {phone_number}")
        print("=" * 40)
        time.sleep(1)
        print("📞 Connected!")
        print(f"Status: Call in progress with {phone_number}")
        
        self.is_connected = True
        self.call_log.append(phone_number)
        
        return True
    
    def hang_up(self) -> None:
        """Disconnect the current call."""
        if not self.is_connected:
            print("No active call to hang up.")
            return
        
        print("\n" + "-" * 40)
        print("📞 Hanging up...")
        time.sleep(0.5)
        print("Call ended.")
        print("-" * 40)
        
        self.is_connected = False
        self.dialed_number.clear()
    
    def clear(self) -> None:
        """Clear the dialed number (useful if a mistake was made)."""
        self.dialed_number.clear()
        print("Dialed number cleared.")
    
    def get_dialed_number(self) -> str:
        """Return the currently dialed number as a string."""
        return ''.join(self.dialed_number)
    
    def get_call_log(self) -> List[str]:
        """Return the list of all numbers called."""
        return self.call_log.copy()
    
    def status(self) -> None:
        """Print the current status of the phone."""
        print("\n" + "=" * 40)
        print("ROTARY PHONE STATUS")
        print("=" * 40)
        print(f"Dialed Number: {self.get_dialed_number() or '(none)'}")
        print(f"Connected: {'Yes' if self.is_connected else 'No'}")
        print(f"Calls Made: {len(self.call_log)}")
        if self.call_log:
            print(f"Call History: {', '.join(self.call_log)}")
        print("=" * 40 + "\n")


def main():
    """Sample usage of the Legendary Rotary Phone."""
    
    print("\n" + "*" * 40)
    print("LEGENDARY ROTARY PHONE SIMULATOR")
    print("*" * 40 + "\n")
    
    # Create a new rotary phone
    phone = RotaryPhone()
    
    try:
        # Example 1: Dial a number digit by digit
        print("Example 1: Dialing number digit by digit\n")
        phone.dial_digit('5')
        phone.dial_digit('5')
        phone.dial_digit('5')
        phone.dial_digit('1')
        phone.dial_digit('2')
        phone.dial_digit('3')
        phone.dial_digit('4')
        
        # Check status before calling
        phone.status()
        
        # Initiate the call
        phone.call()
        time.sleep(2)  # Simulate call duration
        phone.hang_up()
        
        # Example 2: Dial a complete number
        print("\n\nExample 2: Dialing a complete number\n")
        phone.dial_number("2125551234")
        phone.call()
        time.sleep(2)
        phone.hang_up()
        
        # Example 3: Show call history
        phone.status()
        
        # Example 4: Error handling
        print("\nExample 3: Demonstrating error handling\n")
        try:
            phone.dial_digit('A')
        except ValueError as e:
            print(f"❌ Error caught: {e}")
        
        try:
            phone.call()
        except RuntimeError as e:
            print(f"❌ Error caught: {e}")
        
        # Example 4: Interactive dialing
        print("\n\nExample 4: Interactive mode (dial any 5-digit number)\n")
        interactive_number = input("Enter a 5-digit number to dial (or press Enter to skip): ").strip()
        
        if interactive_number:
            try:
                phone.dial_number(interactive_number)
                phone.call()
                time.sleep(1)
                phone.hang_up()
            except ValueError as e:
                print(f"❌ Error: {e}")
        
        # Final status
        phone.status()
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        if phone.is_connected:
            phone.hang_up()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Legendary Rotary Phone Simulator

A simulation of a classic rotary telephone that demonstrates:
- Sequential digit input (0-9)
- Rotary dialing delays based on digit value
- Internal state management for dialed numbers
- Call initiation and error handling
- Voicemail / answering machine
- Incoming call simulation
- Speed dial
"""

import time
import re
import sys
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict

try:
    import websockets
except Exception:
    websockets = None

logger = logging.getLogger(__name__)


class Voicemail:
    def __init__(self, from_number: str, message: str):
        self.from_number = from_number
        self.message = message
        self.timestamp = datetime.now()

    def __repr__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{ts}] From {self.from_number}: {self.message}"


class RotaryPhone:
    PULSE_DURATION = 0.1       # 100ms per pulse
    INTER_DIGIT_DELAY = 0.5    # 500ms between digits

    def __init__(
        self,
        phone_number: Optional[str] = None,
        ring_count: int = 4,
        call_timeout: int = 30,
    ):
        self._own_number = phone_number
        self._dialed_digits: List[str] = []
        self._connected = False
        self._call_log: List[Dict] = []
        self._speed_dial: Dict[str, str] = {}
        self._voicemails: List[Voicemail] = []
        self._ring_count = ring_count
        self._call_timeout = call_timeout
        self._call_start_time: Optional[float] = None
        self._incoming_caller: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Core dialing                                                         #
    # ------------------------------------------------------------------ #

    def _simulate_pulse(self, digit: str) -> None:
        pulses = 10 if digit == "0" else int(digit)
        for _ in range(pulses):
            time.sleep(self.PULSE_DURATION)
        time.sleep(self.INTER_DIGIT_DELAY)

    def dial_digit(self, digit: str, speed: bool = False) -> None:
        """Dial a single digit (0-9), or activate a speed-dial key when speed=True."""
        if self._connected:
            raise RuntimeError("Cannot dial while connected")
        if speed:
            key = str(digit)
            if key not in self._speed_dial:
                raise ValueError(f"No speed dial set for key {key!r}")
            number = self._speed_dial[key]
            print(f"Speed dial {key!r} -> {number}")
            self.dial_number(number)
            return
        if digit not in "0123456789":
            raise ValueError(f"Invalid digit: {digit!r}. Must be 0-9")
        print(f"Dialing digit: {digit}")
        self._simulate_pulse(digit)
        self._dialed_digits.append(digit)

    def dial_number(self, phone_number: str) -> None:
        """Dial a complete phone number digit by digit."""
        if self._connected:
            raise RuntimeError("Cannot dial while connected")
        cleaned = re.sub(r"[\s\-\(\)\+]", "", phone_number)
        if not re.match(r"^\d+$", cleaned):
            raise ValueError(f"Invalid phone number: {phone_number!r}")
        print(f"Dialing number: {phone_number}")
        for digit in cleaned:
            self._simulate_pulse(digit)
            self._dialed_digits.append(digit)

    def call(self) -> bool:
        """Initiate a call to the currently dialed number."""
        if not self._dialed_digits:
            raise RuntimeError("No number dialed")
        if self._connected:
            raise RuntimeError("Already connected")
        number = self.get_dialed_number()
        print(f"Calling {number}...")
        time.sleep(1.5)  # simulate ring before answer
        self._connected = True
        self._call_start_time = time.time()
        self._call_log.append(
            {
                "number": number,
                "timestamp": datetime.now(),
                "type": "outgoing",
                "answered": True,
                "duration": None,
            }
        )
        print(f"Connected to {number}")
        return True

    def hang_up(self) -> None:
        """Disconnect the current call."""
        if self._connected:
            duration = time.time() - (self._call_start_time or time.time())
            if self._call_log:
                self._call_log[-1]["duration"] = round(duration, 1)
            print(f"Call ended. Duration: {duration:.1f}s")
        self._connected = False
        self._call_start_time = None
        self._incoming_caller = None
        self._dialed_digits = []

    def clear(self) -> None:
        """Clear the dialed number (cannot clear while connected)."""
        if self._connected:
            raise RuntimeError("Cannot clear while connected")
        self._dialed_digits = []
        print("Dialed number cleared")

    def get_dialed_number(self) -> str:
        return "".join(self._dialed_digits)

    def get_call_log(self) -> List[Dict]:
        return list(self._call_log)

    def status(self) -> None:
        print("=" * 42)
        print(f"  Phone:      {self._own_number or 'Unknown'}")
        print(f"  Status:     {'Connected' if self._connected else 'On Hook'}")
        print(f"  Dialed:     {self.get_dialed_number() or '(none)'}")
        print(f"  Calls:      {len(self._call_log)}")
        print(f"  Voicemails: {len(self._voicemails)}")
        print(f"  Speed dials:{len(self._speed_dial)}")
        print("=" * 42)

    # ------------------------------------------------------------------ #
    # Feature 3: Speed Dial                                               #
    # ------------------------------------------------------------------ #

    def set_speed_dial(self, key: str, number: str) -> None:
        """Assign a phone number to a speed-dial key."""
        key = str(key)
        cleaned = re.sub(r"[\s\-\(\)\+]", "", number)
        if not re.match(r"^\d+$", cleaned):
            raise ValueError(f"Invalid phone number: {number!r}")
        self._speed_dial[key] = cleaned
        print(f"Speed dial {key!r} -> {cleaned}")

    def get_speed_dial(self) -> Dict[str, str]:
        return dict(self._speed_dial)

    # ------------------------------------------------------------------ #
    # Feature 2: Incoming Call Simulation                                 #
    # ------------------------------------------------------------------ #

    def receive_call(self, from_number: str, auto_answer: bool = False) -> bool:
        """
        Simulate an incoming call from from_number.

        Rings ring_count times.  If auto_answer is True the call is answered
        immediately; otherwise it rolls to voicemail.
        Returns True if answered, False if sent to voicemail.
        """
        if self._connected:
            print(f"Busy. Call from {from_number} rejected.")
            return False

        print(f"\nIncoming call from: {from_number}")
        self._incoming_caller = from_number

        for i in range(self._ring_count):
            print(f"  RING RING... ({i + 1}/{self._ring_count})")
            time.sleep(1.5)
            if auto_answer:
                break

        if auto_answer:
            self._connected = True
            self._call_start_time = time.time()
            self._call_log.append(
                {
                    "number": from_number,
                    "timestamp": datetime.now(),
                    "type": "incoming",
                    "answered": True,
                    "duration": None,
                }
            )
            print(f"Answered call from {from_number}")
            return True

        print(f"No answer. Directing {from_number} to voicemail.")
        self._call_log.append(
            {
                "number": from_number,
                "timestamp": datetime.now(),
                "type": "incoming",
                "answered": False,
                "duration": 0,
            }
        )
        self._incoming_caller = from_number  # kept so leave_voicemail can use it
        return False

    # ------------------------------------------------------------------ #
    # Feature 1: Voicemail / Answering Machine                            #
    # ------------------------------------------------------------------ #

    def leave_voicemail(self, message: str, from_number: Optional[str] = None) -> None:
        """Record a voicemail. Uses the last known incoming caller if from_number is omitted."""
        caller = from_number or self._incoming_caller or "Unknown"
        vm = Voicemail(caller, message)
        self._voicemails.append(vm)
        print(f"Voicemail recorded from {caller}")
        self._incoming_caller = None

    def play_voicemail(self, index: Optional[int] = None) -> Optional[Voicemail]:
        """
        Play voicemail(s).  Pass an index (0-based) to play a single message,
        or omit to list all.
        """
        if not self._voicemails:
            print("No voicemails.")
            return None

        if index is not None:
            if index < 0 or index >= len(self._voicemails):
                raise IndexError(f"No voicemail at index {index}")
            vm = self._voicemails[index]
            print(f"\n--- Voicemail {index + 1} of {len(self._voicemails)} ---")
            print(repr(vm))
            return vm

        print(f"\n--- {len(self._voicemails)} Voicemail(s) ---")
        for i, vm in enumerate(self._voicemails):
            print(f"  {i + 1}. {vm!r}")
        return None

    def delete_voicemail(self, index: int) -> None:
        if index < 0 or index >= len(self._voicemails):
            raise IndexError(f"No voicemail at index {index}")
        self._voicemails.pop(index)
        print(f"Voicemail {index + 1} deleted.")

    def get_voicemails(self) -> List[Voicemail]:
        return list(self._voicemails)


# --------------------------------------------------------------------------- #
# WebSocket chat client (rotary-style)                                        #
# --------------------------------------------------------------------------- #

async def _ws_client(uri: str) -> None:
    if websockets is None:
        print("websockets package not installed. Run: pip install websockets")
        return
    print(f"Connecting to {uri} ...")
    async with websockets.connect(uri) as ws:
        print("Connected. Type messages and press Enter. Ctrl-C to quit.")

        async def recv_loop() -> None:
            async for msg in ws:
                print(f"\r[received] {msg}\n> ", end="", flush=True)

        recv_task = asyncio.create_task(recv_loop())
        try:
            loop = asyncio.get_event_loop()
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                line = line.rstrip("\n")
                if line:
                    await ws.send(line)
                    print("> ", end="", flush=True)
        except (KeyboardInterrupt, EOFError):
            recv_task.cancel()


# --------------------------------------------------------------------------- #
# Entry point                                                                 #
# --------------------------------------------------------------------------- #

def _demo() -> None:
    logging.basicConfig(level=logging.WARNING)
    phone = RotaryPhone(phone_number="555-0001")

    print("\n=== 1. Basic digit dialing ===")
    for d in "5551234":
        phone.dial_digit(d)
    phone.call()
    phone.hang_up()

    print("\n=== 2. dial_number shortcut ===")
    phone.dial_number("212-555-9876")
    phone.call()
    phone.hang_up()

    print("\n=== 3. Speed dial ===")
    phone.set_speed_dial("1", "800-555-0000")
    phone.dial_digit("1", speed=True)
    phone.call()
    phone.hang_up()

    print("\n=== 4. Incoming call -> voicemail ===")
    answered = phone.receive_call("917-555-4321", auto_answer=False)
    if not answered:
        phone.leave_voicemail("Hey, call me back when you get a chance!")
    phone.play_voicemail()

    print("\n=== 5. Incoming call -> auto-answer ===")
    phone.receive_call("646-555-7777", auto_answer=True)
    phone.hang_up()

    print("\n=== 6. Status ===")
    phone.status()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        uri = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:8765/room1"
        asyncio.run(_ws_client(uri))
    else:
        _demo()

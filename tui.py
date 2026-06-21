#!/usr/bin/env python3
"""
Interactive Curses TUI for the Legendary Rotary Phone Simulator.

The dial face shows digits 1-9 and 0 arranged in a circle.
Use Left / Right arrow keys to rotate the finger hole to a digit,
then press Enter (or Space) to dial it.

Keyboard shortcuts
------------------
  Left / Right  Rotate the dial
  Enter / Space  Dial the selected digit
  C              Call (dial current number)
  H              Hang up
  R              Redial last number
  S              Set speed dial (prompts for key then number)
  V              View voicemails
  Backspace      Clear dialed number
  Q / Esc        Quit
"""

import curses
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phone.legendary_rotary_phone import RotaryPhone  # noqa: E402

# Digits in clockwise order starting from ~1 o'clock (matches a real rotary dial)
DIAL_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

# Aspect-ratio-corrected radii for the oval dial
RADIUS_X = 11
RADIUS_Y = 5

# Angle offset so digit '1' sits at ~1 o'clock (36° clockwise from 12 o'clock)
START_ANGLE_DEG = 36


def _digit_offsets() -> list[tuple[int, int, str]]:
    """Return list of (col_offset, row_offset, digit) for all 10 dial positions."""
    positions = []
    for i, digit in enumerate(DIAL_ORDER):
        angle_deg = START_ANGLE_DEG + i * 36
        angle_rad = math.radians(angle_deg)
        # In curses row increases downward, so we negate the cos term
        col = int(round(RADIUS_X * math.sin(angle_rad)))
        row = int(round(RADIUS_Y * -math.cos(angle_rad)))
        positions.append((col, row, digit))
    return positions


DIAL_POSITIONS = _digit_offsets()

# Minimum terminal size required
MIN_ROWS = 28
MIN_COLS = 60


def _draw_dial(win, cy: int, cx: int, selected_idx: int) -> None:
    """Draw the circular rotary dial with the selected digit highlighted."""
    # Outer oval (approximate with spaces and border chars)
    win.addstr(cy, cx, "( ● )", curses.A_DIM)

    for col_off, row_off, digit in DIAL_POSITIONS:
        r = cy + row_off
        c = cx + col_off * 2  # multiply col by 2 for character-cell aspect ratio

        is_selected = DIAL_ORDER.index(digit) == selected_idx
        attr = curses.color_pair(2) | curses.A_BOLD if is_selected else curses.color_pair(1)
        label = f"[{digit}]" if is_selected else f" {digit} "
        try:
            win.addstr(r, c - 1, label, attr)
        except curses.error:
            pass


def _draw_frame(win, rows: int, cols: int) -> None:
    """Draw the outer box and static labels."""
    win.clear()
    try:
        # Top border
        win.addstr(0, 0, "╔" + "═" * (cols - 2) + "╗")
        win.addstr(1, 0, "║")
        title = " LEGENDARY ROTARY PHONE "
        win.addstr(1, (cols - len(title)) // 2, title, curses.A_BOLD)
        win.addstr(1, cols - 1, "║")
        win.addstr(2, 0, "╠" + "═" * (cols - 2) + "╣")

        # Info row
        win.addstr(3, 0, "║")
        win.addstr(3, cols - 1, "║")
        win.addstr(4, 0, "║")
        win.addstr(4, cols - 1, "║")

        # Divider before dial
        win.addstr(5, 0, "╠" + "═" * (cols - 2) + "╣")

        # Rows for the dial area (rows 6-18)
        for r in range(6, 19):
            win.addstr(r, 0, "║")
            win.addstr(r, cols - 1, "║")

        # Divider after dial
        win.addstr(19, 0, "╠" + "═" * (cols - 2) + "╣")

        # Status row
        for r in range(20, 24):
            win.addstr(r, 0, "║")
            win.addstr(r, cols - 1, "║")

        # Keyboard shortcuts
        win.addstr(24, 0, "╠" + "═" * (cols - 2) + "╣")
        for r in range(25, rows - 1):
            win.addstr(r, 0, "║")
            win.addstr(r, cols - 1, "║")
        win.addstr(rows - 1, 0, "╚" + "═" * (cols - 2) + "╝")

        # Static key-hint lines
        hints = [
            " ← →: Rotate dial    Enter/Space: Dial selected digit",
            " C: Call   H: Hang up   R: Redial   Backspace: Clear",
            " S: Set speed dial   V: View voicemails   Q: Quit",
        ]
        for i, hint in enumerate(hints):
            win.addstr(25 + i, 2, hint, curses.A_DIM)
    except curses.error:
        pass


def _draw_info(win, cols: int, phone: RotaryPhone, selected_idx: int, message: str) -> None:
    """Redraw the dynamic info area (rows 3-4 and 20-23)."""
    dialed = phone.get_dialed_number()
    status = "CONNECTED" if phone._connected else "On Hook"
    vms = len(phone._voicemails)
    speed = len(phone._speed_dial)

    # Number / status
    try:
        num_line = f"  Number: {dialed or '(none)':.<30}  "
        win.addstr(3, 1, num_line.ljust(cols - 2))
        stat_line = f"  Status: {status:<12}  Voicemails: {vms}   Speed dials: {speed}  "
        win.addstr(4, 1, stat_line.ljust(cols - 2))

        # Selected digit label (centre, row 20)
        sel_digit = DIAL_ORDER[selected_idx]
        sel_label = f"  Selected: [ {sel_digit} ]   (press Enter or Space to dial)"
        win.addstr(20, 1, sel_label.ljust(cols - 2), curses.color_pair(2))

        # Message / feedback row
        win.addstr(21, 1, ("  " + message).ljust(cols - 2), curses.color_pair(3))
        win.addstr(22, 1, " " * (cols - 2))
        win.addstr(23, 1, " " * (cols - 2))
    except curses.error:
        pass


def _prompt(win, rows: int, cols: int, prompt_text: str) -> str:
    """Show a mini input prompt at the bottom of the status area and return user input."""
    curses.echo()
    curses.curs_set(1)
    win.addstr(22, 2, prompt_text + " " * (cols - len(prompt_text) - 4))
    win.addstr(23, 2, "> ")
    win.refresh()
    raw = win.getstr(23, 4, cols - 8)
    curses.noecho()
    curses.curs_set(0)
    return raw.decode("utf-8", errors="ignore").strip()


def _tui_main(stdscr) -> None:
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_WHITE, -1)    # normal digit
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # selected digit / selected label
    curses.init_pair(3, curses.COLOR_GREEN, -1)    # feedback messages
    curses.init_pair(4, curses.COLOR_RED, -1)      # error messages

    rows, cols = stdscr.getmaxyx()
    if rows < MIN_ROWS or cols < MIN_COLS:
        stdscr.addstr(0, 0, f"Terminal too small! Need {MIN_COLS}x{MIN_ROWS}, got {cols}x{rows}")
        stdscr.getch()
        return

    phone = RotaryPhone(phone_number="555-0001", ring_count=3)
    selected_idx = 0
    message = "Welcome! Use ← → to rotate, Enter to dial."

    _draw_frame(stdscr, rows, cols)

    # Dial centre
    dial_cy = 12
    dial_cx = cols // 2

    while True:
        _draw_dial(stdscr, dial_cy, dial_cx, selected_idx)
        _draw_info(stdscr, cols, phone, selected_idx, message)
        stdscr.refresh()

        key = stdscr.getch()

        if key in (ord("q"), ord("Q"), 27):  # Q or Esc
            break

        elif key == curses.KEY_LEFT:
            selected_idx = (selected_idx - 1) % 10
            message = f"Rotated to digit {DIAL_ORDER[selected_idx]}"

        elif key == curses.KEY_RIGHT:
            selected_idx = (selected_idx + 1) % 10
            message = f"Rotated to digit {DIAL_ORDER[selected_idx]}"

        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r"), ord(" ")):
            digit = DIAL_ORDER[selected_idx]
            try:
                # Skip the sleep simulation in TUI mode for responsiveness
                saved_pulse = RotaryPhone.PULSE_DURATION
                saved_delay = RotaryPhone.INTER_DIGIT_DELAY
                RotaryPhone.PULSE_DURATION = 0
                RotaryPhone.INTER_DIGIT_DELAY = 0
                phone.dial_digit(digit)
                RotaryPhone.PULSE_DURATION = saved_pulse
                RotaryPhone.INTER_DIGIT_DELAY = saved_delay
                message = f"Dialed: {digit}   Number so far: {phone.get_dialed_number()}"
            except RuntimeError as e:
                message = f"Error: {e}"

        elif key in (ord("c"), ord("C")):
            try:
                saved_pulse = RotaryPhone.PULSE_DURATION
                saved_delay = RotaryPhone.INTER_DIGIT_DELAY
                RotaryPhone.PULSE_DURATION = 0
                RotaryPhone.INTER_DIGIT_DELAY = 0
                phone.call()
                RotaryPhone.PULSE_DURATION = saved_pulse
                RotaryPhone.INTER_DIGIT_DELAY = saved_delay
                message = f"Connected to {phone.get_dialed_number()}"
            except RuntimeError as e:
                message = f"Error: {e}"

        elif key in (ord("h"), ord("H")):
            num = phone.get_dialed_number()
            phone._connected = False
            phone._call_start_time = None
            phone._dialed_digits = []
            message = f"Hung up from {num or '(no call)'}"

        elif key in (ord("r"), ord("R")):
            log = phone.get_call_log()
            if log:
                last = log[-1]["number"]
                try:
                    saved_pulse = RotaryPhone.PULSE_DURATION
                    saved_delay = RotaryPhone.INTER_DIGIT_DELAY
                    RotaryPhone.PULSE_DURATION = 0
                    RotaryPhone.INTER_DIGIT_DELAY = 0
                    phone.clear()
                    phone.dial_number(last)
                    RotaryPhone.PULSE_DURATION = saved_pulse
                    RotaryPhone.INTER_DIGIT_DELAY = saved_delay
                    message = f"Redialing {last}"
                except RuntimeError as e:
                    message = f"Error: {e}"
            else:
                message = "No previous call to redial."

        elif key in (curses.KEY_BACKSPACE, 127, 8):
            try:
                if phone._dialed_digits:
                    phone._dialed_digits.pop()
                    message = f"Cleared last digit. Number: {phone.get_dialed_number() or '(empty)'}"
                else:
                    phone.clear()
                    message = "Number cleared."
            except RuntimeError as e:
                message = f"Error: {e}"

        elif key in (ord("s"), ord("S")):
            k = _prompt(stdscr, rows, cols, "Speed dial key (e.g. 1):")
            if k:
                num = _prompt(stdscr, rows, cols, f"Number for speed dial {k!r}:")
                if num:
                    try:
                        phone.set_speed_dial(k, num)
                        message = f"Speed dial {k!r} -> {num}"
                    except ValueError as e:
                        message = f"Error: {e}"
            _draw_frame(stdscr, rows, cols)

        elif key in (ord("v"), ord("V")):
            vms = phone.get_voicemails()
            if not vms:
                message = "No voicemails."
            else:
                # Show first voicemail in status area
                vm = vms[0]
                message = f"VM 1/{len(vms)}: {vm.from_number} - {vm.message[:30]}"

        # Unknown keys are silently ignored


def main() -> None:
    curses.wrapper(_tui_main)


if __name__ == "__main__":
    main()

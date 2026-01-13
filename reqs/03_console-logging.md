# Console Logging

Documents the required console log output format for the drift-bg component's internal state reporting.

## $REQ_CONSOLE_001: Log Frequency
**Source:** ./specs/TESTING.md (Section: "Console Logging Requirement")

The `<drift-bg>` component must log its internal state to the console once per second.

## $REQ_CONSOLE_002: Log Format
**Source:** ./specs/TESTING.md (Section: "Console Logging Requirement")

Console log output must follow this format:
```
drift-bg: x=12.34 y=-5.67 z=23.45 u=0.12 v=-0.08 w=0.15
```

## $REQ_CONSOLE_003: Mode Indicator in Log
**Source:** ./specs/TESTING.md (Section: "3. Mouse Interaction Test")

The console log must include a mode indicator: `[SPIRAL` when in Spiral Mode, or `[MOUSE` when in Mouse Mode.

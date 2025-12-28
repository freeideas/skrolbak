# Debug Logging

Documents the console logging of time offset once per second to enable reproducible bug reports.

## $REQ_DEBUG_001: Log Time Offset to Console Every Second
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Debug Logging")

The component logs the current time offset to the console once per second in the format `t=N` where N is the elapsed time in seconds (e.g., `t=0`, `t=1`, `t=2`).

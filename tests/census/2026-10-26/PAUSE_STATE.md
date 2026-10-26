# Serial runner pause - 2026-10-27 01:38 IST

Broad stability paused to prioritize mechanism investigation after seven broken
streaks. SIGSTOP applied to coordinator subshell PID130988, not active test node
PID214031 (color_feedback repeat2). That node may finish naturally; stopped shell
retains wait/exit status until resumed. Its pending TSV row is NOT counted as
complete before the shell records it. Main shell PID124474 waits on subshell.

Before diagnostic execution, verify active node has exited and its browser
processes are gone. No concurrent browser test. SIGCONT130988 later resumes exact
pending result recording and remaining loop; do NOT restart runner (it truncates
status file). All earlier rows/logs are retained. A paused run is not a failure or
pass. Case streak continuity uses actual completed executions only.

choice_runtime_quiet run4 FAIL3s: expected target._revealMotion.playState idle
30ms after runtime quiet setting; actual false. This is a cancellation-state
assertion, not absence of an expired animation. Unresolved; preserve original
contract and inspect identity/state/timing before classification.

"""Run UI with live logging to file."""
import sys
import subprocess

# Run with unbuffered output
process = subprocess.Popen(
    [sys.executable, "-u", "src/ui/canvas_main_window.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    universal_newlines=True
)

log_file = "ui_live.log"
print(f"[Monitor] Logging to {log_file}")
print("[Monitor] UI starting...")

try:
    with open(log_file, "w", encoding="utf-8") as f:
        for line in process.stdout:
            print(line, end="")  # Print to console
            f.write(line)       # Write to file
            f.flush()           # Force flush
except KeyboardInterrupt:
    print("\n[Monitor] Stopped")
    process.terminate()


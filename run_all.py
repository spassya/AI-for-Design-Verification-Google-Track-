import subprocess
import sys

PYTHON = sys.executable

# Take input argument (visible or hidden)
problems_folder = sys.argv[1] if len(sys.argv) > 1 else "visible_problems"

print("=== Generating Testbenches ===")
subprocess.run([
    PYTHON,
    "test_harness/generate_testbenches.py",
    f"--problems_folder={problems_folder}"
], check=True)

print("\n=== Running Evaluation ===")
subprocess.run([
    PYTHON,
    "test_harness/run_evaluation.py",
    f"--problems_folder={problems_folder}"
], check=True)

print("\n=== DONE ===")
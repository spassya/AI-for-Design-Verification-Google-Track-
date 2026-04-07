import subprocess
import sys

PYTHON = sys.executable  # uses whatever python runs this script

print("=== Generating Testbenches ===")
subprocess.run([
    PYTHON,
    "test_harness/generate_testbenches.py",
    "--problems_folder=./visible_problems"
], check=True)

print("\n=== Running Evaluation ===")
subprocess.run([
    PYTHON,
    "test_harness/run_evaluation.py",
    "--problems_folder=./visible_problems"
], check=True)

print("\n=== DONE ===")
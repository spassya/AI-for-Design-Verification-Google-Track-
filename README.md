# AI for Design Verification – Phase 2

## Overview

This project implements an AI agent that automatically generates Verilog testbenches from natural language specifications to identify the correct RTL implementation among multiple candidates.

The agent analyzes:

* Natural language specifications
* Multiple RTL implementations (mutants)

and generates a testbench that:

* Verifies correctness
* Eliminates incorrect implementations

---

## Project Structure

```
test_harness/
  ├── agent.py                  # AI agent implementation
  ├── generate_testbenches.py   # Generates testbenches
  ├── run_evaluation.py         # Runs simulation & scoring

visible_problems/
  ├── cdc_fifo_flops_push_credit
  ├── counter
  ├── credit_receiver
  ├── ecc_sed_encoder
  ├── enc_bin2gray
  ├── enc_bin2onehot
  ├── fifo_flops
  ├── lfsr
  ├── shift_left
  ├── shift_right

run_all.py                      # Single entry point
.gitignore
```

---

## Requirements

* Python **3.10 or higher**
* iVerilog installed and available in PATH

---

## How to Run

### Option 1: Single Entry Point (Recommended)

```bash
python run_all.py

Using Python 3.11 explicitly (recommended if multiple Python versions exist):

py -3.11 run_all.py
```

This will:

1. Generate testbenches
2. Run evaluation on visible problems

---

### Option 2: Manual Commands

Generate testbenches:

```bash
python test_harness/generate_testbenches.py \
  --problems_folder=./visible_problems
```

Run evaluation:

```bash
python test_harness/run_evaluation.py \
  --problems_folder=./visible_problems
```

---

## Approach

The agent identifies module types using keyword matching on the specification and RTL:

* **Counter**

  * Handles reset, reinit, increment/decrement
  * Wrap-around logic verification
  * Cycle-accurate validation using clock

* **Shift Left**

  * Symbol-based shifting (12-bit symbols)
  * Fill value validation
  * Boundary and invalid shift testing

* **Shift Right**

  * Logical right shifting (5-bit symbols)
  * MSB fill behavior
  * Valid/invalid shift handling

Each testbench:

* Computes expected outputs internally
* Compares against DUT outputs
* Reports mismatches using `$display`
* Prints `"TESTS PASSED"` on success

---

## Results (Visible Problems)

* **Counter**: Reduced candidates from 31 → 1 ✅
* **Shift Left**: Reduced candidates from 31 → 2
* **Shift Right**: Reduced candidates from 31 → 2

---

## Notes

* The evaluation shown is a **dry run** (no answers folder provided)
* Final scoring during grading will use hidden testcases
* The agent is designed to generalize to unseen modules

---

## Submission Details

* No hardcoded paths are used
* Uses `sys.executable` for portability
* Compatible with grading environment



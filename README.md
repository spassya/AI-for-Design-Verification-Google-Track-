# AI for Design Verification – Phase 3

## Overview

This project implements an AI agent that automatically generates Verilog/SystemVerilog testbenches from natural language specifications to identify the correct RTL implementation among multiple candidates.

The agent analyzes:

* Natural language specifications  
* Multiple RTL implementations (mutants)  

and generates a testbench that:

* Verifies correctness  
* Eliminates incorrect implementations  
* Identifies exactly one correct RTL  

---

## Project Structure
```
test_harness/
  ├── agent.py                  # AI agent implementation
  ├── generate_testbenches.py   # Generates testbenches
  ├── run_evaluation.py         # Runs simulation & scoring

visible_problems/
  ├── cdc_fifo_flops_push_credit/
  ├── counter/
  ├── credit_receiver/
  ├── ecc_sed_encoder/
  ├── enc_bin2gray/
  ├── enc_bin2onehot/
  ├── fifo_flops/
  ├── lfsr/
  ├── shift_left/
  ├── shift_right/

run_all.py                      # Single entry point
example_outputs/                # Example logs/results
.gitignore
```
---

## Requirements

* Python **3.10 or higher** (recommended: Python 3.11)  
* iVerilog installed and available in PATH  

### Install Python dependencies
```
pip install -r requirements.txt
```
If multiple Python versions are installed:
```
py -3.11 -m pip install -r requirements.txt
```
---

## How to Run

### Option 1: Single Entry Point (Recommended)
```
python run_all.py visible_problems
```
Using Python 3.11 explicitly:
```
py -3.11 run_all.py visible_problems
```
This will:

1. Generate testbenches  
2. Run evaluation on visible problems  

---

### Running Hidden Testcases

Place the hidden testcase folder in the repository root:

hidden_problems/

Then run:
```
python run_all.py hidden_problems
```
---

### Option 2: Manual Commands

Generate testbenches:
```
python test_harness/generate_testbenches.py --problems_folder=./visible_problems
```
Run evaluation:
```
python test_harness/run_evaluation.py --problems_folder=./visible_problems
```
---

## Approach

The agent identifies module types using keyword matching on the specification and RTL.

* Counter  
  - Handles reset, reinitialization, increment/decrement  
  - Verifies wrap-around logic  
  - Uses cycle-accurate validation  

* Shift Left  
  - Symbol-based shifting (12-bit symbols)  
  - Validates fill values  
  - Tests boundary and invalid shift cases  

* Shift Right  
  - Logical right shifting  
  - MSB fill behavior  
  - Valid/invalid shift handling  

* LFSR  
  - Verifies feedback polynomial behavior  
  - Checks sequence progression  
  - Detects incorrect tap positions  

* FIFO (fifo_flops)  
  - Verifies FIFO ordering (push → pop)  
  - Tests full and empty conditions  
  - Validates pointer behavior  

* Credit Receiver  
  - Verifies credit-based flow control  
  - Checks credit increment/decrement  
  - Validates push/pop credit interactions  

* CDC FIFO (cdc_fifo_flops_push_credit)  
  - Verifies cross-clock domain data transfer  
  - Tests reset synchronization  
  - Validates credit handling and ordering  

* Binary to Gray Encoder (enc_bin2gray)  
  - Verifies correct Gray code generation  
  - Ensures single-bit transitions  

* Binary to One-Hot Encoder (enc_bin2onehot)  
  - Verifies only one output bit is high  
  - Checks correct position mapping  

* ECC Encoder (ecc_sed_encoder)  
  - Verifies parity bit generation  
  - Ensures correct error detection encoding  

Each testbench:

* Computes expected outputs internally  
* Compares against DUT outputs  
* Reports mismatches using $display  
* Prints "TESTS PASSED" on success  

---

## Results (Visible Problems)
```
The agent reduces 31 candidates to exactly one correct implementation per module:

cdc_fifo_flops_push_credit → mutant_19.v  
counter → mutant_11.v  
credit_receiver → mutant_18.v  
ecc_sed_encoder → mutant_18.v  
enc_bin2gray → mutant_25.v  
enc_bin2onehot → mutant_27.v  
fifo_flops → mutant_23.v  
lfsr → mutant_29.v  
shift_left → mutant_1.v  
shift_right → mutant_9.v  

Each module should report:

Number of positive guesses: 1
```
---

## Outputs

The pipeline prints:

* Module name  
* Number of passing mutants  
* Passing mutant filename  

Example:

Evaluating module: counter  
Number of positive guesses: 1  
Passing mutants:  
  mutant_11.v  

---

## Notes

* The evaluation shown is a dry run (no answers folder provided)  
* Precision may appear as 0.00 — this is expected  
* Final scoring during grading uses hidden testcases  
* The agent is designed to generalize to unseen modules  

---

## Reproducibility

The grader can reproduce results using:

git clone <repo>  
cd <repo>  
python run_all.py visible_problems  

No manual steps are required. The pipeline is fully automated.

---

## Submission Details

* Single command execution (run_all.py)  
* Fully automated pipeline  
* No hardcoded paths  
* Uses sys.executable for portability  
* Compatible with grading environment  
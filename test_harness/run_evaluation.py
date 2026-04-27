r"""Script to evaluate testbenches quality."""

from collections.abc import Sequence
import os
import pathlib
import subprocess
import tempfile
import math

from absl import app
from absl import flags

import constants


_PROBLEMS_FOLDER = flags.DEFINE_string(
    "problems_folder",
    None,
    "The path to the problems folder.",
    required=True,
)
_ANSWERS_FOLDER = flags.DEFINE_string(
    "answers_folder",
    None,
    "The path to the answers folder.",
)
_INCLUDE_PATHS = flags.DEFINE_list(
    "include_paths",
    None,
    "List of include paths to be used when compiling the testbench.",
)
_TIMEOUT_SECONDS = 10


def compute_problem_weight(mutant_file: pathlib.Path) -> float:
    if not mutant_file.exists():
        raise ValueError(f"Mutant file {mutant_file} does not exist.")
    content = mutant_file.read_text()
    num_lines = content.count("\n") + 1
    return math.sqrt(num_lines)


def compute_normalized_weighted_precision(
    module_to_precision: dict[str, float],
    module_to_weight: dict[str, float],
) -> float:
    total_weighted_precision = sum(
        module_to_precision[module] * module_to_weight[module]
        for module in module_to_precision
    )
    total_weight = sum(module_to_weight.values())
    if total_weight > 0:
        return total_weighted_precision / total_weight
    return 0.0


def get_answer_mutant_id(answers_folder: pathlib.Path, module_name: str) -> int:
    answer_file = answers_folder / module_name / constants.ANSWER_FILE_NAME
    if not answer_file.exists():
        raise ValueError(f"Answer file {answer_file} does not exist.")
    try:
        return int(answer_file.read_text().strip())
    except ValueError as e:
        raise ValueError(f"Invalid content in answer file {answer_file}: {e}")


def is_test_passing(
    tb_module_name: str, dependency_paths: list[str], include_folders: list[str] | None
) -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        compiled_file = os.path.join(temp_dir, "out")

        include_args = []
        if include_folders is not None:
            for include_folder in include_folders:
                include_args.append("-I")
                include_args.append(include_folder)

        iverilog_cmd = (
            [
                "iverilog",
                "-g2012",
                "-o",
                compiled_file,
                "-s",
                tb_module_name,
            ]
            + dependency_paths
            + include_args
        )

        try:
            subprocess.run(
                iverilog_cmd,
                check=True,
                timeout=_TIMEOUT_SECONDS,
                capture_output=True,
            )
        except subprocess.TimeoutExpired:
            print(f"Compilation timed out after {_TIMEOUT_SECONDS} seconds")
            return False
        except subprocess.CalledProcessError:
            return False

        vvp_cmd = ["vvp", compiled_file]

        try:
            vvp_out = subprocess.run(
                vvp_cmd,
                check=True,
                capture_output=True,
                timeout=_TIMEOUT_SECONDS,
            )

            stdout = vvp_out.stdout.decode()

            if constants.TEST_PASS_STRING in stdout:
                return True

        except subprocess.TimeoutExpired:
            print(f"Execution timed out after {_TIMEOUT_SECONDS} seconds")
        except subprocess.CalledProcessError:
            return False

        return False


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")

    problems_folder = pathlib.Path(_PROBLEMS_FOLDER.value)
    is_dry_run = _ANSWERS_FOLDER.value is None

    if is_dry_run:
        print("Running in dry run mode, the answer folder is not provided.")
        answers_folder = problems_folder
    else:
        answers_folder = pathlib.Path(_ANSWERS_FOLDER.value)

    if not problems_folder.is_dir():
        raise ValueError(
            f"Problems folder {problems_folder} does not exist or is not a directory."
        )

    if not answers_folder.is_dir():
        raise ValueError(
            f"Answers folder {answers_folder} does not exist or is not a directory."
        )

    module_names = [f.name for f in problems_folder.iterdir() if f.is_dir()]

    answer_subdirs = {f.name for f in answers_folder.iterdir() if f.is_dir()}
    missing = set(module_names) - answer_subdirs
    if missing:
        raise ValueError(f"Answers folder missing subdirectories: {missing}")

    module_to_precision = {}
    module_to_weight = {}

    for module in module_names:
        print(f"\nEvaluating module: {module}")

        problem_dir = problems_folder / module

        if is_dry_run:
            answer_mutant_id = 0
        else:
            answer_mutant_id = get_answer_mutant_id(answers_folder, module)

        sorted_mutant_files = list(sorted(problem_dir.glob("mutant_*.v")))

        if not sorted_mutant_files:
            print(f"No mutant files found in {problem_dir}, assigning 0 score.")
            module_to_precision[module] = 0
            module_to_weight[module] = 0
            continue

        weight = compute_problem_weight(sorted_mutant_files[0])
        module_to_weight[module] = weight
        print(f"Weight for module {module}: {weight:.0f}")

        tb_file = problem_dir / constants.TESTBENCH_FILE_NAME
        if not tb_file.exists():
            print(f"No tb.v found in {problem_dir}, assigning 0 score.")
            module_to_precision[module] = 0
            continue

        guesses = []
        passing_mutants = []

        for mutant_file in sorted_mutant_files:
            dependencies = [str(tb_file), str(mutant_file)]

            passed = is_test_passing(
                constants.TESTBENCH_MODULE_NAME,
                dependencies,
                _INCLUDE_PATHS.value,
            )

            guesses.append(1 if passed else 0)

            if passed:
                passing_mutants.append(mutant_file.name)

        num_positive_guesses = sum(guesses)

        print(f"Number of positive guesses: {num_positive_guesses}")

        print(f"Passing mutants for module {module}:")
        if passing_mutants:
            for mutant in passing_mutants:
                print(f"  {mutant}")
        else:
            print("  None")

        found_correct = guesses[answer_mutant_id] == 1

        if found_correct and num_positive_guesses > 0:
            precision = 1 / num_positive_guesses
        else:
            precision = 0

        module_to_precision[module] = precision

        print(f"Precision for module {module}: {precision:.2f}")

    print("\nFinal precisions per module:")
    for module, precision in module_to_precision.items():
        print(f"{module}: {precision:.2f}")

    normalized_weighted_precision = compute_normalized_weighted_precision(
        module_to_precision, module_to_weight
    )

    print(f"Normalized weighted precision: {normalized_weighted_precision:.2f}")

    if is_dry_run:
        print(
            "This was a dry run, precision values are not correct as the answers folder was not provided."
        )


if __name__ == "__main__":
    app.run(main)